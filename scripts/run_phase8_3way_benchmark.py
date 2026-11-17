"""ClaimSense AI - Phase 8 Final Controlled 3-Way Test Benchmarking.

Evaluates three checkpoints on the frozen CarDD test set (datasets/CarDD_300/test - 45 images, 148 instances):
1. Production Baseline: models/phase5/best.pt
2. Session 2 Checkpoint: runs/phase8/session_2/weights/best.pt
3. Session 4 Checkpoint: runs/phase8/session_4_training_01/weights/best.pt

Identical evaluation settings:
- Dataset Config: data/cardd_train.yaml (split='test')
- Resolution: 640x640
- Hardware: CUDA:0 (NVIDIA GeForce RTX 3050 Laptop GPU)
- Batch Size: 4 (with fallback to 2 on OOM)
- Evaluator: Ultralytics YOLO validator (identical version)
- Metrics: Precision, Recall, F1, mAP@50, mAP@50-95, TP/FP/FN analysis, latency benchmark.
- Isolation: Verifies SHA256 hashes before and after; saves outputs under runs/phase8/final_benchmark/
"""

import os
import sys
import time
import json
import hashlib
import multiprocessing
from pathlib import Path
import numpy as np

# Ensure project root in sys.path
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


def measure_dedicated_latency(model, test_images, num_warmup=10):
    """Measure precise per-image inference latency with CUDA synchronization."""
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    
    # Warm-up passes with dummy tensor
    dummy = torch.zeros((1, 3, 640, 640), device=device, dtype=torch.float32)
    for _ in range(num_warmup):
        _ = model.predict(dummy, imgsz=640, device=0, verbose=False)
    
    if torch.cuda.is_available():
        torch.cuda.synchronize()

    # Per-image latency timing using CUDA Events
    timings_ms = []
    starter = torch.cuda.Event(enable_timing=True)
    ender = torch.cuda.Event(enable_timing=True)

    for img_path in test_images:
        starter.record()
        _ = model.predict(str(img_path), imgsz=640, device=0, conf=0.25, iou=0.6, verbose=False)
        ender.record()
        torch.cuda.synchronize()
        timings_ms.append(starter.elapsed_time(ender))

    timings_ms = np.array(timings_ms)
    return {
        "mean_ms": round(float(np.mean(timings_ms)), 2),
        "median_ms": round(float(np.median(timings_ms)), 2),
        "std_ms": round(float(np.std(timings_ms)), 2),
        "min_ms": round(float(np.min(timings_ms)), 2),
        "max_ms": round(float(np.max(timings_ms)), 2),
        "fps": round(1000.0 / float(np.mean(timings_ms)), 1) if np.mean(timings_ms) > 0 else 0.0,
        "sample_count": len(timings_ms),
    }


def extract_evaluation_metrics(val_results, model_names):
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
    gt_per_class = {}

    if hasattr(val_results, "confusion_matrix") and val_results.confusion_matrix is not None:
        try:
            mat = val_results.confusion_matrix.matrix
            cm_matrix = mat.tolist()
            nc = len(model_names)
            for idx, name in model_names.items():
                tp = float(mat[idx, idx])
                # Ground truth total is sum along row idx
                gt_total = float(np.sum(mat[idx, :]))
                fn = gt_total - tp
                # Predicted total is sum along col idx
                pred_total = float(np.sum(mat[:, idx]))
                fp = pred_total - tp

                tp_per_class[name] = int(tp)
                fp_per_class[name] = int(fp)
                fn_per_class[name] = int(fn)
                gt_per_class[name] = int(gt_total)
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
            "class_id": idx,
            "precision": round(p_c, 4),
            "recall": round(r_c, 4),
            "f1_score": round(f1_c, 4),
            "map50": round(map50_c, 4),
            "map50_95": round(map_c, 4),
            "ground_truth_instances": gt_per_class.get(name, 0),
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
            "total_ground_truth": sum(gt_per_class.values()),
            "total_true_positives": sum(tp_per_class.values()),
            "total_false_positives": sum(fp_per_class.values()),
            "total_false_negatives": sum(fn_per_class.values()),
            "validator_speed_ms": {
                "preprocess": round(float(speed.get("preprocess", 0.0)), 2),
                "inference": round(float(speed.get("inference", 0.0)), 2),
                "loss": round(float(speed.get("loss", 0.0)), 2),
                "postprocess": round(float(speed.get("postprocess", 0.0)), 2),
                "total": round(
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
    print("=" * 80, flush=True)
    print("  CLAIMSENSE AI - PHASE 8 FINAL CONTROLLED 3-WAY TEST BENCHMARK", flush=True)
    print("  Test Set: CarDD Frozen Test Split (datasets/CarDD_300/test/images)", flush=True)
    print("  Scope: Production Baseline vs Session 2 vs Session 4", flush=True)
    print("=" * 80, flush=True)

    # 1. Environment & CUDA Pre-check
    print("\n[1] Environment & Hardware Pre-check...", flush=True)
    if not torch.cuda.is_available():
        print("ERROR: CUDA device is not available. Halting.", flush=True)
        sys.exit(1)

    device_name = torch.cuda.get_device_name(0)
    total_vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    print(f"    - Hardware Device:   {device_name} (CUDA:0)", flush=True)
    print(f"    - Total VRAM:        {total_vram_gb:.2f} GB", flush=True)

    # Target models definition
    models_to_evaluate = [
        {
            "key": "production_baseline",
            "name": "Production Baseline (Phase 5)",
            "path": PROJECT_ROOT / "models" / "phase5" / "best.pt",
            "output_subfolder": "eval_production",
            "expected_hash": "90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565",
        },
        {
            "key": "session_2",
            "name": "Phase 8 - Session 2",
            "path": PROJECT_ROOT / "runs" / "phase8" / "session_2" / "weights" / "best.pt",
            "output_subfolder": "eval_session_2",
            "expected_hash": "2ee0a56749ceba72da863fd3496f080ee06f26409daa4e9588fb69ee149333c5",
        },
        {
            "key": "session_4",
            "name": "Phase 8 - Session 4",
            "path": PROJECT_ROOT / "runs" / "phase8" / "session_4_training_01" / "weights" / "best.pt",
            "output_subfolder": "eval_session_4",
            "expected_hash": "ea53eee94e508bbb81620b47b2a23c9826341b6b5a6981d9371e476cb9d0594f",
        },
    ]

    cardd_yaml = PROJECT_ROOT / "data" / "cardd_train.yaml"
    benchmark_dir = PROJECT_ROOT / "runs" / "phase8" / "final_benchmark"
    test_images_dir = PROJECT_ROOT / "datasets" / "CarDD_300" / "test" / "images"
    test_labels_dir = PROJECT_ROOT / "datasets" / "CarDD_300" / "test" / "labels"

    # Pre-benchmark verification of test set
    test_images = sorted(list(test_images_dir.glob("*.*")))
    test_labels = sorted(list(test_labels_dir.glob("*.txt")))
    assert len(test_images) == 45, f"Expected 45 test images, found {len(test_images)}"
    assert len(test_labels) == 45, f"Expected 45 test labels, found {len(test_labels)}"
    print(f"    - Test Dataset:      {len(test_images)} images, {len(test_labels)} labels (FROZEN UNTOUCHED)", flush=True)

    # Pre-benchmark hash verification
    print("\n[2] Pre-benchmark Checkpoint Hash Verification:", flush=True)
    initial_hashes = {}
    for item in models_to_evaluate:
        p = item["path"]
        if not p.exists():
            print(f"ERROR: Checkpoint not found at: {p}", flush=True)
            sys.exit(1)
        h = get_file_hash(p)
        initial_hashes[item["key"]] = h
        match = (h == item["expected_hash"])
        print(f"    - {item['name']:<28} | Hash: {h[:16]}... | Match Expected: {match}", flush=True)
        if not match:
            print(f"ERROR: Hash mismatch for {item['name']}! Expected {item['expected_hash']}, got {h}", flush=True)
            sys.exit(1)

    # 3. Controlled Evaluation Execution for each Checkpoint
    print("\n[3] Executing Standardized Evaluations on Frozen Test Set...", flush=True)
    eval_results_data = {}
    latency_data = {}
    durations = {}

    batch_size = 4
    imgsz = 640

    for item in models_to_evaluate:
        key = item["key"]
        name = item["name"]
        ckpt_path = item["path"]
        subfolder = item["output_subfolder"]
        target_dir = benchmark_dir / subfolder

        print(f"\n---> Evaluating [{name}]...", flush=True)
        print(f"     Checkpoint: {ckpt_path}", flush=True)
        print(f"     Output:     {target_dir}", flush=True)

        torch.cuda.empty_cache()
        model = YOLO(str(ckpt_path))

        # Standardized latency benchmark
        print(f"     Running dedicated latency benchmark (warm-up + 45 test images)...", flush=True)
        lat = measure_dedicated_latency(model, test_images, num_warmup=10)
        latency_data[key] = lat
        print(f"     Latency: mean={lat['mean_ms']}ms, median={lat['median_ms']}ms, FPS={lat['fps']}", flush=True)

        # Standardized Ultralytics val run
        start_val = time.perf_counter()
        try:
            val_out = model.val(
                data=str(cardd_yaml),
                split="test",
                imgsz=imgsz,
                batch=batch_size,
                device=0,
                plots=True,
                save_json=False,
                project=str(benchmark_dir),
                name=subfolder,
                exist_ok=True,
                verbose=False,
            )
        except torch.cuda.OutOfMemoryError:
            print("     [WARNING] OOM encountered at batch=4. Falling back to batch=2...", flush=True)
            torch.cuda.empty_cache()
            val_out = model.val(
                data=str(cardd_yaml),
                split="test",
                imgsz=imgsz,
                batch=2,
                device=0,
                plots=True,
                save_json=False,
                project=str(benchmark_dir),
                name=subfolder,
                exist_ok=True,
                verbose=False,
            )

        duration = time.perf_counter() - start_val
        durations[key] = duration
        print(f"     Val run completed in {duration:.2f} seconds.", flush=True)

        parsed_metrics = extract_evaluation_metrics(val_out, model.names)
        eval_results_data[key] = parsed_metrics

    # 4. Post-benchmark Checkpoint Hash Verification
    print("\n[4] Post-benchmark Checkpoint Integrity Verification (Zero-Tamper Check):", flush=True)
    all_intact = True
    for item in models_to_evaluate:
        key = item["key"]
        p = item["path"]
        post_h = get_file_hash(p)
        pre_h = initial_hashes[key]
        intact = (post_h == pre_h)
        if not intact:
            all_intact = False
        print(f"    - {item['name']:<28} | Post-Hash: {post_h[:16]}... | Intact: {intact}", flush=True)

    assert all_intact, "CRITICAL ERROR: One or more checkpoints were modified during evaluation!"
    print("    - Checkpoint Integrity: 100% UNTOUCHED & VERIFIED", flush=True)

    # 5. Build Comparative Analysis
    print("\n[5] Overall Metrics Comparison (45 Test Images, 148 Ground-Truth Instances):", flush=True)
    header = f"{'Metric':<16} | {'Production':<12} | {'Session 2':<12} | {'Session 4':<12} | {'S4 vs Prod':<14} | {'S4 vs S2':<14}"
    print(header, flush=True)
    print("-" * len(header), flush=True)

    overall_metrics_keys = ["precision", "recall", "f1_score", "map50", "map50_95"]
    comparative_overall = {}

    prod_ov = eval_results_data["production_baseline"]["overall"]
    s2_ov = eval_results_data["session_2"]["overall"]
    s4_ov = eval_results_data["session_4"]["overall"]

    for m in overall_metrics_keys:
        p_val = prod_ov[m]
        s2_val = s2_ov[m]
        s4_val = s4_ov[m]

        d_prod = s4_val - p_val
        d_s2 = s4_val - s2_val

        sign_p = "+" if d_prod >= 0 else ""
        sign_s2 = "+" if d_s2 >= 0 else ""

        comparative_overall[m] = {
            "production": p_val,
            "session_2": s2_val,
            "session_4": s4_val,
            "delta_s4_vs_prod": round(d_prod, 4),
            "delta_s4_vs_s2": round(d_s2, 4),
        }
        print(
            f"{m:<16} | {p_val:<12.4f} | {s2_val:<12.4f} | {s4_val:<12.4f} | {sign_p + f'{d_prod:.4f}':<14} | {sign_s2 + f'{d_s2:.4f}':<14}",
            flush=True,
        )

    # Latency row
    p_lat = latency_data["production_baseline"]["mean_ms"]
    s2_lat = latency_data["session_2"]["mean_ms"]
    s4_lat = latency_data["session_4"]["mean_ms"]
    print(
        f"{'latency_mean_ms':<16} | {p_lat:<12.2f} | {s2_lat:<12.2f} | {s4_lat:<12.2f} | {s4_lat - p_lat:<+14.2f} | {s4_lat - s2_lat:<+14.2f}",
        flush=True,
    )

    # 6. Per-Class Metrics Comparison
    print("\n[6] Per-Class mAP@50 and Recall Comparison:", flush=True)
    class_names = list(eval_results_data["production_baseline"]["per_class"].keys())
    c_header = f"{'Class':<14} | {'Prod mAP50':<11} | {'S2 mAP50':<11} | {'S4 mAP50':<11} | {'S4 vs Prod':<12} | {'S4 vs S2':<12} | {'Prod Rec':<9} | {'S2 Rec':<9} | {'S4 Rec':<9}"
    print(c_header, flush=True)
    print("-" * len(c_header), flush=True)

    comparative_per_class = {}
    for c_name in class_names:
        p_c = eval_results_data["production_baseline"]["per_class"][c_name]
        s2_c = eval_results_data["session_2"]["per_class"][c_name]
        s4_c = eval_results_data["session_4"]["per_class"][c_name]

        d_map_prod = s4_c["map50"] - p_c["map50"]
        d_map_s2 = s4_c["map50"] - s2_c["map50"]

        sign_p = "+" if d_map_prod >= 0 else ""
        sign_s2 = "+" if d_map_s2 >= 0 else ""

        comparative_per_class[c_name] = {
            "production": p_c,
            "session_2": s2_c,
            "session_4": s4_c,
            "delta_map50_s4_vs_prod": round(d_map_prod, 4),
            "delta_map50_s4_vs_s2": round(d_map_s2, 4),
            "delta_recall_s4_vs_prod": round(s4_c["recall"] - p_c["recall"], 4),
            "delta_recall_s4_vs_s2": round(s4_c["recall"] - s2_c["recall"], 4),
            "delta_precision_s4_vs_prod": round(s4_c["precision"] - p_c["precision"], 4),
            "delta_precision_s4_vs_s2": round(s4_c["precision"] - s2_c["precision"], 4),
            "delta_f1_s4_vs_prod": round(s4_c["f1_score"] - p_c["f1_score"], 4),
            "delta_f1_s4_vs_s2": round(s4_c["f1_score"] - s2_c["f1_score"], 4),
        }

        print(
            f"{c_name:<14} | "
            f"{p_c['map50']:<11.4f} | "
            f"{s2_c['map50']:<11.4f} | "
            f"{s4_c['map50']:<11.4f} | "
            f"{sign_p + f'{d_map_prod:.4f}':<12} | "
            f"{sign_s2 + f'{d_map_s2:.4f}':<12} | "
            f"{p_c['recall']:<9.4f} | "
            f"{s2_c['recall']:<9.4f} | "
            f"{s4_c['recall']:<9.4f}",
            flush=True,
        )

    # 7. Detailed TP / FP / FN Breakdown
    print("\n[7] Detailed Detection Error Analysis (TP / FP / FN at Conf=0.25, IoU=0.45):", flush=True)
    err_header = f"{'Class':<14} | {'GT':<4} | {'Prod TP':<8} {'S2 TP':<8} {'S4 TP':<8} | {'Prod FP':<8} {'S2 FP':<8} {'S4 FP':<8} | {'Prod FN':<8} {'S2 FN':<8} {'S4 FN':<8}"
    print(err_header, flush=True)
    print("-" * len(err_header), flush=True)

    for c_name in class_names:
        p_c = eval_results_data["production_baseline"]["per_class"][c_name]
        s2_c = eval_results_data["session_2"]["per_class"][c_name]
        s4_c = eval_results_data["session_4"]["per_class"][c_name]
        gt = p_c["ground_truth_instances"]
        print(
            f"{c_name:<14} | {gt:<4} | "
            f"{p_c['true_positives']:<8} {s2_c['true_positives']:<8} {s4_c['true_positives']:<8} | "
            f"{p_c['false_positives']:<8} {s2_c['false_positives']:<8} {s4_c['false_positives']:<8} | "
            f"{p_c['false_negatives']:<8} {s2_c['false_negatives']:<8} {s4_c['false_negatives']:<8}",
            flush=True,
        )

    # 8. Save Machine-Readable Benchmark Deliverables
    benchmark_report_payload = {
        "status": "PASSED",
        "benchmark_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "dataset": {
            "name": "CarDD Frozen Test Split",
            "config": str(cardd_yaml),
            "images_count": len(test_images),
            "labels_count": len(test_labels),
            "total_ground_truth_instances": 148,
        },
        "evaluation_settings": {
            "imgsz": imgsz,
            "batch": batch_size,
            "device": f"CUDA:0 ({device_name})",
            "evaluator": "Ultralytics YOLO Validator",
            "matching_criteria": {
                "mAP_conf_threshold": 0.001,
                "mAP_iou_thresholds": "0.50:0.95:0.05",
                "confusion_matrix_conf_threshold": 0.25,
                "confusion_matrix_iou_threshold": 0.45,
            },
        },
        "models": {
            item["key"]: {
                "name": item["name"],
                "path": str(item["path"]),
                "sha256": initial_hashes[item["key"]],
                "eval_duration_sec": round(durations[item["key"]], 2),
                "latency_bench": latency_data[item["key"]],
                "artifacts_dir": str(benchmark_dir / item["output_subfolder"]),
            }
            for item in models_to_evaluate
        },
        "comparative_overall": comparative_overall,
        "comparative_per_class": comparative_per_class,
        "raw_results": eval_results_data,
        "evaluation_limitations": [
            "Sample size: The frozen test set contains 45 images and 148 ground-truth instances. Minor classes such as crack (13 instances) and tire flat (6 instances) have high variance where 1 true positive represents ~7.7% and ~16.7% recall delta respectively.",
            "Confusion Matrix vs mAP operating point: The TP, FP, FN metrics are evaluated at a fixed confidence threshold (0.25) and IoU threshold (0.45), whereas mAP integrates over the entire precision-recall curve across confidence thresholds [0.001, 1.0].",
            "Hardware latency: Latency was measured on an NVIDIA GeForce RTX 3050 Laptop GPU (4GB VRAM) under Windows 11. Production deployment on server-grade GPUs (e.g. T4, A10G, L4) will exhibit different latency scaling.",
        ],
        "promotion_recommendation": {
            "authorized": False,
            "decision": "HOLD_PENDING_SEPARATE_HUMAN_AUTHORIZATION",
            "reason": "Controlled benchmarking completed. Production model remains active and untouched per strict execution constraints.",
        },
    }

    # Save to runs/phase8/final_benchmark/benchmark_report.json
    out_json = benchmark_dir / "benchmark_report.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(benchmark_report_payload, f, indent=2)

    # Also save to reports/phase8_final_benchmark_report.json
    reports_json = PROJECT_ROOT / "reports" / "phase8_final_benchmark_report.json"
    reports_json.parent.mkdir(parents=True, exist_ok=True)
    with open(reports_json, "w", encoding="utf-8") as f:
        json.dump(benchmark_report_payload, f, indent=2)

    print(f"\n[8] Full Machine-Readable Reports Saved to:")
    print(f"    - {out_json}", flush=True)
    print(f"    - {reports_json}", flush=True)
    print("=" * 80, flush=True)
    print("  PHASE 8 FINAL 3-WAY BENCHMARK COMPLETE.", flush=True)
    print("=" * 80, flush=True)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
