"""
planner.py — AI script generation using InVideo-style viral formulas.
Powered by Gemini 2.5. Understands your media context from Vision analysis.
"""
import json
import re
import logging
from google import genai
from config import SCRIPT_FORMULAS

log = logging.getLogger(__name__)


def generate_plan(
    topic: str,
    media_analysis: list[dict],
    formula: str,
    style: str,
    brand: dict,
    api_key: str,
    model: str,
    refinement: str = "",
) -> dict:
    """
    Generate a complete reel plan (title, description, script_segments).
    Each segment is matched to the best available media from vision analysis.
    """
    client = genai.Client(api_key=api_key)

    formula_cfg = SCRIPT_FORMULAS.get(formula, SCRIPT_FORMULAS["hook_loop_payoff"])
    formula_prompt = formula_cfg["prompt_template"]

    # Build rich media context from vision analysis
    media_ctx_lines = []
    for i, m in enumerate(media_analysis):
        actions_str = ", ".join(m.get("actions", [])) or "none noted"
        media_ctx_lines.append(
            f"[{i}] {m['filename']} ({m['type']}) — "
            f"{m.get('description', '')} | mood: {m.get('mood')} | "
            f"actions: {actions_str} | best_for: {m.get('best_for')} | "
            f"quality: {m.get('quality')}"
        )
    media_context = "\n".join(media_ctx_lines) if media_ctx_lines else "No media uploaded — generate AI visuals."

    refine_part = f"\n\nExtra Instructions (apply these corrections): {refinement}" if refinement else ""

    brand_voice = brand.get("voice", "warm and energetic")
    channel_name = brand.get("channel_name", "PetReels")

    prompt = f"""
You are a world-class short-form video producer at a top social media studio.
Channel: {channel_name}
Brand voice: {brand_voice}
Video style: {style}
Topic: {topic}
{refine_part}

=== SCRIPT FORMULA ===
{formula_prompt}

=== AVAILABLE MEDIA (from AI Vision analysis) ===
{media_context}

=== YOUR TASK ===
1. Generate a complete YouTube Shorts / Instagram Reel plan.
2. For each script segment, choose the BEST matching media from the list above using its index number.
   If a segment needs a generated AI image (no good media available), set media_ref to "AI_GENERATE" and describe what to generate in ai_image_prompt.
3. Keep each voiceover under 18 words — punchy and conversational.
4. on_screen_text should be 1–5 words max — bold, impactful captions.
5. hook_options: give 3 alternative opening hooks (A/B test ideas).

Return ONLY raw JSON (no markdown):
{{
    "title": "SEO-optimised title (max 70 chars, include viral hook word)",
    "description": "YouTube description with storytelling + 5 hashtags",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
    "hook_options": ["Hook A", "Hook B", "Hook C"],
    "thumbnail_prompt": "Describe ideal YouTube thumbnail visual",
    "total_duration_estimate": 30,
    "script_segments": [
        {{
            "segment_id": 1,
            "role": "hook | context | build | climax | payoff | outro",
            "media_ref": "exact_filename.jpg OR AI_GENERATE",
            "media_index": 0,
            "ai_image_prompt": "describe image to generate if media_ref is AI_GENERATE, else null",
            "voiceover_text": "Short punchy narration under 18 words",
            "on_screen_text": "BOLD CAPTION (1-5 words)",
            "text_animation": "typewriter | fade | slide_up | pop | none",
            "estimated_duration_seconds": 4,
            "visual_note": "Any special effect or emphasis note for this clip"
        }}
    ]
}}
"""

    import time
    last_err = None
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config={"system_instruction": (
                    "You are a senior viral content strategist. "
                    "Output ONLY valid JSON. No prose, no markdown fences."
                )},
            )
            break
        except Exception as e:
            last_err = e
            wait = 10 * (attempt + 1)
            log.warning(f"  Gemini attempt {attempt+1} failed: {e} — retrying in {wait}s")
            time.sleep(wait)
    else:
        raise last_err

    text = response.text.strip()
    text = re.sub(r"```json|```", "", text).strip()

    try:
        plan = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini returned invalid JSON:\n{text[:600]}") from e

    log.info(f"  Plan generated: '{plan.get('title')}' | {len(plan.get('script_segments', []))} segments")
    return plan
