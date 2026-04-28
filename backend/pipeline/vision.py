"""
vision.py — Parallel Gemini Vision analysis of every uploaded media file.
Analyzes 5 files simultaneously for fast processing of large libraries.
"""
import os
import base64
import mimetypes
import logging
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from google import genai
from google.genai import types

log = logging.getLogger(__name__)


def _encode_file(path: str) -> tuple[str, str]:
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        ext = os.path.splitext(path)[1].lower()
        mime = "video/mp4" if ext in {".mp4", ".mov", ".avi"} else "image/jpeg"
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode(), mime


def analyze_media(file_paths: list[str], api_key: str, model: str) -> list[dict]:
    client = genai.Client(api_key=api_key)
    results = []

    def analyze_one(path):
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
  "actions":     ["list", "of", "key", "actions"],
  "best_for":    "hook | middle | payoff | outro | any",
  "quality":     "high | medium | low",
  "duration_estimate": {{"seconds": 0}}
}}
"""
            last_err = None
            for attempt in range(5):
                try:
                    response = client.models.generate_content(
                        model=model,
                        contents=[
                            types.Part.from_bytes(data=base64.b64decode(data), mime_type=mime),
                            types.Part.from_text(text=prompt),
                        ],
                    )
                    break
                except Exception as e:
                    last_err = e
                    wait = 10 * (attempt + 1)
                    log.warning(f"  Vision retry {attempt+1}: {e} — waiting {wait}s")
                    time.sleep(wait)
            else:
                raise last_err

            text = response.text.strip()
            text = re.sub(r"```json|```", "", text).strip()
            info = json.loads(text)
            info["path"]     = path
            info["filename"] = fname
            info["type"]     = ftype
            log.info(f"  Analyzed: {fname} — {info.get('mood')} {info.get('pet_type')}")
            return info

        except Exception as e:
            log.warning(f"  Vision failed for {os.path.basename(path)}: {e}")
            return {
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
            }

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(analyze_one, path): path for path in file_paths}
        for future in as_completed(futures):
            results.append(future.result())
            log.info(f"  Progress: {len(results)}/{len(file_paths)} analyzed")

    return results
