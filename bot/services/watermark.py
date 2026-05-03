"""Add a subtle watermark to generated images."""
from __future__ import annotations

import io
from PIL import Image, ImageDraw, ImageFont

from bot.config import WATERMARK_TEXT


def add_watermark(image_bytes: bytes) -> bytes:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    w, h = img.size

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_size = max(14, w // 30)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except (IOError, OSError):
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), WATERMARK_TEXT, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    margin = 12
    x = w - text_w - margin
    y = h - text_h - margin

    draw.rectangle(
        [x - 6, y - 4, x + text_w + 6, y + text_h + 4],
        fill=(0, 0, 0, 90),
    )
    draw.text((x, y), WATERMARK_TEXT, font=font, fill=(255, 255, 255, 200))

    result = Image.alpha_composite(img, overlay).convert("RGB")
    buf = io.BytesIO()
    result.save(buf, format="JPEG", quality=92)
    return buf.getvalue()
