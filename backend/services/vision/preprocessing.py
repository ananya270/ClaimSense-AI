"""Image preprocessing utilities for Phase 5 vehicle damage detection."""

import os
from pathlib import Path
from typing import Tuple, Union, Optional, Dict, Any, List
from PIL import Image, ImageOps
import numpy as np

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    cv2 = None
    OPENCV_AVAILABLE = False


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


def assess_image_quality(
    image_input: Union[str, Path, bytes, Image.Image, np.ndarray],
) -> Dict[str, Any]:
    """Evaluates image resolution, sharpness, contrast, brightness, and noise metrics."""
    if isinstance(image_input, np.ndarray):
        np_img = image_input
        h, w = np_img.shape[:2]
        channels = np_img.shape[2] if len(np_img.shape) == 3 else 1
    else:
        _, np_img, meta = load_and_preprocess_image(image_input)
        w, h = meta["width"], meta["height"]
        channels = meta.get("channels", 3)

    # Grayscale conversion for analytical metrics
    if OPENCV_AVAILABLE and cv2 is not None:
        if len(np_img.shape) == 3:
            gray = cv2.cvtColor(np_img, cv2.COLOR_RGB2GRAY)
        else:
            gray = np_img.copy()

        # 1. Sharpness via Laplacian variance
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        lap_var = float(laplacian.var())
        is_sharp = bool(lap_var >= 100.0)

        # 2. Contrast via standard deviation
        contrast_std = float(gray.std())

        # 3. Mean brightness
        mean_brightness = float(gray.mean())

        # 4. Noise estimation via difference from median blur
        blurred = cv2.medianBlur(gray, 3)
        noise_diff = cv2.absdiff(gray, blurred)
        noise_score = float(noise_diff.mean())

        # Quality grade
        if lap_var > 150 and contrast_std > 40 and 40 < mean_brightness < 220:
            quality_grade = "GOOD"
        elif lap_var > 60 and contrast_std > 25:
            quality_grade = "FAIR"
        else:
            quality_grade = "POOR"

        return {
            "width": w,
            "height": h,
            "megapixels": round((w * h) / 1_000_000, 2),
            "channels": channels,
            "laplacian_variance": round(lap_var, 2),
            "is_sharp": is_sharp,
            "contrast_std": round(contrast_std, 2),
            "mean_brightness": round(mean_brightness, 2),
            "noise_score": round(noise_score, 2),
            "quality_grade": quality_grade,
            "engine": "opencv",
        }
    else:
        # Fallback using standard numpy calculations if OpenCV is not available
        if len(np_img.shape) == 3:
            gray = np_img.mean(axis=2).astype(np.float64)
        else:
            gray = np_img.astype(np.float64)

        contrast_std = float(gray.std())
        mean_brightness = float(gray.mean())

        return {
            "width": w,
            "height": h,
            "megapixels": round((w * h) / 1_000_000, 2),
            "channels": channels,
            "laplacian_variance": 0.0,
            "is_sharp": True,
            "contrast_std": round(contrast_std, 2),
            "mean_brightness": round(mean_brightness, 2),
            "noise_score": 0.0,
            "quality_grade": "UNKNOWN",
            "engine": "numpy_fallback",
        }


def enhance_contrast_clahe(
    np_img: np.ndarray,
    clip_limit: float = 2.0,
    tile_grid_size: Tuple[int, int] = (8, 8),
) -> np.ndarray:
    """Applies Contrast Limited Adaptive Histogram Equalization (CLAHE) on the luminance channel."""
    if not OPENCV_AVAILABLE or cv2 is None or len(np_img.shape) != 3:
        return np_img

    lab = cv2.cvtColor(np_img, cv2.COLOR_RGB2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    cl = clahe.apply(l_channel)
    enhanced_lab = cv2.merge((cl, a_channel, b_channel))
    return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)


def reduce_noise(np_img: np.ndarray, method: str = "bilateral") -> np.ndarray:
    """Applies edge-preserving noise reduction using Bilateral Filtering or Gaussian blur."""
    if not OPENCV_AVAILABLE or cv2 is None:
        return np_img

    if method == "bilateral":
        return cv2.bilateralFilter(np_img, 9, 75, 75)
    elif method == "gaussian":
        return cv2.GaussianBlur(np_img, (5, 5), 0)
    return np_img


def detect_edges_and_contours(
    np_img: np.ndarray,
    min_contour_area: int = 150,
    max_contours: int = 25,
) -> Dict[str, Any]:
    """Performs traditional OpenCV Canny edge detection and contour extraction.

    NOTE: Contour detections represent image gradient boundaries and structural features,
    NOT validated vehicle damage classifications.
    """
    if not OPENCV_AVAILABLE or cv2 is None:
        return {
            "edge_density": 0.0,
            "edge_pixels": 0,
            "total_contours": 0,
            "salient_contours": [],
            "edges": None,
        }

    h, w = np_img.shape[:2]
    total_pixels = h * w

    # Grayscale
    if len(np_img.shape) == 3:
        gray = cv2.cvtColor(np_img, cv2.COLOR_RGB2GRAY)
    else:
        gray = np_img.copy()

    # Pre-blur to reduce high-frequency noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Adaptive Canny thresholds based on median intensity
    med = float(np.median(blurred))
    sigma = 0.33
    lower_thresh = int(max(0, (1.0 - sigma) * med))
    upper_thresh = int(min(255, (1.0 + sigma) * med))
    edges = cv2.Canny(blurred, lower_thresh, upper_thresh)

    edge_pixels = int(np.count_nonzero(edges))
    edge_density = float(round(edge_pixels / max(1, total_pixels), 4))

    # Dilate edges slightly to close gaps for contour discovery
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated = cv2.dilate(edges, kernel, iterations=1)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    salient_contours = []
    for c in contours:
        area = float(cv2.contourArea(c))
        if area >= min_contour_area:
            x, y, cw, ch = cv2.boundingRect(c)
            # Filter out full-image border contours
            if cw >= w * 0.98 and ch >= h * 0.98:
                continue
            peri = float(cv2.arcLength(c, True))
            salient_contours.append({
                "bbox": [float(x), float(y), float(x + cw), float(y + ch)],
                "area": float(round(area, 1)),
                "perimeter": float(round(peri, 1)),
                "aspect_ratio": float(round(cw / max(1, ch), 3)),
            })

    # Sort by area descending and cap
    salient_contours.sort(key=lambda item: item["area"], reverse=True)
    salient_contours = salient_contours[:max_contours]

    return {
        "edge_density": edge_density,
        "edge_density_pct": round(edge_density * 100.0, 2),
        "edge_pixels": edge_pixels,
        "total_contours": len(contours),
        "salient_contours": salient_contours,
    }
