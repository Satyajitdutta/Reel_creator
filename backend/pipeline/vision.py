"""
vision.py — Gemini Vision analysis of every uploaded media file.
This is how InVideo AI "understands" your content before scripting.
"""
import os
import base64
import mimetypes
import logging
from google import genai
from google.genai import types

log = logging.getLogger(__name__)


def _encode_file(path: str) -> tuple[str, str]:
    """Return (base64_data, mime_type) for any image or video file."""
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        ext = os.path.splitext(path)[1].lower()
        mime = "video/mp4" if ext in {".mp4", ".mov", ".avi"} else "image/jpeg"
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode(), mime


def analyze_media(file_paths: list[str], api_key: str, model: str) -> list[dict]:
    """
    Use Gemini Vision to describe each uploaded file.
    Returns a list of dicts: {path, filename, type, description, mood, actions, best_for}
    """
    client = genai.Client(api_key=api_key)
    results = []

    for path in file_paths:
        try:
            data, mime = _encode_file(path)
            fname = os.path.basename(path)
            ftype = "video" if mime.startswith("video") else "image"

            prompt = f"""
Analyze this pet {ftype} for a social media video editor.
Respond ONLY with JSON (no markdown):
{{
  "description": "one detailed sentence describing exactly what is happening",
  "pet_type":    "dog | cat | bird | rabbit | hamster | reptile | other",
  "pet_name_guess": "if a name is visible on a tag/collar, otherwise null",
  "mood":        "funny | cute | calm | energetic | dramatic | heartwarming",
  "actions":     ["list", "of", "key", "actions", "or", "expressions"],
  "best_for":    "hook | middle | payoff | outro | any",
  "quality":     "high | medium | low",
  "duration_estimate": {{"seconds": 0}} 
}}
For images, duration_estimate seconds = 0.
For videos, estimate viewing duration in seconds.
"""
            response = client.models.generate_content(
                model=model,
                contents=[
                    types.Part.from_bytes(data=base64.b64decode(data), mime_type=mime),
                    types.Part.from_text(text=prompt),
                ],
            )

            import json, re
            text = response.text.strip()
            # strip any accidental markdown fences
            text = re.sub(r"```json|```", "", text).strip()
            info = json.loads(text)
            info["path"]     = path
            info["filename"] = fname
            info["type"]     = ftype
            results.append(info)
            log.info(f"  Analyzed {fname}: {info.get('mood')} {info.get('pet_type')}")

        except Exception as e:
            log.warning(f"  Vision analysis failed for {os.path.basename(path)}: {e}")
            results.append({
                "path": path,
                "filename": os.path.basename(path),
                "type": "image" if not path.lower().endswith((".mp4", ".mov")) else "video",
                "description": "A pet media file",
                "pet_type": "unknown",
                "mood": "cute",
                "actions": [],
                "best_for": "any",
                "quality": "medium",
                "duration_estimate": {"seconds": 0},
            })

    return results
