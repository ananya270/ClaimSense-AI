"""Standalone CLI runner for ClaimSense AI Vehicle Damage Detection Model.

Executes actual inference using YOLOv8n fine-tuned on the CarDD dataset.
"""
import sys
import json
import time
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.vision.damage_detector import VehicleDamageDetector
from backend.services.vision.visualization import create_annotated_image


def main():
    print("=" * 65)
    print("  CLAIMSENSE AI - VEHICLE DAMAGE DETECTION MODEL INFERENCE")
    print("=" * 65)

    model_path = PROJECT_ROOT / "models" / "phase5" / "best.pt"
    if not model_path.exists():
        model_path = PROJECT_ROOT / "models" / "cardd_damage_yolov8n.pt"

    print(f"\n[1] Loading model checkpoint: {model_path}")
    start_load = time.perf_counter()
    detector = VehicleDamageDetector.get_instance(model_path)
    load_time = (time.perf_counter() - start_load) * 1000.0

    print(f"    - Model Name:     {detector.model_name}")
    print(f"    - Architecture:   Ultralytics YOLOv8n")
    print(f"    - Device:         {detector.device}")
    print(f"    - Load Latency:   {load_time:.2f} ms")
    print(f"    - Target Classes: dent (0), scratch (1), crack (2), glass shatter (3), lamp broken (4), tire flat (5)")

    # Test Targets
    targets = [
        ("Claim CLM-20261116-WRTN Evidence", PROJECT_ROOT / "uploads" / "CLM-20261116-WRTN" / "images" / "replacement_vehicle_image_asdfghjkl.jpg"),
        ("CarDD-300 Test Image (000023.jpg)", PROJECT_ROOT / "datasets" / "CarDD_300" / "test" / "images" / "000023.jpg"),
        ("CarDD-300 Test Image (000042.jpg)", PROJECT_ROOT / "datasets" / "CarDD_300" / "test" / "images" / "000042.jpg"),
    ]

    for label, target_path in targets:
        if not target_path.exists():
            continue

        print("\n" + "-" * 65)
        print(f"[*] Running inference on: {label}")
        print(f"    File: {target_path}")

        result = detector.detect_damage(target_path, conf_threshold=0.15, iou_threshold=0.45)

        print(f"    Dimensions:         {result['image_dimensions']['width']} x {result['image_dimensions']['height']} px")
        print(f"    Inference Latency:  {result['processing_time_ms']:.2f} ms")
        print(f"    Total Detections:   {result['total_detections']}")
        print(f"    Peak Confidence:    {result['highest_confidence']*100:.1f}%")
        print(f"    Damage Categories:  {', '.join(result['damage_categories']) if result['damage_categories'] else 'None'}")

        if result['detections']:
            print("\n    Detections Breakdown:")
            for det in result['detections']:
                idx = det['detection_index']
                cat = det['category'].upper()
                conf = det['confidence_percentage']
                region = det['location_region']
                bbox = det['bbox']
                print(f"      [{idx:02d}] {cat:<14} | Conf: {conf:5.1f}% | Region: {region:<14} | BBox: {bbox}")

            # Generate/verify annotated photograph
            output_dir = PROJECT_ROOT / "models" / "phase5" / "inference_runs"
            output_dir.mkdir(parents=True, exist_ok=True)
            annotated_out = output_dir / f"annotated_{target_path.stem}.jpg"
            create_annotated_image(target_path, result['detections'], output_path=annotated_out)
            print(f"    Saved Annotated Output: {annotated_out}")

    print("\n" + "=" * 65)
    print("  MODEL INFERENCE RUN COMPLETED SUCCESSFULLY")
    print("=" * 65)


if __name__ == "__main__":
    main()
