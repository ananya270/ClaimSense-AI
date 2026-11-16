"""Image preprocessing utilities for Phase 5 vehicle damage detection."""

import os
from pathlib import Path
from typing import Tuple, Union, Optional, Dict, Any
from PIL import Image, ImageOps
import numpy as np


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def validate_image_file(image_path: Union[str, Path]) -> Tuple[bool, Optional[str]]:
    """Validates that image file exists, is non-empty, and has an allowed format."""
    path = Path(image_path)
    if not path.exists():
        return False, f"Image file not found: {path}"
    if not path.is_file():
        return False, f"Path is not a regular file: {path}"
    if path.stat().st_size == 0:
        return False, f"Image file is empty: {path}"
    if path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
        return False, f"Unsupported image extension '{path.suffix}'. Allowed: {', '.join(sorted(SUPPORTED_IMAGE_EXTENSIONS))}"
    return True, None


def load_and_preprocess_image(
    image_input: Union[str, Path, bytes, Image.Image],
) -> Tuple[Image.Image, np.ndarray, Dict[str, Any]]:
    """Loads an image, applies EXIF orientation normalization, converts to RGB,

    and returns both PIL.Image and NumPy RGB array along with image metadata.
    """
    metadata: Dict[str, Any] = {}

    if isinstance(image_input, (str, Path)):
        img_path = Path(image_input)
        is_valid, err = validate_image_file(img_path)
        if not is_valid:
            raise ValueError(err)
        pil_img = Image.open(img_path)
        metadata["source_path"] = str(img_path)
        metadata["file_name"] = img_path.name
        metadata["file_size_bytes"] = img_path.stat().st_size
    elif isinstance(image_input, bytes):
        import io
        pil_img = Image.open(io.BytesIO(image_input))
        metadata["source_type"] = "bytes"
        metadata["file_size_bytes"] = len(image_input)
    elif isinstance(image_input, Image.Image):
        pil_img = image_input.copy()
        metadata["source_type"] = "pil_image"
    else:
        raise TypeError(f"Unsupported image input type: {type(image_input)}")

    # 1. Normalize EXIF orientation (crucial for mobile/tablet accident photos)
    try:
        pil_img = ImageOps.exif_transpose(pil_img)
    except Exception:
        # Some images might have malformed EXIF headers; ignore transpose safely
        pass

    # 2. Standardize color mode to RGB
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")

    width, height = pil_img.size
    metadata["width"] = width
    metadata["height"] = height
    metadata["aspect_ratio"] = round(width / max(1, height), 3)

    # 3. Convert to NumPy array
    np_img = np.array(pil_img)
    metadata["channels"] = np_img.shape[2] if len(np_img.shape) == 3 else 1

    return pil_img, np_img, metadata
