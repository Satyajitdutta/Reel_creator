"""
PetReel Studio — Central Configuration
All tuneable parameters in one place.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── AI Models ─────────────────────────────────────────────────────────────────
GEMINI_API_KEY   = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL     = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_PRO_MODEL = os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro")
IMAGEN_MODEL     = os.getenv("IMAGEN_MODEL", "imagen-3.0-generate-001")
ELEVENLABS_KEY   = os.getenv("ELEVENLABS_API_KEY", "")   # optional premium TTS

# ── Storage ───────────────────────────────────────────────────────────────────
STORAGE_ROOT = os.getenv("STORAGE_ROOT", "/data")        # Railway volume
MEDIA_DIR    = os.path.join(STORAGE_ROOT, "media")
OUTPUT_DIR   = os.path.join(STORAGE_ROOT, "output")
ASSETS_DIR   = os.path.join(STORAGE_ROOT, "assets")      # generated title cards
MUSIC_DIR    = os.path.join(STORAGE_ROOT, "music")
TEMP_DIR     = os.path.join(STORAGE_ROOT, "temp")

# ── Video Quality ─────────────────────────────────────────────────────────────
RESOLUTION_SHORTS  = (1080, 1920)   # 9:16 — YouTube Shorts / Reels
RESOLUTION_YOUTUBE = (1920, 1080)   # 16:9 — YouTube landscape
RESOLUTION_SQUARE  = (1080, 1080)   # 1:1  — Instagram square
FPS                = 30
VIDEO_BITRATE      = "5000k"
CRF                = 18             # 0–51, lower = better quality
CROSSFADE_DUR      = 0.5
ZOOM_FACTOR        = 1.07
BG_MUSIC_VOL       = 0.10
SUBTITLE_FONT_SIZE = 52
LOWER_THIRD_DUR    = 3.0            # seconds to show name plate
OUTRO_DUR          = 5.0            # seconds for outro card

# ── YouTube ───────────────────────────────────────────────────────────────────
YT_CATEGORY_PETS   = "15"
YT_DEFAULT_PRIVACY = "unlisted"
YT_SECRETS_PATH    = os.getenv("YT_SECRETS_PATH", "client_secrets.json")
YT_TOKEN_PATH      = os.getenv("YT_TOKEN_PATH", "yt_token.pickle")

# ── Style Presets — the Canva-equivalent design system ────────────────────────
STYLE_PRESETS = {
    "cinematic": {
        "label": "Cinematic",
        "icon": "🎬",
        "bg_gradient": [("#0D0D12", "#1A1A2E"), ("#16213E", "#0F3460")],
        "primary":     "#C9A84C",   # gold
        "secondary":   "#FFFFFF",
        "text_shadow": "#000000",
        "font_display": "HelveticaNeue-Bold",
        "font_body":    "HelveticaNeue",
        "overlay_alpha": 0.72,
        "color_grade":  "teal_orange",
        "transition":   "fade",
        "vignette":     True,
        "film_grain":   True,
        "subtitle_bg":  "#000000CC",
    },
    "energetic": {
        "label": "Energetic",
        "icon": "⚡",
        "bg_gradient": [("#FF4500", "#FF6B35"), ("#F7931E", "#FFD700")],
        "primary":     "#FFD700",
        "secondary":   "#FFFFFF",
        "text_shadow": "#8B0000",
        "font_display": "Arial-Black",
        "font_body":    "Arial-Bold",
        "overlay_alpha": 0.55,
        "color_grade":  "warm_vibrant",
        "transition":   "zoom_punch",
        "vignette":     False,
        "film_grain":   False,
        "subtitle_bg":  "#FF450099",
    },
    "warm_cozy": {
        "label": "Warm & Cozy",
        "icon": "🌅",
        "bg_gradient": [("#FFF3E0", "#FFE0B2"), ("#FFCC80", "#FFB74D")],
        "primary":     "#E65100",
        "secondary":   "#4E342E",
        "text_shadow": "#FF8F00",
        "font_display": "Georgia-Bold",
        "font_body":    "Georgia",
        "overlay_alpha": 0.65,
        "color_grade":  "warm_soft",
        "transition":   "crossfade",
        "vignette":     True,
        "film_grain":   False,
        "subtitle_bg":  "#E6510099",
    },
    "minimal": {
        "label": "Minimal",
        "icon": "◻",
        "bg_gradient": [("#FAFAFA", "#F0F0F0"), ("#E8E8E8", "#DCDCDC")],
        "primary":     "#111111",
        "secondary":   "#555555",
        "text_shadow": "#CCCCCC",
        "font_display": "Helvetica-Light",
        "font_body":    "Helvetica",
        "overlay_alpha": 0.80,
        "color_grade":  "neutral",
        "transition":   "slide",
        "vignette":     False,
        "film_grain":   False,
        "subtitle_bg":  "#00000099",
    },
    "dramatic": {
        "label": "Dramatic",
        "icon": "🎭",
        "bg_gradient": [("#0A0A0A", "#1C0A00"), ("#3D0000", "#0A0A0A")],
        "primary":     "#FF1744",
        "secondary":   "#FFFFFF",
        "text_shadow": "#000000",
        "font_display": "Arial-Black",
        "font_body":    "Arial-Bold",
        "overlay_alpha": 0.78,
        "color_grade":  "high_contrast",
        "transition":   "wipe",
        "vignette":     True,
        "film_grain":   True,
        "subtitle_bg":  "#FF174499",
    },
    "playful": {
        "label": "Playful",
        "icon": "🐾",
        "bg_gradient": [("#E040FB", "#7C4DFF"), ("#40C4FF", "#18FFFF")],
        "primary":     "#FFFFFF",
        "secondary":   "#FFD740",
        "text_shadow": "#7C4DFF",
        "font_display": "Arial-Rounded-MT-Bold",
        "font_body":    "Arial",
        "overlay_alpha": 0.50,
        "color_grade":  "vibrant",
        "transition":   "bounce",
        "vignette":     False,
        "film_grain":   False,
        "subtitle_bg":  "#7C4DFF99",
    },
}

# ── Script Formulas — the InVideo-equivalent viral templates ──────────────────
SCRIPT_FORMULAS = {
    "hook_loop_payoff": {
        "label": "Hook → Loop → Payoff",
        "description": "Start with the best moment, rewind, build tension, deliver.",
        "icon": "🪝",
        "prompt_template": """
Write a viral pet video script using the HOOK → LOOP → PAYOFF formula.
Structure:
1. HOOK (0–3s): Open with the single most shocking / funny / adorable moment.
   Use a cliffhanger — "You won't believe what happened next…"
2. CONTEXT: "But let me take you back to the beginning…" Set the scene.
3. BUILD: Add energy, anticipation, micro-revelations.
4. LOOP BACK: Return to the hook moment with full context.
5. PAYOFF: Satisfying resolution + CTA ("Follow for daily cuteness!").
""",
    },
    "pas": {
        "label": "Problem → Agitation → Solution",
        "description": "Relatable problem, amplify it, pet content as the answer.",
        "icon": "💡",
        "prompt_template": """
Write a viral pet video script using the PAS formula.
Structure:
1. PROBLEM (0–3s): Name a specific, relatable pet parent struggle.
2. AGITATION: Make the problem feel urgent, funny, or emotionally resonant.
3. SOLUTION: Show how THIS pet / moment solves, heals, or entertains.
4. CTA: Invite follow for more.
""",
    },
    "storytime": {
        "label": "Story Arc",
        "description": "Classic beginning → middle → end narrative.",
        "icon": "📖",
        "prompt_template": """
Write a viral pet video script using a classic story arc.
Structure:
1. SETUP: Introduce the pet and context in one punchy sentence.
2. RISING ACTION: What happened? Build tension or delight step by step.
3. CLIMAX: The peak funny / cute / emotional moment.
4. RESOLUTION: How it ended. Leave the viewer smiling.
5. CTA: "Like & follow for more [pet name] adventures!"
""",
    },
    "reaction": {
        "label": "Reaction / Commentary",
        "description": "Live commentary over clips like a sports commentator.",
        "icon": "🎙️",
        "prompt_template": """
Write a viral pet video script in the style of excited live sports commentary.
Structure:
1. INTRO: Brief excited setup ("Oh my goodness, you have GOT to see this…")
2. PLAY-BY-PLAY: Describe each action as it unfolds, with energy and humour.
3. COLOUR COMMENTARY: Add funny observations or relatable pet-parent thoughts.
4. HIGHLIGHT CALL: The single best line that captures the magic moment.
5. OUTRO + CTA.
""",
    },
    "day_in_life": {
        "label": "Day in the Life",
        "description": "Chronological morning-to-night slice of your pet's world.",
        "icon": "🌅",
        "prompt_template": """
Write a viral pet video script structured as a "Day in the Life" of a pet.
Structure:
1. MORNING: Wake-up routine, first meal, first zoomies.
2. MIDDAY: The signature nap, the window patrol, the mischief.
3. AFTERNOON: Play session, the chaos moment.
4. EVENING: The cuddle-down, the final check-in.
5. CTA: "Come back tomorrow for more [pet] content!"
""",
    },
}

# ── Voice Presets ─────────────────────────────────────────────────────────────
VOICE_PRESETS = {
    "warm_female":  {"lang": "en", "tld": "com", "slow": False},
    "deep_male":    {"lang": "en", "tld": "co.uk", "slow": False},
    "excited":      {"lang": "en", "tld": "com.au", "slow": False},
    "calm_narrator":{"lang": "en", "tld": "ca", "slow": True},
    "playful":      {"lang": "en", "tld": "co.in", "slow": False},
}
