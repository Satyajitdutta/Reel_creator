"""
main.py — PetReel Studio · Railway Backend
FastAPI server that orchestrates the complete Canva+InVideo pipeline.
"""
import os
import uuid
import asyncio
import logging
import shutil
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

import config
from pipeline import vision, planner, designer, tts_engine, video_engine, uploader

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ── Ensure directories ────────────────────────────────────────────────────────
for d in [config.MEDIA_DIR, config.OUTPUT_DIR, config.ASSETS_DIR,
          config.MUSIC_DIR, config.TEMP_DIR]:
    os.makedirs(d, exist_ok=True)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="PetReel Studio API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static file serving ───────────────────────────────────────────────────────
app.mount("/media",  StaticFiles(directory=config.MEDIA_DIR),  name="media")
app.mount("/output", StaticFiles(directory=config.OUTPUT_DIR), name="output")
app.mount("/music",  StaticFiles(directory=config.MUSIC_DIR),  name="music")

# ── In-memory job store ───────────────────────────────────────────────────────
# In production, use Redis. For Railway single-instance, in-memory is fine.
jobs: dict[str, dict] = {}


def _job_log(job_id: str, msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"{ts} [{level}] {msg}"
    jobs[job_id]["logs"].append(line)
    log.info(f"[{job_id[:8]}] {msg}")


def _job_step(job_id: str, step: int, label: str):
    jobs[job_id]["step"]  = step
    jobs[job_id]["label"] = label
    _job_log(job_id, f"[{step}/7] {label}")


# ── Upload endpoints ──────────────────────────────────────────────────────────
@app.post("/api/upload/media")
async def upload_media(files: list[UploadFile] = File(...)):
    saved = []
    for f in files:
        dest = os.path.join(config.MEDIA_DIR, f.filename)
        with open(dest, "wb") as out:
            shutil.copyfileobj(f.file, out)
        saved.append(f.filename)
    return {"uploaded": saved}


@app.post("/api/upload/music")
async def upload_music(file: UploadFile = File(...)):
    dest = os.path.join(config.MUSIC_DIR, file.filename)
    with open(dest, "wb") as out:
        shutil.copyfileobj(file.file, out)
    return {"uploaded": file.filename}


@app.post("/api/upload/logo")
async def upload_logo(file: UploadFile = File(...)):
    dest = os.path.join(config.ASSETS_DIR, "brand_logo" + Path(file.filename).suffix)
    with open(dest, "wb") as out:
        shutil.copyfileobj(file.file, out)
    return {"path": dest, "url": f"/assets/{os.path.basename(dest)}"}


# ── List files ────────────────────────────────────────────────────────────────
@app.get("/api/media")
def list_media():
    files = [f for f in os.listdir(config.MEDIA_DIR) if not f.startswith(".")]
    return files

@app.get("/api/music")
def list_music():
    files = [f for f in os.listdir(config.MUSIC_DIR) if not f.startswith(".")]
    return files

@app.get("/api/output")
def list_output():
    files = [f for f in os.listdir(config.OUTPUT_DIR) if not f.startswith(".")]
    return sorted(files, reverse=True)

@app.delete("/api/media/{filename}")
def delete_media(filename: str):
    p = os.path.join(config.MEDIA_DIR, filename)
    if os.path.exists(p):
        os.remove(p)
        return {"deleted": filename}
    raise HTTPException(404, "File not found")


# ── Analyze media (Vision AI) ─────────────────────────────────────────────────
@app.post("/api/analyze")
async def analyze_media(body: dict):
    """
    InVideo AI: Analyze uploaded files with Gemini Vision before scripting.
    Returns rich descriptions that power smarter script generation.
    """
    api_key = body.get("api_key") or config.GEMINI_API_KEY
    if not api_key:
        raise HTTPException(400, "GEMINI_API_KEY required")

    filenames = body.get("filenames", [])
    paths = [os.path.join(config.MEDIA_DIR, f) for f in filenames if
             os.path.exists(os.path.join(config.MEDIA_DIR, f))]

    if not paths:
        return []

    results = vision.analyze_media(paths, api_key, config.GEMINI_MODEL)
    return results


# ── Generate pipeline ─────────────────────────────────────────────────────────
@app.post("/api/generate")
async def start_generation(body: dict, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "id":     job_id,
        "status": "queued",
        "step":   0,
        "label":  "Queued",
        "logs":   ["Job created"],
        "outputs": {},
        "plan":   None,
        "error":  None,
        "created_at": datetime.now().isoformat(),
    }
    background_tasks.add_task(_run_pipeline, job_id, body)
    return {"job_id": job_id}


async def _run_pipeline(job_id: str, body: dict):
    jobs[job_id]["status"] = "running"
    try:
        await asyncio.to_thread(_pipeline_sync, job_id, body)
    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"]  = str(e)
        _job_log(job_id, f"Pipeline failed: {e}", "ERROR")
        log.exception(e)


def _pipeline_sync(job_id: str, body: dict):
    """Synchronous pipeline — runs in thread pool."""

    api_key      = body.get("api_key")      or config.GEMINI_API_KEY
    el_key       = body.get("elevenlabs_key") or config.ELEVENLABS_KEY
    topic        = body.get("topic",        "My pet's best moments")
    formula      = body.get("formula",      "hook_loop_payoff")
    style_name   = body.get("style",        "cinematic")
    voice_preset = body.get("voice_preset", "warm_female")
    music_file   = body.get("music_file",   "")
    refinement   = body.get("refinement",   "")
    media_list   = body.get("media_list",   [])
    no_upload    = body.get("no_upload",    True)
    export_formats = body.get("export_formats", ["shorts"])
    brand        = body.get("brand", {})
    el_voice_id  = body.get("elevenlabs_voice_id", "21m00Tcm4TlvDq8ikWAM")
    media_analysis_input = body.get("media_analysis", [])

    if not api_key:
        raise ValueError("GEMINI_API_KEY not provided")

    style_cfg = config.STYLE_PRESETS.get(style_name, config.STYLE_PRESETS["cinematic"])
    style_cfg["label"] = style_name
    job_dir   = os.path.join(config.TEMP_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    # ── Step 1: Gather media ──────────────────────────────────────────────────
    _job_step(job_id, 1, "Gathering media assets")
    if media_list:
        media_paths = [os.path.join(config.MEDIA_DIR, f) for f in media_list
                       if os.path.exists(os.path.join(config.MEDIA_DIR, f))]
    else:
        import media_manager
        media_paths, _ = media_manager.get_fresh_media(config.MEDIA_DIR, num_clips=10)
    _job_log(job_id, f"  {len(media_paths)} asset(s) selected")

    # ── Step 2: Vision analysis ───────────────────────────────────────────────
    _job_step(job_id, 2, "Analyzing media with Gemini Vision (InVideo AI)")
    if media_analysis_input:
        # Frontend already ran analysis — reuse results
        media_analysis = media_analysis_input
        _job_log(job_id, f"  Using pre-computed vision analysis ({len(media_analysis)} items)")
    elif media_paths:
        media_analysis = vision.analyze_media(media_paths, api_key, config.GEMINI_MODEL)
    else:
        media_analysis = []

    # ── Step 3: AI script planning ────────────────────────────────────────────
    _job_step(job_id, 3, "Generating viral script with Gemini (InVideo formula)")
    plan = planner.generate_plan(
        topic=topic,
        media_analysis=media_analysis,
        formula=formula,
        style=style_name,
        brand=brand,
        api_key=api_key,
        model=config.GEMINI_MODEL,
        refinement=refinement,
    )
    jobs[job_id]["plan"] = plan
    _job_log(job_id, f"  Title: {plan.get('title')}")
    _job_log(job_id, f"  Segments: {len(plan.get('script_segments', []))}")

    # Build media paths map (filename → absolute path)
    media_map = {os.path.basename(p): p for p in media_paths}

    # ── Step 3b: Generate AI scenes for missing media ─────────────────────────
    for i, seg in enumerate(plan.get("script_segments", [])):
        if seg.get("media_ref") == "AI_GENERATE":
            ai_prompt = seg.get("ai_image_prompt", topic)
            ai_path   = os.path.join(job_dir, f"ai_scene_{i:03d}.jpg")
            _job_log(job_id, f"  Generating AI scene {i}: {ai_prompt[:60]}")
            result = designer.generate_ai_scene(ai_prompt, style_cfg, api_key, ai_path, config.RESOLUTION_SHORTS)
            if result:
                key = f"AI_GENERATE_{seg.get('segment_id', i)}"
                media_map[key]    = result
                seg["media_ref"]  = key
                seg["type"]       = "image"

    # ── Step 4: Canva-style branded assets ────────────────────────────────────
    _job_step(job_id, 4, "Designing branded assets (Canva Magic Design)")

    # Title card
    title_card_path = os.path.join(job_dir, "title_card.jpg")
    try:
        designer.generate_title_card(
            title=plan.get("title", topic),
            subtitle=brand.get("channel_name", "PetReels Studio"),
            style_cfg=style_cfg,
            brand=brand,
            resolution=config.RESOLUTION_SHORTS,
            out_path=title_card_path,
        )
        _job_log(job_id, "  Title card generated")
    except Exception as e:
        _job_log(job_id, f"  Title card skipped: {e}", "WARN")
        title_card_path = None

    # Outro card
    outro_card_path = os.path.join(job_dir, "outro_card.jpg")
    try:
        designer.generate_outro_card(
            channel_name=brand.get("channel_name", "PetReels"),
            cta=brand.get("cta", "Follow for daily cuteness!"),
            style_cfg=style_cfg,
            brand=brand,
            resolution=config.RESOLUTION_SHORTS,
            out_path=outro_card_path,
        )
        _job_log(job_id, "  Outro card generated")
    except Exception as e:
        _job_log(job_id, f"  Outro card skipped: {e}", "WARN")
        outro_card_path = None

    # ── Step 5: TTS voiceovers ────────────────────────────────────────────────
    _job_step(job_id, 5, "Generating voiceovers (ElevenLabs / gTTS)")
    segments = tts_engine.generate_voiceovers(
        plan["script_segments"], job_dir, voice_preset, el_key, el_voice_id
    )
    total_dur = sum(s["actual_duration_seconds"] for s in segments)
    _job_log(job_id, f"  Total duration: {total_dur:.1f}s")

    # ── Step 6: Video assembly ────────────────────────────────────────────────
    _job_step(job_id, 6, "Assembling video (Ken Burns + transitions + subtitles)")
    bg_music_path = os.path.join(config.MUSIC_DIR, music_file) if music_file else None
    output_video  = os.path.join(config.OUTPUT_DIR, f"reel_{job_id[:8]}.mp4")
    thumbnail_raw = os.path.join(job_dir, "thumb_raw.jpg")

    video_engine.create_reel(
        script_segments=segments,
        media_paths_map=media_map,
        title_card_path=title_card_path,
        outro_card_path=outro_card_path,
        bg_music_path=bg_music_path,
        output_path=output_video,
        thumbnail_path=thumbnail_raw,
        resolution=config.RESOLUTION_SHORTS,
        fps=config.FPS,
        style_cfg=style_cfg,
        crossfade=config.CROSSFADE_DUR,
        zoom_factor=config.ZOOM_FACTOR,
        bg_music_volume=config.BG_MUSIC_VOL,
    )

    # Branded thumbnail (Canva thumbnail maker)
    thumbnail_final = os.path.join(config.OUTPUT_DIR, f"thumb_{job_id[:8]}.jpg")
    try:
        designer.generate_thumbnail(
            title=plan.get("title", topic),
            style_cfg=style_cfg,
            brand=brand,
            base_frame_path=thumbnail_raw if os.path.exists(thumbnail_raw) else None,
            out_path=thumbnail_final,
            resolution=(1280, 720),
        )
    except Exception as e:
        _job_log(job_id, f"  Thumbnail generation warning: {e}", "WARN")
        thumbnail_final = thumbnail_raw

    # Multi-format export (Canva Smart Resize)
    if "instagram" in export_formats or "all" in export_formats:
        _job_log(job_id, "  Exporting multi-format versions (Canva Smart Resize)")
        fmt_outputs = video_engine.export_all_formats(output_video, config.OUTPUT_DIR)
    else:
        fmt_outputs = {"shorts": output_video}

    outputs = {
        "video":     os.path.basename(output_video),
        "thumbnail": os.path.basename(thumbnail_final),
        **{k: os.path.basename(v) for k, v in fmt_outputs.items()},
    }
    jobs[job_id]["outputs"] = outputs

    # ── Step 7: YouTube upload ────────────────────────────────────────────────
    if not no_upload:
        _job_step(job_id, 7, "Uploading to YouTube")
        try:
            video_id = uploader.upload_video(
                video_path=output_video,
                title=plan.get("title", topic),
                description=plan.get("description", ""),
                tags=plan.get("tags", []),
                category_id=config.YT_CATEGORY_PETS,
                privacy_status=body.get("yt_privacy", config.YT_DEFAULT_PRIVACY),
                thumbnail_path=thumbnail_final,
                secrets_path=config.YT_SECRETS_PATH,
                token_path=config.YT_TOKEN_PATH,
            )
            jobs[job_id]["youtube_id"] = video_id
            jobs[job_id]["youtube_url"] = f"https://youtube.com/shorts/{video_id}"
            _job_log(job_id, f"  YouTube: https://youtube.com/shorts/{video_id}")
        except Exception as e:
            _job_log(job_id, f"  YouTube upload failed: {e}", "WARN")
    else:
        _job_log(job_id, "  YouTube upload skipped (local only mode)")

    # Done
    jobs[job_id]["status"] = "done"
    _job_log(job_id, "✅ Pipeline complete!")


# ── Job status ────────────────────────────────────────────────────────────────
@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    return jobs[job_id]

@app.get("/api/jobs")
def list_jobs():
    return list(reversed(list(jobs.values())))


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0.0", "model": config.GEMINI_MODEL}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
