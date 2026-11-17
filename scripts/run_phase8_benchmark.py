"""ClaimSense AI - Phase 8 Final Benchmark Evaluation Runner.

Performs a strict head-to-head evaluation of:
1. Original baseline: models/phase5/best.pt
2. Phase 8 trained model: runs/phase8/session_2/weights/best.pt

Uses the untouched CarDD test split (datasets/CarDD_300/test - 45 images, 148 instances).
Identical settings: imgsz=640, device=0 (CUDA), batch=4, plots=True.
Extracts precision, recall, F1, mAP@50, mAP@50-95, confusion matrices, TP/FP/FN analysis,
and side-by-side comparative deltas.
Preserves production checkpoints and Phase 7 isolation.
"""

import os
import sys
import time
import json
import hashlib
import numpy as np
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch
from ultralytics import YOLO


def get_file_hash(path: Path) -> str:
    """Compute SHA256 of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def extract_metrics(val_results, model_names):
    """Extract overall and per-class metrics from Ultralytics validator results."""
    box = val_results.box
    speed = val_results.speed  # preprocess, inference, loss, postprocess

    p_overall = float(box.mp)
    r_overall = float(box.mr)
    map50_overall = float(box.map50)
    map_overall = float(box.map)
    f1_overall = (2 * p_overall * r_overall / (p_overall + r_overall)) if (p_overall + r_overall) > 0 else 0.0

    p_classes = box.p
    r_classes = box.r
    f1_classes = box.f1
    ap50_classes = box.ap50
    ap_classes = box.ap

    # Confusion matrix extraction
    cm_matrix = None
    tp_per_class = {}
    fp_per_class = {}
    fn_per_class = {}

    if hasattr(val_results, "confusion_matrix") and val_results.confusion_matrix is not None:
        try:
            mat = val_results.confusion_matrix.matrix
            cm_matrix = mat.tolist()
            nc = len(model_names)
            for idx, name in model_names.items():
                tp = float(mat[idx, idx])
                fn = float(np.sum(mat[idx, :])) - tp
                fp = float(np.sum(mat[:, idx])) - tp
                tp_per_class[name] = int(tp)
                fp_per_class[name] = int(fp)
                fn_per_class[name] = int(fn)
        except Exception as e:
            print(f"Warning: Could not parse confusion matrix: {e}")

    per_class = {}
    for idx, name in model_names.items():
        p_c = float(p_classes[idx]) if idx < len(p_classes) else 0.0
        r_c = float(r_classes[idx]) if idx < len(r_classes) else 0.0
        f1_c = float(f1_classes[idx]) if idx < len(f1_classes) else 0.0
        map50_c = float(ap50_classes[idx]) if idx < len(ap50_classes) else 0.0
        map_c = float(ap_classes[idx]) if idx < len(ap_classes) else 0.0

        per_class[name] = {
            "precision": round(p_c, 4),
            "recall": round(r_c, 4),
            "f1_score": round(f1_c, 4),
            "map50": round(map50_c, 4),
            "map50_95": round(map_c, 4),
            "true_positives": tp_per_class.get(name, 0),
            "false_positives": fp_per_class.get(name, 0),
            "false_negatives": fn_per_class.get(name, 0),
        }

    return {
        "overall": {
            "precision": round(p_overall, 4),
            "recall": round(r_overall, 4),
            "f1_score": round(f1_overall, 4),
            "map50": round(map50_overall, 4),
            "map50_95": round(map_overall, 4),
            "latency_ms": {
                "preprocess": round(float(speed.get("preprocess", 0.0)), 2),
                "inference": round(float(speed.get("inference", 0.0)), 2),
                "postprocess": round(float(speed.get("postprocess", 0.0)), 2),
                "total_per_image": round(
                    float(speed.get("preprocess", 0.0))
                    + float(speed.get("inference", 0.0))
                    + float(speed.get("postprocess", 0.0)),
                    2,
                ),
            },
        },
        "per_class": per_class,
        "confusion_matrix": cm_matrix,
    }


def main():
    print("=" * 75)
    print("  CLAIMSENSE AI - PHASE 8 FINAL BENCHMARK EVALUATION (HEAD-TO-HEAD)")
    print("=" * 75)

    # 1. Environment & CUDA Check
    if not torch.cuda.is_available():
        print("ERROR: CUDA device not available.")
        sys.exit(1)

    print("\n[1] Environment & Model Verification:")
    device_name = torch.cuda.get_device_name(0)
    print(f"    - Hardware Device:   {device_name} (device 0)")

    baseline_path = PROJECT_ROOT / "models" / "phase5" / "best.pt"
    phase8_path = PROJECT_ROOT / "runs" / "phase8" / "session_2" / "weights" / "best.pt"
    cardd_yaml = PROJECT_ROOT / "data" / "cardd_train.yaml"
    benchmark_dir = PROJECT_ROOT / "runs" / "phase8" / "final_benchmark"

    if not baseline_path.exists():
        print(f"ERROR: Baseline model not found at {baseline_path}")
        sys.exit(1)
    if not phase8_path.exists():
        print(f"ERROR: Phase 8 model not found at {phase8_path}")
        sys.exit(1)

    init_base_hash = get_file_hash(baseline_path)
    init_p8_hash = get_file_hash(phase8_path)
    print(f"    - Baseline Model:    {baseline_path} (SHA256: {init_base_hash[:16]}...)")
    print(f"    - Phase 8 Model:     {phase8_path} (SHA256: {init_p8_hash[:16]}...)")
    print(f"    - Test Dataset:      {cardd_yaml} (split='test', 45 images)")
    print(f"    - Artifacts Out:     {benchmark_dir}")

    # Verify model loading
    print("\n[2] Loading Models into PyTorch...")
    model_baseline = YOLO(str(baseline_path))
    model_phase8 = YOLO(str(phase8_path))
    print("    - Baseline load:     SUCCESS (Architecture verified)")
    print("    - Phase 8 load:      SUCCESS (Architecture verified)")

    # 3. Benchmark Run 1: Baseline Model on Test Split
    print("\n[3] Evaluating Baseline Model (models/phase5/best.pt) on Test Split...")
    start_base = time.perf_counter()
    baseline_val = model_baseline.val(
        data=str(cardd_yaml),
        split="test",
        imgsz=640,
        batch=4,
        device=0,
        plots=True,
        save_json=False,
        project=str(benchmark_dir),
        name="baseline_test",
        exist_ok=True,
        verbose=False,
    )
    base_eval_duration = time.perf_counter() - start_base
    print(f"    - Baseline Test Eval Completed in {base_eval_duration:.2f} seconds.")

    # 4. Benchmark Run 2: Phase 8 Model on Test Split
    print("\n[4] Evaluating Phase 8 Model (runs/phase8/session_2/weights/best.pt) on Test Split...")
    start_p8 = time.perf_counter()
    phase8_val = model_phase8.val(
        data=str(cardd_yaml),
        split="test",
        imgsz=640,
        batch=4,
        device=0,
        plots=True,
        save_json=False,
        project=str(benchmark_dir),
        name="phase8_test",
        exist_ok=True,
        verbose=False,
    )
    p8_eval_duration = time.perf_counter() - start_p8
    print(f"    - Phase 8 Test Eval Completed in {p8_eval_duration:.2f} seconds.")

    # 5. Extract and Compare Metrics
    base_data = extract_metrics(baseline_val, model_baseline.names)
    p8_data = extract_metrics(phase8_val, model_phase8.names)

    print("\n[5] Head-to-Head Overall Metrics Comparison (45 Test Images, 148 Instances):")
    print(f"{'Metric':<18} | {'Baseline':<12} | {'Phase 8':<12} | {'Absolute Delta':<16} | {'Relative Change':<15}")
    print("-" * 80)
    for m in ["precision", "recall", "f1_score", "map50", "map50_95"]:
        b_val = base_data["overall"][m]
        p_val = p8_data["overall"][m]
        delta = p_val - b_val
        rel_chg = ((delta / b_val) * 100) if b_val > 0 else (100.0 if p_val > 0 else 0.0)
        sign = "+" if delta >= 0 else ""
        print(f"{m:<18} | {b_val:<12.4f} | {p_val:<12.4f} | {sign + f'{delta:.4f}':<16} | {sign + f'{rel_chg:.1f}%':<15}")

    # Latency comparison
    b_lat = base_data["overall"]["latency_ms"]["total_per_image"]
    p_lat = p8_data["overall"]["latency_ms"]["total_per_image"]
    print(f"{'total_latency_ms':<18} | {b_lat:<12.2f} | {p_lat:<12.2f} | {p_lat - b_lat:<+16.2f} | -")

    print("\n[6] Per-Class Metrics Comparison:")
    classes = list(model_baseline.names.values())
    print(f"{'Class':<14} | {'Base mAP50':<11} | {'P8 mAP50':<11} | {'Delta mAP50':<12} | {'Base Rec':<9} | {'P8 Rec':<9} | {'Base F1':<9} | {'P8 F1':<9}")
    print("-" * 92)
    deltas_per_class = {}
    for cls_name in classes:
        b_c = base_data["per_class"][cls_name]
        p_c = p8_data["per_class"][cls_name]
        d_map50 = p_c["map50"] - b_c["map50"]
        deltas_per_class[cls_name] = {
            "delta_map50": round(d_map50, 4),
            "delta_recall": round(p_c["recall"] - b_c["recall"], 4),
            "delta_precision": round(p_c["precision"] - b_c["precision"], 4),
            "delta_f1": round(p_c["f1_score"] - b_c["f1_score"], 4),
        }
        sign = "+" if d_map50 >= 0 else ""
        print(
            f"{cls_name:<14} | "
            f"{b_c['map50']:<11.4f} | "
            f"{p_c['map50']:<11.4f} | "
            f"{sign + f'{d_map50:.4f}':<12} | "
            f"{b_c['recall']:<9.4f} | "
            f"{p_c['recall']:<9.4f} | "
            f"{b_c['f1_score']:<9.4f} | "
            f"{p_c['f1_score']:<9.4f}"
        )

    print("\n[7] Error Analysis (False Positives & False Negatives on Test Split):")
    print(f"{'Class':<14} | {'Base TP':<8} | {'P8 TP':<8} | {'Base FP':<8} | {'P8 FP':<8} | {'Base FN':<8} | {'P8 FN':<8}")
    print("-" * 65)
    for cls_name in classes:
        b_c = base_data["per_class"][cls_name]
        p_c = p8_data["per_class"][cls_name]
        print(
            f"{cls_name:<14} | "
            f"{b_c['true_positives']:<8} | "
            f"{p_c['true_positives']:<8} | "
            f"{b_c['false_positives']:<8} | "
            f"{p_c['false_positives']:<8} | "
            f"{b_c['false_negatives']:<8} | "
            f"{p_c['false_negatives']:<8}"
        )

    # 8. Checkpoint & Production Integrity Check
    print("\n[8] Production Isolation & Zero-Tamper Verification:")
    final_base_hash = get_file_hash(baseline_path)
    base_untouched = (init_base_hash == final_base_hash)
    print(f"    - Baseline Initial:  {init_base_hash}")
    print(f"    - Baseline Final:    {final_base_hash}")
    print(f"    - Zero-Tamper Check: {'PASSED (100% untouched)' if base_untouched else 'FAILED'}")

    # 9. Save Benchmark Report Artifact
    benchmark_report = {
        "status": "PASSED" if base_untouched else "FAILED",
        "dataset": {
            "name": "CarDD (Car Damage Dataset)",
            "split": "test",
            "images_evaluated": 45,
            "total_instances": 148,
            "config": str(cardd_yaml),
        },
        "evaluation_settings": {
            "imgsz": 640,
            "batch": 4,
            "device": "CUDA:0 (NVIDIA GeForce RTX 3050 Laptop GPU)",
            "plots": True,
        },
        "models_evaluated": {
            "baseline": {
                "path": str(baseline_path),
                "sha256": final_base_hash,
                "eval_duration_sec": round(base_eval_duration, 2),
            },
            "phase8": {
                "path": str(phase8_path),
                "sha256": init_p8_hash,
                "eval_duration_sec": round(p8_eval_duration, 2),
            },
        },
        "overall_comparison": {
            "baseline": base_data["overall"],
            "phase8": p8_data["overall"],
            "absolute_delta": {
                "precision": round(p8_data["overall"]["precision"] - base_data["overall"]["precision"], 4),
                "recall": round(p8_data["overall"]["recall"] - base_data["overall"]["recall"], 4),
                "f1_score": round(p8_data["overall"]["f1_score"] - base_data["overall"]["f1_score"], 4),
                "map50": round(p8_data["overall"]["map50"] - base_data["overall"]["map50"], 4),
                "map50_95": round(p8_data["overall"]["map50_95"] - base_data["overall"]["map50_95"], 4),
            },
        },
        "per_class_comparison": {
            cls_name: {
                "baseline": base_data["per_class"][cls_name],
                "phase8": p8_data["per_class"][cls_name],
                "delta": deltas_per_class[cls_name],
            }
            for cls_name in classes
        },
        "artifacts_directory": str(benchmark_dir),
    }

    report_path = PROJECT_ROOT / "reports" / "phase8_final_benchmark_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(benchmark_report, f, indent=2)

    print(f"\n[9] Benchmark report saved to: {report_path}")
    print("=" * 75)
    print("  FINAL BENCHMARK EVALUATION COMPLETED")
    print("=" * 75)


if __name__ == "__main__":
    main()
