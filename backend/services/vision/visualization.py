"""Visualization service to render annotated vehicle damage images."""

import os
from pathlib import Path
from typing import Dict, Any, List, Union, Optional
from PIL import Image, ImageDraw, ImageFont

from backend.services.vision.preprocessing import load_and_preprocess_image

# Color palette mapped by CarDD category (RGB format)
CATEGORY_COLORS_RGB = {
    "dent": (59, 130, 246),           # Electric Blue
    "scratch": (234, 179, 8),          # Amber Gold
    "crack": (239, 68, 68),            # Crimson Red
    "glass shatter": (6, 182, 212),    # Cyan
    "lamp broken": (249, 115, 22),     # Orange
    "tire flat": (168, 85, 247),       # Purple
}
DEFAULT_COLOR_RGB = (239, 68, 68)     # Default Red


def get_category_color(category: str) -> tuple:
    """Returns the RGB color tuple for a damage category."""
    return CATEGORY_COLORS_RGB.get(category.lower().strip(), DEFAULT_COLOR_RGB)


def create_annotated_image(
    image_input: Union[str, Path, bytes, Image.Image],
    detections: List[Dict[str, Any]],
    output_path: Optional[Union[str, Path]] = None,
) -> Image.Image:
    """Draws bounding boxes and labels for each detected damage instance on the image.

    Preserves original dimensions and aspect ratio, and saves to output_path if provided.
    """
    pil_img, _, meta = load_and_preprocess_image(image_input)
    annotated = pil_img.copy()
    draw = ImageDraw.Draw(annotated, "RGBA")

    img_w, img_h = annotated.size
    line_width = max(2, int(min(img_w, img_h) / 300))
    font_size = max(13, int(min(img_w, img_h) / 40))

    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    for det in detections:
        bbox = det.get("bbox", [0, 0, 0, 0])
        category = det.get("category", "damage")
        conf_pct = det.get("confidence_percentage", det.get("confidence", 0.0) * 100)
        region = det.get("location_region", "")

        x1, y1, x2, y2 = bbox
        color = get_category_color(category)

        # 1. Draw outer bounding box
        draw.rectangle([x1, y1, x2, y2], outline=color, width=line_width)

        # 2. Prepare badge label text
        label_text = f"{category.upper()} {conf_pct:.1f}%"
        if region and region != "center":
            label_text += f" [{region}]"

        # 3. Compute text dimensions for label background banner
        if hasattr(draw, "textbbox"):
            tb = draw.textbbox((0, 0), label_text, font=font)
            text_w = tb[2] - tb[0]
            text_h = tb[3] - tb[1]
        else:
            text_w = len(label_text) * 8
            text_h = 14

        pad = 4
        badge_y1 = max(0, y1 - text_h - pad * 2)
        badge_y2 = y1 if badge_y1 > 0 else (y1 + text_h + pad * 2)
        badge_x2 = min(img_w, x1 + text_w + pad * 2)

        # Draw filled background badge with slight transparency
        fill_color = color + (220,)
        draw.rectangle([x1, badge_y1, badge_x2, badge_y2], fill=fill_color)

        # Draw text in contrasting white
        draw.text(
            (x1 + pad, badge_y1 + pad),
            label_text,
            fill=(255, 255, 255),
            font=font,
        )

    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        annotated.save(out_p, format="JPEG", quality=92)

    return annotated
