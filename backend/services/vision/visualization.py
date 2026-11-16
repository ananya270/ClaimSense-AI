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
OPENCV_REGION_COLOR_RGB = (14, 165, 233)  # Sky Blue for non-semantic OpenCV contours


def get_category_color(category: str) -> tuple:
    """Returns the RGB color tuple for a damage category."""
    return CATEGORY_COLORS_RGB.get(category.lower().strip(), DEFAULT_COLOR_RGB)


def create_annotated_image(
    image_input: Union[str, Path, bytes, Image.Image],
    detections: List[Dict[str, Any]],
    output_path: Optional[Union[str, Path]] = None,
    opencv_observations: Optional[Dict[str, Any]] = None,
) -> Image.Image:
    """Draws bounding boxes and labels for each detected damage instance on the image.

    If detections are empty and opencv_observations are provided, generates an
    OpenCV structural analysis visualization without asserting false damage classes.
    Preserves original dimensions and aspect ratio, and saves to output_path if provided.
    """
    if (not detections) and opencv_observations:
        return create_opencv_visual_analysis(
            image_input=image_input,
            observations=opencv_observations,
            output_path=output_path,
        )

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


def create_opencv_visual_analysis(
    image_input: Union[str, Path, bytes, Image.Image],
    observations: Optional[Dict[str, Any]] = None,
    output_path: Optional[Union[str, Path]] = None,
) -> Image.Image:
    """Generates an OpenCV diagnostic visual analysis image.

    Explicitly labels morphological contours and edge regions without asserting
    semantic damage classes (e.g. no fake dents, scratches, cracks).
    """
    pil_img, _, meta = load_and_preprocess_image(image_input)
    annotated = pil_img.copy()
    draw = ImageDraw.Draw(annotated, "RGBA")

    img_w, img_h = annotated.size
    line_width = max(2, int(min(img_w, img_h) / 350))

    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    obs = observations or {}
    contour_info = obs.get("contour_analysis", obs)
    salient_contours = contour_info.get("salient_contours", [])
    quality = obs.get("image_quality", {})

    # 1. Top Informational Banner (Distinct from YOLO detections)
    banner_h = max(28, int(img_h * 0.05))
    draw.rectangle([0, 0, img_w, banner_h], fill=(15, 23, 42, 230))  # Dark Slate
    banner_title = "OPENCV STRUCTURAL ANALYSIS (TRADITIONAL CV - NO SEMANTIC DAMAGE PREDICTIONS)"
    draw.text((12, int(banner_h * 0.25)), banner_title, fill=(255, 255, 255), font=font)

    # 2. Render Salient Contour Regions (Neutral sky-blue outlines, non-semantic labels)
    for idx, sc in enumerate(salient_contours, start=1):
        bbox = sc.get("bbox", [0, 0, 0, 0])
        x1, y1, x2, y2 = bbox
        region = sc.get("relative_location", "surface")
        area = sc.get("area", 0)

        # Draw structural feature outline
        draw.rectangle([x1, y1, x2, y2], outline=OPENCV_REGION_COLOR_RGB, width=line_width)

        # Label as morphological feature, NEVER as damage category
        label_text = f"FEATURE #{idx} [{region}]"
        pad = 4
        text_h = 14
        raw_by1 = y1 - text_h - pad * 2
        raw_by2 = y1
        if raw_by1 < banner_h + 2:
            raw_by1 = max(banner_h + 2, y1)
            raw_by2 = raw_by1 + text_h + pad * 2

        by0 = min(raw_by1, raw_by2)
        by1 = max(raw_by1, raw_by2)
        bx0 = max(0, min(x1, x2))
        bx1 = min(img_w, bx0 + len(label_text) * 8 + pad * 2)

        draw.rectangle([bx0, by0, bx1, by1], fill=(14, 165, 233, 200))
        draw.text((bx0 + pad, by0 + pad), label_text, fill=(255, 255, 255), font=font)

    # 3. Bottom Diagnostic Metrics & Disclaimer Banner
    footer_h = max(32, int(img_h * 0.06))
    footer_y1 = img_h - footer_h
    draw.rectangle([0, footer_y1, img_w, img_h], fill=(15, 23, 42, 230))

    grade = quality.get("quality_grade", "ASSESSED")
    sharpness = quality.get("laplacian_variance", 0.0)
    edge_density = contour_info.get("edge_density_pct", 0.0)
    footer_text_1 = f"Quality: {grade} | Sharpness: {sharpness:.1f} | Edge Density: {edge_density}% | Salient Features: {len(salient_contours)}"
    footer_text_2 = "OpenCV Traditional CV Fallback: Bounding boxes indicate contour density, NOT semantic damage classes."

    draw.text((12, footer_y1 + 4), footer_text_1, fill=(226, 232, 240), font=font)
    draw.text((12, footer_y1 + 18), footer_text_2, fill=(148, 163, 184), font=font)

    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        annotated.save(out_p, format="JPEG", quality=92)

    return annotated

