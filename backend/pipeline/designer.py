"""
designer.py — Canva Enterprise replica.

Generates:
  • Branded title / intro cards          (Magic Design equivalent)
  • Lower-thirds / name plates           (Canva text element)
  • Outro / subscribe cards              (Canva template)
  • YouTube thumbnails                   (Canva thumbnail maker)
  • AI scene images via Gemini Imagen    (Canva AI image generator)
  • Color-grading via FFmpeg             (Canva video filters)

All visuals respect the Brand Kit (colors, fonts, logo).
"""

import os
import base64
import logging
import subprocess
import textwrap
from io import BytesIO
from typing import Optional
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np

log = logging.getLogger(__name__)

# ── Font resolution ───────────────────────────────────────────────────────────
FONT_FALLBACKS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]

def _load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    for path in FONT_FALLBACKS:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _hex_to_rgb(hex_str: str) -> tuple:
    h = hex_str.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


# ── Gradient background ───────────────────────────────────────────────────────
def _gradient_background(size: tuple, color1: str, color2: str) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size)
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    c1 = np.array(_hex_to_rgb(color1), dtype=np.float64)
    c2 = np.array(_hex_to_rgb(color2), dtype=np.float64)
    for y in range(h):
        t = y / max(h - 1, 1)
        arr[y, :] = ((1 - t) * c1 + t * c2).astype(np.uint8)
    img = Image.fromarray(arr)
    return img


# ── Noise / grain overlay ─────────────────────────────────────────────────────
def _add_grain(img: Image.Image, amount: float = 0.03) -> Image.Image:
    arr = np.array(img).astype(np.float32)
    noise = np.random.normal(0, amount * 255, arr.shape)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


# ── Vignette ─────────────────────────────────────────────────────────────────
def _add_vignette(img: Image.Image, strength: float = 0.5) -> Image.Image:
    w, h = img.size
    mask = Image.new("L", (w, h), 255)
    draw = ImageDraw.Draw(mask)
    steps = 80
    for i in range(steps):
        t = i / steps
        alpha = int(255 * strength * t * t)
        mx, my = int(w * t / 2), int(h * t / 2)
        draw.rectangle([(mx, my), (w - mx, h - my)], outline=255 - alpha)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=w // 8))
    vig = Image.new("RGB", (w, h), (0, 0, 0))
    vig.paste(img, mask=mask)
    # blend
    result = Image.blend(vig, img, alpha=1 - strength * 0.6)
    return result


# ── Centered text with wrapping ───────────────────────────────────────────────
def _draw_centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    y_center: int,
    canvas_w: int,
    color: str,
    shadow_color: str = "#000000",
    max_width: int = None,
    line_spacing: int = 8,
):
    mw = max_width or int(canvas_w * 0.85)
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        bbox = font.getbbox(test)
        if bbox[2] - bbox[0] <= mw or not current:
            current = test
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)

    total_h = sum(font.getbbox(l)[3] - font.getbbox(l)[1] + line_spacing for l in lines)
    y = y_center - total_h // 2

    for line in lines:
        bbox = font.getbbox(line)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        x = (canvas_w - lw) // 2
        # shadow
        draw.text((x + 2, y + 2), line, font=font, fill=shadow_color)
        draw.text((x, y), line, font=font, fill=color)
        y += lh + line_spacing


# ── Title / Intro Card ────────────────────────────────────────────────────────
def generate_title_card(
    title: str,
    subtitle: str,
    style_cfg: dict,
    brand: dict,
    resolution: tuple = (1080, 1920),
    out_path: str = None,
) -> str:
    """Generate a branded title card image (like Canva Magic Design)."""
    w, h = resolution
    grads = style_cfg.get("bg_gradient", [("#0D0D12", "#1A1A2E")])
    bg = _gradient_background((w, h), grads[0][0], grads[0][1])

    # Logo overlay
    logo_path = brand.get("logo_path")
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            lw = int(w * 0.18)
            logo.thumbnail((lw, lw), Image.LANCZOS)
            lx = (w - logo.width) // 2
            ly = int(h * 0.12)
            bg.paste(logo, (lx, ly), logo if logo.mode == "RGBA" else None)
        except Exception as e:
            log.debug(f"Logo paste failed: {e}")

    # Semi-transparent panel behind text
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    panel_alpha = int(255 * style_cfg.get("overlay_alpha", 0.6))
    panel_color = _hex_to_rgb(style_cfg.get("bg_gradient", [("#000000",)])[0][0])
    panel_h = int(h * 0.45)
    panel_y = (h - panel_h) // 2
    od.rounded_rectangle(
        [(int(w * 0.06), panel_y), (int(w * 0.94), panel_y + panel_h)],
        radius=30, fill=(*panel_color, panel_alpha)
    )
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(bg)
    primary   = style_cfg.get("primary", "#FFFFFF")
    secondary = style_cfg.get("secondary", "#CCCCCC")
    shadow    = style_cfg.get("text_shadow", "#000000")

    title_font = _load_font(int(w * 0.072), bold=True)
    sub_font   = _load_font(int(w * 0.038))

    _draw_centered_text(draw, title,    title_font, h // 2 - int(h * 0.04), w, primary, shadow)
    _draw_centered_text(draw, subtitle, sub_font,   h // 2 + int(h * 0.10), w, secondary, shadow)

    # Accent line
    accent = _hex_to_rgb(primary)
    ax = int(w * 0.3)
    ay = h // 2 + int(h * 0.04)
    draw.line([(ax, ay), (w - ax, ay)], fill=accent, width=3)

    if style_cfg.get("film_grain"):
        bg = _add_grain(bg, 0.025)
    if style_cfg.get("vignette"):
        bg = _add_vignette(bg, 0.45)

    if not out_path:
        raise ValueError("out_path must be specified")
    bg.save(out_path, quality=95)
    log.info(f"  Title card → {out_path}")
    return out_path


# ── Lower-Third (name plate) ──────────────────────────────────────────────────
def generate_lower_third(
    text: str,
    style_cfg: dict,
    resolution: tuple = (1080, 1920),
    out_path: str = None,
) -> str:
    """Generate a transparent lower-third PNG overlay."""
    w, h = resolution
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    primary = style_cfg.get("primary", "#FFFFFF")
    bg_col  = (*_hex_to_rgb(style_cfg.get("bg_gradient", [("#000000",)])[0][0]), 200)

    font = _load_font(int(w * 0.042), bold=True)
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0] + 60
    th = bbox[3] - bbox[1] + 30

    bar_y = int(h * 0.78)
    draw.rounded_rectangle([(40, bar_y), (40 + tw, bar_y + th + 10)], radius=12, fill=bg_col)
    draw.text((70, bar_y + 12), text, font=font, fill=primary)

    img.save(out_path, format="PNG")
    return out_path


# ── Outro Card ────────────────────────────────────────────────────────────────
def generate_outro_card(
    channel_name: str,
    cta: str,
    style_cfg: dict,
    brand: dict,
    resolution: tuple = (1080, 1920),
    out_path: str = None,
) -> str:
    """Generate a subscribe/follow CTA outro card."""
    grads = style_cfg.get("bg_gradient", [("#0D0D12", "#1A1A2E")])
    bg = _gradient_background(resolution, grads[0][0], grads[0][1])
    w, h = resolution
    draw = ImageDraw.Draw(bg)

    primary  = style_cfg.get("primary", "#FFFFFF")
    secondary = style_cfg.get("secondary", "#CCCCCC")
    shadow   = style_cfg.get("text_shadow", "#000000")

    big_font  = _load_font(int(w * 0.080))
    med_font  = _load_font(int(w * 0.046))
    sub_font  = _load_font(int(w * 0.034))

    # Bell / subscribe icon (unicode)
    _draw_centered_text(draw, "🔔", big_font, int(h * 0.32), w, primary, shadow)
    _draw_centered_text(draw, "SUBSCRIBE", big_font, int(h * 0.44), w, primary, shadow)
    _draw_centered_text(draw, channel_name, med_font, int(h * 0.55), w, secondary, shadow)
    _draw_centered_text(draw, cta, sub_font, int(h * 0.65), w, secondary, shadow)

    # Paw print decoration
    paw_font = _load_font(int(w * 0.06))
    _draw_centered_text(draw, "🐾 🐾 🐾", paw_font, int(h * 0.75), w, primary, shadow)

    if style_cfg.get("vignette"):
        bg = _add_vignette(bg, 0.5)

    bg.save(out_path, quality=95)
    return out_path


# ── YouTube Thumbnail ─────────────────────────────────────────────────────────
def generate_thumbnail(
    title: str,
    style_cfg: dict,
    brand: dict,
    base_frame_path: Optional[str] = None,
    out_path: str = None,
    resolution: tuple = (1280, 720),
) -> str:
    """Canva-style YouTube thumbnail with branded overlay and bold title text."""
    w, h = resolution

    if base_frame_path and os.path.exists(base_frame_path):
        bg = Image.open(base_frame_path).convert("RGB").resize((w, h), Image.LANCZOS)
        # Apply slight blur to background to make text pop
        bg = bg.filter(ImageFilter.GaussianBlur(radius=2))
        # Darken
        bg = ImageEnhance.Brightness(bg).enhance(0.75)
    else:
        grads = style_cfg.get("bg_gradient", [("#0D0D12", "#1A1A2E")])
        bg = _gradient_background((w, h), grads[0][0], grads[0][1])

    # Bold gradient overlay (bottom half)
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ov = ImageDraw.Draw(overlay)
    for y in range(h):
        alpha = int(220 * max(0, (y - h * 0.3) / (h * 0.7)))
        ov.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(bg)
    primary = style_cfg.get("primary", "#FFFFFF")
    shadow  = style_cfg.get("text_shadow", "#000000")

    # Title — large bold text bottom-left
    font = _load_font(int(h * 0.14), bold=True)
    words = title.split()
    line1 = " ".join(words[:len(words)//2])
    line2 = " ".join(words[len(words)//2:])
    px, py = int(w * 0.05), int(h * 0.55)
    draw.text((px + 3, py + 3), line1, font=font, fill=shadow)
    draw.text((px, py), line1, font=font, fill=primary)
    py2 = py + int(h * 0.18)
    draw.text((px + 3, py2 + 3), line2, font=font, fill=shadow)
    draw.text((px, py2), line2, font=font, fill=primary)

    # Brand accent stripe (top-left)
    accent = _hex_to_rgb(primary)
    draw.rectangle([(0, 0), (int(w * 0.006), h)], fill=accent)

    bg.save(out_path, quality=95)
    log.info(f"  Thumbnail → {out_path}")
    return out_path


# ── AI Image Generation via Gemini Imagen ─────────────────────────────────────
def generate_ai_scene(
    prompt: str,
    style_cfg: dict,
    api_key: str,
    out_path: str,
    resolution: tuple = (1080, 1920),
) -> Optional[str]:
    """
    Use Gemini Imagen to generate a scene image from a text prompt.
    This is the InVideo AI "generate missing scene" feature.
    Falls back to a branded placeholder if Imagen is unavailable.
    """
    style_label = style_cfg.get("label", "cinematic")
    full_prompt = (
        f"{style_label} style, high quality, professional photography, "
        f"pet video frame: {prompt}"
    )

    try:
        from google import genai as _genai
        from google.genai.types import GenerateImagesConfig

        client = _genai.Client(api_key=api_key)
        response = client.models.generate_images(
            model="imagen-3.0-generate-001",
            prompt=full_prompt,
            config=GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="9:16" if resolution[0] < resolution[1] else "16:9",
            ),
        )
        img_bytes = response.generated_images[0].image.image_bytes
        img = Image.open(BytesIO(img_bytes)).resize(resolution, Image.LANCZOS)
        img.save(out_path, quality=95)
        log.info(f"  AI scene generated → {out_path}")
        return out_path

    except Exception as e:
        log.warning(f"  Imagen unavailable ({e}), using branded placeholder")
        return _branded_placeholder(prompt, style_cfg, resolution, out_path)


def _branded_placeholder(
    text: str, style_cfg: dict, resolution: tuple, out_path: str
) -> str:
    """Canva-like placeholder frame with gradient + text when Imagen is unavailable."""
    grads = style_cfg.get("bg_gradient", [("#1A1A2E", "#16213E")])
    bg = _gradient_background(resolution, grads[0][0], grads[0][1])
    w, h = resolution
    draw = ImageDraw.Draw(bg)
    primary = style_cfg.get("primary", "#FFFFFF")
    shadow  = style_cfg.get("text_shadow", "#000000")
    font = _load_font(int(w * 0.04))
    _draw_centered_text(draw, text, font, h // 2, w, primary, shadow, max_width=int(w * 0.8))
    if style_cfg.get("vignette"):
        bg = _add_vignette(bg, 0.4)
    bg.save(out_path, quality=90)
    return out_path


# ── Color Grading via FFmpeg ──────────────────────────────────────────────────
GRADE_FILTERS = {
    "teal_orange":    "colorchannelmixer=rr=1.1:gg=0.9:bb=1.05:rb=-0.03:br=0.05:bg=-0.05,eq=contrast=1.1:saturation=1.2",
    "warm_vibrant":   "eq=contrast=1.15:saturation=1.4:brightness=0.05,colorchannelmixer=rr=1.15:gg=1.0:bb=0.85",
    "warm_soft":      "eq=contrast=1.05:saturation=1.1:brightness=0.03,colorchannelmixer=rr=1.08:gg=1.0:bb=0.90",
    "neutral":        "eq=contrast=1.05:saturation=0.95",
    "high_contrast":  "eq=contrast=1.35:saturation=1.25:brightness=-0.05",
    "vibrant":        "eq=contrast=1.1:saturation=1.5:brightness=0.02",
}

def apply_color_grade(input_path: str, output_path: str, grade: str) -> str:
    """Apply Canva-style color grade to a video clip using FFmpeg."""
    vf = GRADE_FILTERS.get(grade, "eq=contrast=1.0")
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vf", vf,
        "-c:v", "libx264", "-crf", "20", "-preset", "fast",
        "-c:a", "copy",
        output_path
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    except Exception as e:
        log.warning(f"  Color grade failed: {e}, using original")
        return input_path
