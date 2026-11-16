"""Computer Vision service package (Phase 5: Vehicle Damage Detection)."""

from backend.services.vision.preprocessing import (
    validate_image_file,
    load_and_preprocess_image,
)
from backend.services.vision.damage_detector import (
    VehicleDamageDetector,
    determine_spatial_region,
    CARDD_CLASS_NAMES,
)
from backend.services.vision.visualization import (
    create_annotated_image,
    get_category_color,
    CATEGORY_COLORS_RGB,
)
from backend.services.vision.evaluation import (
    get_model_evaluation_metrics,
)

__all__ = [
    "validate_image_file",
    "load_and_preprocess_image",
    "VehicleDamageDetector",
    "determine_spatial_region",
    "CARDD_CLASS_NAMES",
    "create_annotated_image",
    "get_category_color",
    "CATEGORY_COLORS_RGB",
    "get_model_evaluation_metrics",
]
