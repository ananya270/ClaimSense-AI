"""OpenCV-based image preprocessing for OCR and document cleanup."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Optional


def preprocess_image(image_path: str | os.PathLike[str], output_dir: Optional[str | os.PathLike[str]] = None) -> str:
    """Enhance image readability before OCR by converting to grayscale and applying thresholding."""
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image file does not exist: {image_path}")

    try:
        import cv2
        import numpy as np
    except ImportError:
        return str(image_path)

    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        return str(image_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    gray = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    _, thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    output_dir_path = Path(output_dir) if output_dir else Path(tempfile.gettempdir())
    output_dir_path.mkdir(parents=True, exist_ok=True)
    processed_name = f"processed_{image_path.stem}.png"
    output_path = output_dir_path / processed_name
    cv2.imwrite(str(output_path), thresholded)
    return str(output_path)
