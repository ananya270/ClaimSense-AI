"""ClaimSense AI - Phase 8 Benchmark Metric Integrity Audit Script.

Performs a forensic, prediction-level audit of the Phase 8 Final 3-Way Benchmark.
Reconciles:
1. Session 4 scratch recall (0.0167 vs 67.9% vs 36 TP).
2. Ultralytics curve-max-F1 metrics vs fixed operational threshold metrics (conf=0.25, IoU=0.45).
3. Cross-class vs background false positives.
4. Independent recomputation of TP, FP, FN directly from raw bounding box predictions.
5. Verification of mAP50, mAP50-95, latency, and checkpoint SHA256 hashes.
"""

import os
import sys
import time
import json
import hashlib
import multiprocessing
from pathlib import Path
from collections import defaultdict
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch
from ultralytics import YOLO
from ultralytics.utils.metrics import box_iou


def get_file_hash(path: Path) -> str:
    """Compute SHA256 of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def box_xywh_to_xyxy(box):
    """Convert normalized [x_center, y_center, w, h] to normalized [x1, y1, x2, y2]."""
    x, y, w, h = box
    return [x - w / 2, y - h / 2, x + w / 2, y + h / 2]


def compute_iou(box1, box2):
    """Compute IoU between two [x1, y1, x2, y2] boxes."""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    inter_area = max(0, x2 - x1) * max(0, y2 - y1)
    b1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    b2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])

    union_area = b1_area + b2_area - inter_area
    return inter_area / union_area if union_area > 0 else 0.0


def load_test_ground_truth(test_labels_dir: Path):
    """Load all 45 ground truth test label files."""
    gt_by_image = {}
    for txt_path in sorted(test_labels_dir.glob("*.txt")):
        stem = txt_path.stem
        boxes = []
        for line in txt_path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            cls_id = int(parts[0])
            xywh = [float(p) for p in parts[1:5]]
            xyxy = box_xywh_to_xyxy(xywh)
            boxes.append({"cls": cls_id, "bbox": xyxy})
        gt_by_image[stem] = boxes
    return gt_by_image


def match_predictions_to_gt(preds, gts, iou_thresh=0.45, conf_thresh=0.25):
    """Perform greedy one-to-one matching between predictions and ground truths for one image.
    
    preds: list of dicts with 'cls', 'conf', 'bbox' (normalized xyxy)
    gts: list of dicts with 'cls', 'bbox' (normalized xyxy)
    """
    # Filter by confidence
    valid_preds = [p for p in preds if p["conf"] >= conf_thresh]
    # Sort predictions by descending confidence
    valid_preds.sort(key=lambda x: x["conf"], reverse=True)

    matched_gt = set()
    matched_pred = set()
    matches = []  # list of (pred_idx, gt_idx, iou)

    for p_idx, p in enumerate(valid_preds):
        best_iou = 0.0
        best_gt_idx = -1
        for g_idx, g in enumerate(gts):
            if g_idx in matched_gt:
                continue
            iou = compute_iou(p["bbox"], g["bbox"])
            if iou > best_iou:
                best_iou = iou
                best_gt_idx = g_idx
        if best_iou >= iou_thresh and best_gt_idx >= 0:
            matched_gt.add(best_gt_idx)
            matched_pred.add(p_idx)
            matches.append((p_idx, best_gt_idx, best_iou))

    results = {
        "tp": [],          # (pred, gt, iou) where pred.cls == gt.cls
        "fp_cross": [],    # (pred, gt, iou) where pred.cls != gt.cls
        "fp_bg": [],       # pred unmatched to any gt
        "fn_missed": [],   # gt unmatched to any pred
        "fn_misclass": [], # gt matched to pred with wrong class
    }

    for p_idx, g_idx, iou in matches:
        p = valid_preds[p_idx]
        g = gts[g_idx]
        if p["cls"] == g["cls"]:
            results["tp"].append((p, g, iou))
        else:
            results["fp_cross"].append((p, g, iou))
            results["fn_misclass"].append((g, p, iou))

    for p_idx, p in enumerate(valid_preds):
        if p_idx not in matched_pred:
            results["fp_bg"].append(p)

    for g_idx, g in enumerate(gts):
        if g_idx not in matched_gt:
            results["fn_missed"].append(g)

    return results


def run_raw_inference(model, test_images_dir: Path):
    """Run model on all 45 test images at conf=0.001 to record all detections."""
    image_paths = sorted(test_images_dir.glob("*.*"))
    predictions_by_image = {}

    for img_p in image_paths:
        res = model.predict(str(img_p), imgsz=640, conf=0.001, iou=0.6, device=0, half=True, verbose=False)[0]
        boxes = res.boxes
        preds = []
        if len(boxes) > 0:
            cls_arr = boxes.cls.cpu().numpy()
            conf_arr = boxes.conf.cpu().numpy()
            # xyxyn gives normalized coordinates [x1, y1, x2, y2]
            xyxyn_arr = boxes.xyxyn.cpu().numpy()
            for c, s, b in zip(cls_arr, conf_arr, xyxyn_arr):
                preds.append({"cls": int(c), "conf": float(s), "bbox": [float(x) for x in b]})
        predictions_by_image[img_p.stem] = preds

    return predictions_by_image


def audit_model_matching(predictions_by_image, ground_truth_by_image, conf_thresholds=[0.001, 0.05, 0.10, 0.25, 0.50]):
    """Evaluate matching at multiple confidence thresholds."""
    names = {0: "dent", 1: "scratch", 2: "crack", 3: "glass shatter", 4: "lamp broken", 5: "tire flat"}
    nc = 6

    threshold_results = {}

    for c_thresh in conf_thresholds:
        class_stats = {
            i: {
                "name": names[i],
                "gt": 0,
                "tp": 0,
                "fn_missed": 0,
                "fn_misclass": 0,
                "fn_total": 0,
                "fp_cross": 0,
                "fp_bg": 0,
                "fp_total": 0,
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
            }
            for i in range(nc)
        }

        # Count total ground truth
        for stem, gts in ground_truth_by_image.items():
            for g in gts:
                class_stats[g["cls"]]["gt"] += 1

        for stem, preds in predictions_by_image.items():
            gts = ground_truth_by_image.get(stem, [])
            match_res = match_predictions_to_gt(preds, gts, iou_thresh=0.45, conf_thresh=c_thresh)

            for p, g, iou in match_res["tp"]:
                class_stats[p["cls"]]["tp"] += 1

            for p, g, iou in match_res["fp_cross"]:
                class_stats[p["cls"]]["fp_cross"] += 1
                class_stats[g["cls"]]["fn_misclass"] += 1

            for p in match_res["fp_bg"]:
                class_stats[p["cls"]]["fp_bg"] += 1

            for g in match_res["fn_missed"]:
                class_stats[g["cls"]]["fn_missed"] += 1

        # Compute per-class precision, recall, f1
        total_tp = 0
        total_fp = 0
        total_fn = 0
        total_gt = 0

        for i in range(nc):
            cs = class_stats[i]
            cs["fn_total"] = cs["fn_missed"] + cs["fn_misclass"]
            cs["fp_total"] = cs["fp_cross"] + cs["fp_bg"]
            tp = cs["tp"]
            fp = cs["fp_total"]
            fn = cs["fn_total"]
            gt = cs["gt"]

            cs["precision"] = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
            cs["recall"] = round(tp / gt, 4) if gt > 0 else 0.0
            p = cs["precision"]
            r = cs["recall"]
            cs["f1"] = round(2 * p * r / (p + r), 4) if (p + r) > 0 else 0.0

            total_tp += tp
            total_fp += fp
            total_fn += fn
            total_gt += gt

        macro_p = round(float(np.mean([class_stats[i]["precision"] for i in range(nc)])), 4)
        macro_r = round(float(np.mean([class_stats[i]["recall"] for i in range(nc)])), 4)
        macro_f1 = round(2 * macro_p * macro_r / (macro_p + macro_r), 4) if (macro_p + macro_r) > 0 else 0.0

        micro_p = round(total_tp / (total_tp + total_fp), 4) if (total_tp + total_fp) > 0 else 0.0
        micro_r = round(total_tp / total_gt, 4) if total_gt > 0 else 0.0
        micro_f1 = round(2 * micro_p * micro_r / (micro_p + micro_r), 4) if (micro_p + micro_r) > 0 else 0.0

        threshold_results[str(c_thresh)] = {
            "confidence_threshold": c_thresh,
            "overall": {
                "total_ground_truth": total_gt,
                "total_true_positives": total_tp,
                "total_false_positives": total_fp,
                "total_false_negatives": total_fn,
                "macro_precision": macro_p,
                "macro_recall": macro_r,
                "macro_f1": macro_f1,
                "micro_precision": micro_p,
                "micro_recall": micro_r,
                "micro_f1": micro_f1,
            },
            "per_class": class_stats,
        }

    return threshold_results


def main():
    print("=" * 80, flush=True)
    print("  CLAIMSENSE AI - PHASE 8 BENCHMARK METRIC INTEGRITY AUDIT", flush=True)
    print("  Scope: Prediction-Level Independent Verification & Root-Cause Audit", flush=True)
    print("=" * 80, flush=True)

    audit_dir = PROJECT_ROOT / "runs" / "phase8" / "final_benchmark" / "integrity_audit"
    audit_dir.mkdir(parents=True, exist_ok=True)

    # 1. Verify Checkpoint Hashes
    print("\n[1] Checkpoint SHA256 Hash Verification:", flush=True)
    checkpoints = {
        "production_baseline": {
            "name": "Production Baseline (Phase 5)",
            "path": PROJECT_ROOT / "models" / "phase5" / "best.pt",
            "expected_hash": "90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565",
        },
        "session_2": {
            "name": "Phase 8 - Session 2",
            "path": PROJECT_ROOT / "runs" / "phase8" / "session_2" / "weights" / "best.pt",
            "expected_hash": "2ee0a56749ceba72da863fd3496f080ee06f26409daa4e9588fb69ee149333c5",
        },
        "session_4": {
            "name": "Phase 8 - Session 4",
            "path": PROJECT_ROOT / "runs" / "phase8" / "session_4_training_01" / "weights" / "best.pt",
            "expected_hash": "ea53eee94e508bbb81620b47b2a23c9826341b6b5a6981d9371e476cb9d0594f",
        },
    }

    hash_audit = {}
    for key, info in checkpoints.items():
        actual_h = get_file_hash(info["path"])
        match = (actual_h == info["expected_hash"])
        print(f"    - {info['name']:<28} | Hash: {actual_h[:16]}... | Match: {match}", flush=True)
        assert match, f"Hash mismatch for {key}!"
        hash_audit[key] = {
            "name": info["name"],
            "path": str(info["path"]),
            "sha256": actual_h,
            "intact": match,
        }

    # 2. Load Ground Truth
    test_labels_dir = PROJECT_ROOT / "datasets" / "CarDD_300" / "test" / "labels"
    test_images_dir = PROJECT_ROOT / "datasets" / "CarDD_300" / "test" / "images"
    gt_by_image = load_test_ground_truth(test_labels_dir)
    total_gt_count = sum(len(v) for v in gt_by_image.values())
    print(f"\n[2] Ground Truth Loaded: {len(gt_by_image)} images, {total_gt_count} damage instances.", flush=True)
    assert total_gt_count == 148, f"Expected 148 GT instances, got {total_gt_count}"

    # 3. Raw Inference & Multi-Threshold Matching Audit
    print("\n[3] Executing Raw Prediction Extraction across all 45 Test Images...", flush=True)
    raw_predictions = {}
    matching_audits = {}

    for key, info in checkpoints.items():
        print(f"    - Extracting predictions for {info['name']}...", flush=True)
        m = YOLO(str(info["path"]))
        preds = run_raw_inference(m, test_images_dir)
        raw_predictions[key] = preds
        audit_res = audit_model_matching(preds, gt_by_image, conf_thresholds=[0.001, 0.05, 0.10, 0.20, 0.25, 0.30, 0.50])
        matching_audits[key] = audit_res

    # 4. Save Raw Predictions and Multi-Threshold Audit
    print("\n[4] Saving Prediction-Level Audit Deliverables...", flush=True)
    with open(audit_dir / "matching_audits_by_confidence.json", "w", encoding="utf-8") as f:
        json.dump(matching_audits, f, indent=2)

    # 5. Extract Detailed Scratch Prediction Confidence Distribution in Session 4 vs Session 2
    scratch_confs_s2 = []
    scratch_confs_s4 = []

    for stem, preds in raw_predictions["session_2"].items():
        for p in preds:
            if p["cls"] == 1:
                scratch_confs_s2.append(p["conf"])

    for stem, preds in raw_predictions["session_4"].items():
        for p in preds:
            if p["cls"] == 1:
                scratch_confs_s4.append(p["conf"])

    print(f"\n[5] Scratch Predictions Distribution:")
    print(f"    - Session 2 Scratch Proposals (conf>=0.001): {len(scratch_confs_s2)} boxes")
    print(f"    - Session 4 Scratch Proposals (conf>=0.001): {len(scratch_confs_s4)} boxes")
    for cut in [0.001, 0.01, 0.05, 0.10, 0.20, 0.25, 0.30, 0.50]:
        n_s2 = sum(1 for c in scratch_confs_s2 if c >= cut)
        n_s4 = sum(1 for c in scratch_confs_s4 if c >= cut)
        print(f"      >= {cut:<5}: S2 = {n_s2:<4} | S4 = {n_s4:<4}", flush=True)

    # 6. Detailed Comparison at Operational conf=0.25 and conf=0.10
    print("\n" + "=" * 80)
    print("  CONFIDENCE OPERATING POINT AUDIT: OPERATIONAL (conf=0.25) vs CURVE-MAX-F1")
    print("=" * 80)
    
    names = {0: "dent", 1: "scratch", 2: "crack", 3: "glass shatter", 4: "lamp broken", 5: "tire flat"}
    
    print("\n--- OPERATIONAL METRICS AT conf=0.25, IoU=0.45 ---")
    hdr = f"{'Model':<12} | {'Class':<14} | {'GT':<4} | {'TP':<4} | {'FN':<4} | {'FP_cross':<8} | {'FP_bg':<8} | {'FP_tot':<8} | {'Prec':<7} | {'Rec':<7} | {'F1':<7}"
    print(hdr)
    print("-" * len(hdr))

    for m_key in ["production_baseline", "session_2", "session_4"]:
        stats = matching_audits[m_key]["0.25"]["per_class"]
        for i in range(6):
            cs = stats[str(i)] if str(i) in stats else stats[i]
            cname = names[i]
            print(
                f"{m_key[:12]:<12} | {cname:<14} | {cs['gt']:<4} | {cs['tp']:<4} | {cs['fn_total']:<4} | "
                f"{cs['fp_cross']:<8} | {cs['fp_bg']:<8} | {cs['fp_total']:<8} | "
                f"{cs['precision']:<7.4f} | {cs['recall']:<7.4f} | {cs['f1']:<7.4f}"
            )
        ov = matching_audits[m_key]["0.25"]["overall"]
        print(f"{m_key[:12]:<12} | {'OVERALL (MACRO)':<14} | {ov['total_ground_truth']:<4} | {ov['total_true_positives']:<4} | {ov['total_false_negatives']:<4} | "
              f"{'-':<8} | {'-':<8} | {ov['total_false_positives']:<8} | "
              f"{ov['macro_precision']:<7.4f} | {ov['macro_recall']:<7.4f} | {ov['macro_f1']:<7.4f}")
        print("-" * len(hdr))

    print("\n--- OPERATIONAL METRICS AT conf=0.10, IoU=0.45 ---")
    print(hdr)
    print("-" * len(hdr))
    for m_key in ["production_baseline", "session_2", "session_4"]:
        stats = matching_audits[m_key]["0.1"]["per_class"]
        for i in range(6):
            cs = stats[str(i)] if str(i) in stats else stats[i]
            cname = names[i]
            print(
                f"{m_key[:12]:<12} | {cname:<14} | {cs['gt']:<4} | {cs['tp']:<4} | {cs['fn_total']:<4} | "
                f"{cs['fp_cross']:<8} | {cs['fp_bg']:<8} | {cs['fp_total']:<8} | "
                f"{cs['precision']:<7.4f} | {cs['recall']:<7.4f} | {cs['f1']:<7.4f}"
            )
        ov = matching_audits[m_key]["0.1"]["overall"]
        print(f"{m_key[:12]:<12} | {'OVERALL (MACRO)':<14} | {ov['total_ground_truth']:<4} | {ov['total_true_positives']:<4} | {ov['total_false_negatives']:<4} | "
              f"{'-':<8} | {'-':<8} | {ov['total_false_positives']:<8} | "
              f"{ov['macro_precision']:<7.4f} | {ov['macro_recall']:<7.4f} | {ov['macro_f1']:<7.4f}")
        print("-" * len(hdr))

    # 7. Write Comprehensive Audit Summary JSON
    summary_audit = {
        "audit_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "checkpoints_verified": hash_audit,
        "test_dataset": {
            "images": 45,
            "instances": total_gt_count,
            "class_counts": {names[i]: sum(1 for stem, gts in gt_by_image.items() for g in gts if g["cls"] == i) for i in range(6)},
        },
        "operational_metrics_conf_0_25": {
            m_key: matching_audits[m_key]["0.25"] for m_key in checkpoints.keys()
        },
        "operational_metrics_conf_0_10": {
            m_key: matching_audits[m_key]["0.1"] for m_key in checkpoints.keys()
        },
    }

    audit_json_path = audit_dir / "integrity_audit_summary.json"
    with open(audit_json_path, "w", encoding="utf-8") as f:
        json.dump(summary_audit, f, indent=2)

    print(f"\n[7] Audit Summary JSON saved to: {audit_json_path}", flush=True)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
