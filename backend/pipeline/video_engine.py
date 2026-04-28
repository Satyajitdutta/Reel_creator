"""
video_engine.py — Professional video assembly engine.
Ken Burns · Crossfade · Subtitles · Music ducking · Multi-format export.
"""
import os
import subprocess
import logging
from typing import Optional

import numpy as np
from PIL import Image

log = logging.getLogger(__name__)

# ── MoviePy compat (supports v1 and v2) ────────────────────────────────────────
try:
    from moviepy.editor import (
        ImageClip, VideoFileClip, concatenate_videoclips,
        CompositeAudioClip, AudioFileClip, TextClip, CompositeVideoClip,
    )
    from moviepy.video.fx.all import loop as mpy_loop
    def _dur(c, d):          return c.set_duration(d)
    def _sub(c, s, e=None):  return c.subclip(s, e) if e else c.subclip(s)
    def _rsz(c, **kw):       return c.resize(**kw)
    def _pos(c, p, r=False): return c.set_position(p, relative=r)
    def _sta(c, s):          return c.set_start(s)
    def _aud(c, a):          return c.set_audio(a)
    def _vol(c, v):          return c.volumex(v)
    def _cfi(c, d):          return c.crossfadein(d)
except Exception:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    from moviepy.video.VideoClip import ImageClip, TextClip
    from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
    from moviepy.video.compositing.concatenate import concatenate_videoclips
    from moviepy.audio.AudioClip import AudioFileClip, CompositeAudioClip
    try:
        from moviepy.video.fx.loop import loop as mpy_loop
    except ImportError:
        mpy_loop = None
    def _dur(c, d):          return c.with_duration(d)
    def _sub(c, s, e=None):  return c.subclipped(s, e) if e else c.subclipped(s)
    def _rsz(c, **kw):       return c.resized(**kw)
    def _pos(c, p, r=False): return c.with_position(p, relative=r)
    def _sta(c, s):          return c.with_start(s)
    def _aud(c, a):          return c.with_audio(a)
    def _vol(c, v):          return c.multiply_volume(v)
    def _cfi(c, d):          return c


def _fit(clip, resolution):
    tw, th = resolution
    cw, ch = clip.size
    scale  = max(tw / cw, th / ch)
    clip   = _rsz(clip, width=int(cw * scale))
    try:
        from moviepy.video.fx.all import crop
        clip = crop(clip, x_center=clip.size[0]//2, y_center=clip.size[1]//2, width=tw, height=th)
    except Exception:
        clip = _rsz(clip, width=tw)
    return _pos(clip, "center")


def _ken_burns(clip, zoom: float = 1.07, direction: str = "in"):
    try:
        w, h = clip.size
        dur  = clip.duration

        def make_frame(t):
            progress = t / max(dur - 0.001, 0.001)
            scale    = (1.0 + (zoom - 1.0) * progress) if direction == "in" else (zoom - (zoom - 1.0) * progress)
            nw, nh   = int(w * scale), int(h * scale)
            pil      = Image.fromarray(clip.get_frame(t)).resize((nw, nh), Image.LANCZOS)
            arr      = np.array(pil)
            x0, y0   = (nw - w) // 2, (nh - h) // 2
            return arr[y0:y0 + h, x0:x0 + w]

        from moviepy.video.VideoClip import VideoClip
        kb     = VideoClip(make_frame, duration=dur)
        kb.fps = getattr(clip, "fps", 30) or 30
        return kb
    except Exception:
        return clip


def _subtitle(text, resolution, start_time, duration, style_cfg):
    w = resolution[0]
    try:
        txt = TextClip(text, fontsize=52, color="white", font="Arial-Bold",
                       stroke_color="black", stroke_width=2.5,
                       method="caption", size=(w - 100, None))
    except TypeError:
        txt = TextClip(text=text, font_size=52, color="white", font="Arial-Bold",
                       stroke_color="black", stroke_width=2.5,
                       method="caption", size=(w - 100, None))
    txt = _pos(txt, ("center", 0.74), r=True)
    txt = _sta(txt, start_time)
    return _dur(txt, duration)


def create_reel(
    script_segments, media_paths_map, title_card_path, outro_card_path,
    bg_music_path, output_path, thumbnail_path,
    resolution, fps, style_cfg,
    crossfade=0.5, zoom_factor=1.07, bg_music_volume=0.10,
):
    clips       = []
    audio_clips = []
    zoom_toggle = True

    # Intro title card
    if title_card_path and os.path.exists(title_card_path):
        tc = _fit(_dur(ImageClip(title_card_path), 3.0), resolution)
        try: tc = _cfi(tc, crossfade)
        except Exception: pass
        tc.fps = fps
        clips.append(tc)

    for seg in script_segments:
        media_ref = seg.get("media_ref", "")
        file_path = media_paths_map.get(media_ref) or media_paths_map.get(
            "AI_GENERATE_" + str(seg.get("segment_id", "")))
        duration  = float(seg.get("actual_duration_seconds", 4))

        if not file_path or not os.path.exists(file_path):
            log.warning(f"  Missing media: {media_ref!r}")
            continue

        ext = os.path.splitext(file_path)[1].lower()
        if ext in {".mp4", ".mov", ".avi", ".mkv", ".webm"}:
            clip = VideoFileClip(file_path, audio=False)
            safe_end = min(duration, clip.duration)
            clip = _sub(clip, 0, safe_end)
            if clip.duration < duration - 0.1 and mpy_loop:
                clip = mpy_loop(clip, duration=duration)
        else:
            clip = _dur(ImageClip(file_path), duration)
            clip = _fit(clip, resolution)
            clip = _ken_burns(clip, zoom_factor, "in" if zoom_toggle else "out")
            zoom_toggle = not zoom_toggle

        clip = _fit(clip, resolution)
        try: clip = _cfi(clip, crossfade)
        except Exception: pass
        clip.fps = fps
        clips.append(clip)

        ap = seg.get("audio_file_path")
        if ap and os.path.exists(ap):
            vo = _sta(AudioFileClip(ap), seg.get("start_time", 0) + (3.0 if title_card_path else 0))
            audio_clips.append(vo)

    # Outro
    if outro_card_path and os.path.exists(outro_card_path):
        oc = _fit(_dur(ImageClip(outro_card_path), 5.0), resolution)
        try: oc = _cfi(oc, crossfade)
        except Exception: pass
        oc.fps = fps
        clips.append(oc)

    if not clips:
        raise ValueError("No clips assembled — check media files.")

    final = concatenate_videoclips(clips, method="compose", padding=-crossfade)

    
    # Subtitles disabled (ImageMagick not available)

    # Background music
    if bg_music_path and os.path.exists(bg_music_path):
        bg = AudioFileClip(bg_music_path)
        if bg.duration < final.duration:
            if mpy_loop: bg = mpy_loop(bg, duration=final.duration)
        bg = _sub(bg, 0, final.duration)
        bg = _vol(bg, bg_music_volume)
        audio_clips.append(bg)

    if audio_clips:
        final = _aud(final, CompositeAudioClip(audio_clips))

    # Thumbnail
    try: final.save_frame(thumbnail_path, t=min(3.5, final.duration * 0.25))
    except Exception as e: log.warning(f"  Thumbnail extraction: {e}")

    log.info(f"  Encoding {final.duration:.1f}s → {output_path}")
    final.write_videofile(output_path, fps=fps, codec="libx264",
                          audio_codec="aac", preset="fast",
                          ffmpeg_params=["-crf", "28"], logger=None)

    for c in clips:
        try: c.close()
        except Exception: pass

    return output_path


def export_all_formats(source_mp4: str, output_dir: str) -> dict:
    outputs = {"original": source_mp4}
    for fmt, scale in [("instagram", "1080:1080")]:
        out = os.path.join(output_dir, f"final_{fmt}.mp4")
        cmd = ["ffmpeg", "-y", "-i", source_mp4,
               "-vf", f"scale={scale},setsar=1",
               "-c:v", "libx264", "-crf", "20", "-preset", "fast",
               "-c:a", "aac", "-b:a", "192k", out]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            outputs[fmt] = out
        except Exception as e:
            log.warning(f"  {fmt} export: {e}")
    return outputs
