from pathlib import Path
import hashlib
import re

from PIL import Image, ImageDraw, ImageFont
from google import genai

from .config import get_settings


def _safe(v):
    return (
        re.sub(r"[^a-zA-Z0-9_-]+", "_", v).strip("_") or "panel"
    )[:50]


def _demo(prompt, path, num):
    """Fallback placeholder generator."""
    s = get_settings()
    w, h = s.image_width, s.image_height

    d = hashlib.sha256(prompt.encode()).digest()
    bg = (235 + d[0] % 15, 225 + d[1] % 20, 190 + d[2] % 25)

    im = Image.new("RGB", (w, h), bg)
    dr = ImageDraw.Draw(im)
    f = ImageFont.load_default()
    m = 24

    dr.rounded_rectangle(
        (m, m, w - m, h - m),
        radius=22,
        outline=(25, 25, 25),
        width=5,
    )

    cx, cy = w // 2, h // 2 - 20
    r = min(w, h) // 5

    dr.ellipse(
        (cx - r, cy - r, cx + r, cy + r),
        outline=(30, 30, 30),
        width=5,
    )

    dr.text(
        (40, 40),
        f"PANEL {num}",
        fill=(20, 20, 20),
        font=f,
    )

    words = prompt[:350].split()
    lines = []
    line = ""

    for word in words:
        candidate = f"{line} {word}".strip()

        if len(candidate) > 46:
            lines.append(line)
            line = word
        else:
            line = candidate

    if line:
        lines.append(line)

    y = h - 120

    dr.rectangle(
        (35, y - 12, w - 35, h - 35),
        fill="white",
    )

    for t in lines[-4:]:
        dr.text(
            (48, y),
            t,
            fill=(25, 25, 25),
            font=f,
        )
        y += 18

    im.save(path, "PNG")


def _gemini_client():
    s = get_settings()

    if not s.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to your .env file."
        )

    return genai.Client(api_key=s.gemini_api_key)


def _generate_with_gemini(prompt, path):
    """
    Generate one comic panel using Gemini's native image generation.
    """

    s = get_settings()

    client = _gemini_client()

    image_model = getattr(
        s,
        "gemini_image_model",
        None,
    ) or "gemini-3.1-flash-image"

    comic_prompt = f"""
Create a single high-quality comic-book panel.

IMPORTANT:
- Generate ONLY the artwork for this panel.
- Do NOT generate a comic page containing multiple panels.
- Do NOT create a title outside the artwork.
- Do NOT add a watermark or UI.
- Do NOT put long written narration into the image.
- Leave clean visual space where speech bubbles or captions can be added later.
- Use consistent character appearance.
- Use expressive characters and cinematic composition.
- Make the scene visually clear and suitable for a modern colorful comic.

Panel description:

{prompt}
"""

    try:
        response = client.models.generate_content(
            model=image_model,
            contents=[comic_prompt],
        )

        generated_image = None

        for part in response.parts:
            if getattr(part, "inline_data", None) is not None:
                generated_image = part.as_image()
                break

        if generated_image is None:
            raise RuntimeError(
                "Gemini returned no image data."
            )

        # Save as PNG.
        generated_image.save(path, "PNG")

        # Resize to the project's configured panel size.
        target_width = s.image_width
        target_height = s.image_height

        with Image.open(path) as im:
            im = im.convert("RGB")
            im = im.resize(
                (target_width, target_height),
                Image.Resampling.LANCZOS,
            )
            im.save(path, "PNG")

    except Exception as e:
        raise RuntimeError(
            f"Gemini image generation failed: {e}"
        )


def generate_image(prompt: str, panel_number: int = 1):
    """
    Generate a comic panel.

    Supported backends:
      - demo
      - gemini
    """

    s = get_settings()

    name = (
        f"panel_{panel_number}_{_safe(prompt)}.png"
    )

    path = s.panels_dir / name

    backend = s.image_backend.lower().strip()

    if backend == "demo":
        _demo(
            prompt,
            path,
            panel_number,
        )

        return f"/static/panels/{name}"

    if backend == "gemini":
        _generate_with_gemini(
            prompt,
            path,
        )

        return f"/static/panels/{name}"

    raise RuntimeError(
        "IMAGE_BACKEND must be 'demo' or 'gemini'."
    )