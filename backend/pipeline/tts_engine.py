"""
tts_engine.py — Multi-voice TTS engine.

audioop shim is handled by audioop_shim.py — import it first.
Primary:  ElevenLabs (premium natural voices).
Fallback: gTTS (free, multiple accents/regions).
"""
import os
import sys

# Load shim before any audio library
try:
    import pipeline.audioop_shim  # noqa: F401
except ImportError:
    try:
        import audioop_shim  # noqa: F401
    except ImportError:
        pass

from gtts import gTTS
from pydub import AudioSegment

from config import VOICE_PRESETS

import logging
log = logging.getLogger(__name__)


def _gtts_voice(text: str, preset: str, out_path: str) -> float:
    cfg = VOICE_PRESETS.get(preset, VOICE_PRESETS["warm_female"])
    tts = gTTS(text=text, lang=cfg["lang"], tld=cfg.get("tld", "com"), slow=cfg.get("slow", False))
    tts.save(out_path)
    audio  = AudioSegment.from_mp3(out_path)
    padded = audio + AudioSegment.silent(duration=350)
    padded.export(out_path, format="mp3")
    return len(padded) / 1000.0


def _elevenlabs_voice(text: str, voice_id: str, api_key: str, out_path: str) -> float:
    import requests
    url     = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
    body    = {
        "text": text,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.85},
    }
    r = requests.post(url, json=body, headers=headers, timeout=30)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(r.content)
    audio = AudioSegment.from_mp3(out_path)
    return len(audio) / 1000.0


def generate_voiceovers(
    segments: list,
    output_dir: str,
    voice_preset: str = "warm_female",
    elevenlabs_key: str = "",
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM",
) -> list:
    os.makedirs(output_dir, exist_ok=True)
    updated      = []
    current_time = 0.0

    for i, seg in enumerate(segments):
        seg        = dict(seg)
        text       = (seg.get("voiceover_text") or "").strip()
        audio_path = os.path.join(output_dir, f"vo_{i:03d}.mp3")

        if text:
            try:
                if elevenlabs_key:
                    dur = _elevenlabs_voice(text, elevenlabs_voice_id, elevenlabs_key, audio_path)
                    log.info(f"  [ElevenLabs] seg {i}: {dur:.1f}s")
                else:
                    dur = _gtts_voice(text, voice_preset, audio_path)
                    log.info(f"  [gTTS] seg {i}: {dur:.1f}s")
            except Exception as e:
                log.warning(f"  TTS failed seg {i}: {e}")
                audio_path = None
                dur        = float(seg.get("estimated_duration_seconds", 4))
        else:
            audio_path = None
            dur        = float(seg.get("estimated_duration_seconds", 4))

        seg["audio_file_path"]         = audio_path
        seg["actual_duration_seconds"] = max(dur, float(seg.get("estimated_duration_seconds", 3)))
        seg["start_time"]              = current_time
        current_time                  += seg["actual_duration_seconds"]
        updated.append(seg)

    return updated
