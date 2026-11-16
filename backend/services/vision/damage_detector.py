"""Vehicle Damage Detector Service using fine-tuned YOLOv8 on CarDD dataset."""

import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from PIL import Image
import numpy as np

from ultralytics import YOLO
from backend.services.vision.preprocessing import load_and_preprocess_image
from backend.utils.logger import setup_logger

logger = setup_logger("claimsense.vision.detector")

CARDD_CLASS_NAMES = {
    0: "dent",
    1: "scratch",
    2: "crack",
    3: "glass shatter",
    4: "lamp broken",
    5: "tire flat",
}


def determine_spatial_region(
    bbox: List[float], img_width: int, img_height: int
) -> str:
    """Determines spatial region (e.g. 'front_left', 'rear_center') from bounding box centroid."""
    if img_width <= 0 or img_height <= 0:
        return "center"

    x1, y1, x2, y2 = bbox
    cx = (x1 + x2) / 2.0
    cy = (y1 + y2) / 2.0

    rx = cx / img_width
    ry = cy / img_height

    # Vertical categorization
    if ry < 0.35:
        vertical = "front"
    elif ry > 0.65:
        vertical = "rear"
    else:
        vertical = "mid"

    # Horizontal categorization
    if rx < 0.35:
        horizontal = "left"
    elif rx > 0.65:
        horizontal = "right"
    else:
        horizontal = "center"

    if vertical == "mid" and horizontal == "center":
        return "center"
    if vertical == "mid":
        return f"center_{horizontal}"
    if horizontal == "center":
        return f"{vertical}_center"
    return f"{vertical}_{horizontal}"


class VehicleDamageDetector:
    """Singleton service for detecting vehicle damage using YOLOv8."""

    _instance: Optional["VehicleDamageDetector"] = None

    def __init__(self, model_path: Optional[Union[str, Path]] = None):
        self.model_path = self._resolve_model_path(model_path)
        logger.info(f"Loading vehicle damage YOLO model from: {self.model_path}")
        self.model = YOLO(str(self.model_path))
        self.model_name = "YOLOv8n-CarDD"
        self.model_version = "v1.0"
        self.device = "cpu"

    @classmethod
    def get_instance(cls, model_path: Optional[Union[str, Path]] = None) -> "VehicleDamageDetector":
        """Provides a cached singleton detector to avoid loading weights on every call."""
        if cls._instance is None:
            cls._instance = cls(model_path)
        return cls._instance

    @staticmethod
    def _resolve_model_path(candidate_path: Optional[Union[str, Path]] = None) -> Path:
        """Finds the trained CarDD weights checkpoint, checking standard project locations."""
        if candidate_path:
            p = Path(candidate_path)
            if p.exists():
                return p

        # Search candidates in repository
        base_dir = Path(__file__).resolve().parents[3]
        candidates = [
            base_dir / "models" / "phase5" / "best.pt",
            base_dir / "models" / "vehicle_damage" / "best.pt",
            base_dir / "models" / "runs" / "cardd_damage" / "weights" / "best.pt",
            base_dir / "models" / "cardd_damage_yolov8n.pt",
            base_dir / "models" / "phase5" / "last.pt",
            base_dir / "models" / "vehicle_damage" / "last.pt",
            base_dir / "yolov8n.pt",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate

        raise FileNotFoundError(
            f"No vehicle damage model checkpoint found in: {[str(c) for c in candidates]}"
        )

    def detect_damage(
        self,
        image_input: Union[str, Path, bytes, Image.Image],
        conf_threshold: float = 0.15,
        iou_threshold: float = 0.45,
    ) -> Dict[str, Any]:
        """Runs damage detection on the given image and returns structured predictions."""
        pil_img, np_img, meta = load_and_preprocess_image(image_input)
        img_w = meta["width"]
        img_h = meta["height"]

        start_time = time.perf_counter()

        # Run inference
        results = self.model.predict(
            source=pil_img,
            conf=conf_threshold,
            iou=iou_threshold,
            device=self.device,
            verbose=False,
        )

        processing_time_ms = (time.perf_counter() - start_time) * 1000.0

        detections: List[Dict[str, Any]] = []
        highest_conf = 0.0

        if results and len(results) > 0:
            result = results[0]
            boxes = result.boxes

            if boxes is not None and len(boxes) > 0:
                for idx, box in enumerate(boxes, start=1):
                    cls_id = int(box.cls[0].item())
                    conf = float(box.conf[0].item())
                    xyxy = [float(v) for v in box.xyxy[0].tolist()]

                    # Clamp coordinates to image boundaries
                    x1 = max(0.0, min(float(img_w), xyxy[0]))
                    y1 = max(0.0, min(float(img_h), xyxy[1]))
                    x2 = max(0.0, min(float(img_w), xyxy[2]))
                    y2 = max(0.0, min(float(img_h), xyxy[3]))

                    category = CARDD_CLASS_NAMES.get(cls_id, f"damage_cls_{cls_id}")
                    region = determine_spatial_region([x1, y1, x2, y2], img_w, img_h)

                    if conf > highest_conf:
                        highest_conf = conf

                    detections.append({
                        "detection_index": idx,
                        "category": category,
                        "class_id": cls_id,
                        "confidence": round(conf, 4),
                        "confidence_percentage": round(conf * 100.0, 1),
                        "bbox": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                        "normalized_bbox": [
                            round(x1 / img_w, 4),
                            round(y1 / img_h, 4),
                            round(x2 / img_w, 4),
                            round(y2 / img_h, 4),
                        ],
                        "location_region": region,
                    })

        # Sort detections by confidence descending
        detections.sort(key=lambda d: d["confidence"], reverse=True)
        for i, det in enumerate(detections, start=1):
            det["detection_index"] = i

        distinct_categories = sorted(list({d["category"] for d in detections}))

        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "device": self.device,
            "image_dimensions": {"width": img_w, "height": img_h},
            "conf_threshold": conf_threshold,
            "total_detections": len(detections),
            "damage_categories": distinct_categories,
            "highest_confidence": round(highest_conf, 4),
            "processing_time_ms": round(processing_time_ms, 2),
            "detections": detections,
            "has_damage": len(detections) > 0,
        }
