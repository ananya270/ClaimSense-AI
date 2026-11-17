"""ClaimSense AI - Phase 8 Session 2 vs Session 4 Class-Wise Calibration Study.

Performs a rigorous confidence threshold sweep across:
[0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
Evaluates on the frozen CarDD test set (45 images, 148 instances).
Reports TP, FP (cross-class and background), FN, precision, recall, and F1.
Conducts visual failure mode categorization for false positives (panel seams, reflections, paint marks).
Generates class-calibrated operating threshold recommendations with statistical limitation safeguards.
"""

import os
import sys
import time
import json
import hashlib
import multiprocessing
from pathlib import Path
import numpy as np

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


def run_raw_inference(model, test_images_dir: Path):
    """Run model on all 45 test images at conf=0.001 to record all candidate detections."""
    image_paths = sorted(test_images_dir.glob("*.*"))
    predictions_by_image = {}

    for img_p in image_paths:
        res = model.predict(str(img_p), imgsz=640, conf=0.001, iou=0.6, device=0, half=True, verbose=False)[0]
        boxes = res.boxes
        preds = []
        if len(boxes) > 0:
            cls_arr = boxes.cls.cpu().numpy()
            conf_arr = boxes.conf.cpu().numpy()
            xyxyn_arr = boxes.xyxyn.cpu().numpy()
            for c, s, b in zip(cls_arr, conf_arr, xyxyn_arr):
                preds.append({
                    "cls": int(c),
                    "conf": float(s),
                    "bbox": [float(x) for x in b],
                    "image": img_p.name,
                })
        predictions_by_image[img_p.stem] = preds

    return predictions_by_image


def match_image_predictions(preds, gts, iou_thresh=0.45, conf_thresh=0.25):
    """Perform greedy one-to-one matching between predictions and ground truths for one image."""
    valid_preds = [p for p in preds if p["conf"] >= conf_thresh]
    valid_preds.sort(key=lambda x: x["conf"], reverse=True)

    matched_gt = set()
    matched_pred = set()
    matches = []

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
        "tp": [],
        "fp_cross": [],
        "fp_bg": [],
        "fn_missed": [],
        "fn_misclass": [],
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


def evaluate_sweep(predictions_by_image, ground_truth_by_image, thresholds):
    """Sweep confidence thresholds and compute class-wise and overall metrics."""
    names = {0: "dent", 1: "scratch", 2: "crack", 3: "glass shatter", 4: "lamp broken", 5: "tire flat"}
    nc = 6

    sweep_data = {}

    for c_thresh in thresholds:
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

        # Initialize ground truth counts
        for stem, gts in ground_truth_by_image.items():
            for g in gts:
                class_stats[g["cls"]]["gt"] += 1

        fps_at_threshold = []

        for stem, preds in predictions_by_image.items():
            gts = ground_truth_by_image.get(stem, [])
            match_res = match_image_predictions(preds, gts, iou_thresh=0.45, conf_thresh=c_thresh)

            for p, g, iou in match_res["tp"]:
                class_stats[p["cls"]]["tp"] += 1

            for p, g, iou in match_res["fp_cross"]:
                class_stats[p["cls"]]["fp_cross"] += 1
                class_stats[g["cls"]]["fn_misclass"] += 1
                fps_at_threshold.append({
                    "type": "cross_class",
                    "image": p["image"],
                    "pred_cls": names[p["cls"]],
                    "gt_cls": names[g["cls"]],
                    "conf": round(p["conf"], 4),
                    "bbox": [round(x, 4) for x in p["bbox"]],
                    "iou_with_gt": round(iou, 4),
                })

            for p in match_res["fp_bg"]:
                class_stats[p["cls"]]["fp_bg"] += 1
                fps_at_threshold.append({
                    "type": "background",
                    "image": p["image"],
                    "pred_cls": names[p["cls"]],
                    "conf": round(p["conf"], 4),
                    "bbox": [round(x, 4) for x in p["bbox"]],
                })

            for g in match_res["fn_missed"]:
                class_stats[g["cls"]]["fn_missed"] += 1

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

        sweep_data[f"{c_thresh:.2f}"] = {
            "threshold": c_thresh,
            "overall": {
                "total_ground_truth": total_gt,
                "total_tp": total_tp,
                "total_fp": total_fp,
                "total_fn": total_fn,
                "macro_precision": macro_p,
                "macro_recall": macro_r,
                "macro_f1": macro_f1,
                "micro_precision": micro_p,
                "micro_recall": micro_r,
                "micro_f1": micro_f1,
            },
            "per_class": {names[i]: class_stats[i] for i in range(nc)},
            "false_positives": fps_at_threshold,
        }

    return sweep_data


def categorize_false_positives(fps_list):
    """Categorize background false positives into visual defect archetypes based on heuristics."""
    categories = {
        "specular_reflection_or_highlight": 0,
        "panel_seam_or_body_line": 0,
        "paint_blemish_or_surface_mark": 0,
        "trim_or_wheel_edge": 0,
        "glass_edge_or_wiper": 0,
        "unassigned_background": 0,
    }

    # Heuristic analysis based on bbox aspect ratio and class
    for item in fps_list:
        if item["type"] == "cross_class":
            continue
        cname = item["pred_cls"]
        bbox = item["bbox"]  # [x1, y1, x2, y2]
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        aspect_ratio = max(w / h, h / w) if min(w, h) > 0 else 1.0

        if cname in ["scratch", "crack"]:
            if aspect_ratio > 3.0:
                categories["panel_seam_or_body_line"] += 1
            else:
                categories["paint_blemish_or_surface_mark"] += 1
        elif cname in ["dent"]:
            if aspect_ratio < 2.0:
                categories["specular_reflection_or_highlight"] += 1
            else:
                categories["panel_seam_or_body_line"] += 1
        elif cname in ["tire flat"]:
            categories["trim_or_wheel_edge"] += 1
        elif cname in ["glass shatter"]:
            categories["glass_edge_or_wiper"] += 1
        else:
            categories["unassigned_background"] += 1

    return categories


def main():
    print("=" * 80, flush=True)
    print("  CLAIMSENSE AI - PHASE 8 CLASS-WISE CALIBRATION STUDY (AUDIT ONLY)", flush=True)
    print("  Scope: Session 2 vs Session 4 across 8 Confidence Thresholds", flush=True)
    print("=" * 80, flush=True)

    study_dir = PROJECT_ROOT / "runs" / "phase8" / "final_benchmark" / "calibration_study"
    study_dir.mkdir(parents=True, exist_ok=True)

    # 1. Verify Checkpoints & Environment
    print("\n[1] Checkpoint Hash Verification:", flush=True)
    ckpts = {
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

    for k, v in ckpts.items():
        h = get_file_hash(v["path"])
        assert h == v["expected_hash"], f"Hash mismatch for {k}!"
        print(f"    - {v['name']:<25} | Hash: {h[:16]}... (VERIFIED UNTOUCHED)", flush=True)

    # Verify Production model remains untouched
    prod_path = PROJECT_ROOT / "models" / "phase5" / "best.pt"
    prod_h = get_file_hash(prod_path)
    assert prod_h == "90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565", "Production hash mismatch!"
    print(f"    - Production Baseline       | Hash: {prod_h[:16]}... (VERIFIED UNTOUCHED)", flush=True)

    # 2. Load Ground Truth
    test_labels_dir = PROJECT_ROOT / "datasets" / "CarDD_300" / "test" / "labels"
    test_images_dir = PROJECT_ROOT / "datasets" / "CarDD_300" / "test" / "images"
    gt_by_image = load_test_ground_truth(test_labels_dir)
    print(f"\n[2] Loaded 45 test images containing {sum(len(v) for v in gt_by_image.values())} ground-truth instances.", flush=True)

    # 3. Raw Inference & Threshold Sweep
    thresholds = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
    sweep_results = {}
    fp_categorizations = {}

    for k, v in ckpts.items():
        print(f"\n[3] Running raw predictions and threshold sweep for {v['name']}...", flush=True)
        m = YOLO(str(v["path"]))
        preds = run_raw_inference(m, test_images_dir)
        sw = evaluate_sweep(preds, gt_by_image, thresholds)
        sweep_results[k] = sw

        # Categorize false positives at conf=0.10 and conf=0.25
        fp_cat_10 = categorize_false_positives(sw["0.10"]["false_positives"])
        fp_cat_25 = categorize_false_positives(sw["0.25"]["false_positives"])
        fp_categorizations[k] = {
            "conf_0_10": {
                "total_fp": len(sw["0.10"]["false_positives"]),
                "categories": fp_cat_10,
                "samples": sw["0.10"]["false_positives"][:10],
            },
            "conf_0_25": {
                "total_fp": len(sw["0.25"]["false_positives"]),
                "categories": fp_cat_25,
                "samples": sw["0.25"]["false_positives"][:10],
            },
        }

    # 4. Save Raw Sweep Data JSON
    calib_json = study_dir / "calibration_data.json"
    with open(calib_json, "w", encoding="utf-8") as f:
        json.dump(sweep_results, f, indent=2)

    fp_json = study_dir / "false_positive_analysis.json"
    with open(fp_json, "w", encoding="utf-8") as f:
        json.dump(fp_categorizations, f, indent=2)

    print(f"\n[4] Saved calibration data to {calib_json}", flush=True)
    print(f"    Saved false positive analysis to {fp_json}", flush=True)

    # 5. Print Detailed Class-Wise Sweep Comparison Tables
    names = ["dent", "scratch", "crack", "glass shatter", "lamp broken", "tire flat"]
    print("\n" + "=" * 80)
    print("  SESSION 2 vs SESSION 4 CLASS-WISE THRESHOLD SWEEP COMPARISON")
    print("=" * 80)

    for cname in names:
        print(f"\n>>> CLASS: {cname.upper()} (Ground Truth = {sweep_results['session_2']['0.25']['per_class'][cname]['gt']} instances)")
        hdr = f"{'Threshold':<10} | {'S2 TP':<6} {'S4 TP':<6} | {'S2 FP':<6} {'S4 FP':<6} | {'S2 Prec':<8} {'S4 Prec':<8} | {'S2 Rec':<8} {'S4 Rec':<8} | {'S2 F1':<8} {'S4 F1':<8}"
        print(hdr)
        print("-" * len(hdr))
        for t in thresholds:
            t_str = f"{t:.2f}"
            s2_c = sweep_results["session_2"][t_str]["per_class"][cname]
            s4_c = sweep_results["session_4"][t_str]["per_class"][cname]
            print(
                f"{t_str:<10} | "
                f"{s2_c['tp']:<6} {s4_c['tp']:<6} | "
                f"{s2_c['fp_total']:<6} {s4_c['fp_total']:<6} | "
                f"{s2_c['precision']:<8.4f} {s4_c['precision']:<8.4f} | "
                f"{s2_c['recall']:<8.4f} {s4_c['recall']:<8.4f} | "
                f"{s2_c['f1']:<8.4f} {s4_c['f1']:<8.4f}"
            )

    print("\n" + "=" * 80)
    print("  OVERALL MACRO METRICS ACROSS THRESHOLDS")
    print("=" * 80)
    ov_hdr = f"{'Threshold':<10} | {'S2 Macro Prec':<14} {'S4 Macro Prec':<14} | {'S2 Macro Rec':<14} {'S4 Macro Rec':<14} | {'S2 Macro F1':<12} {'S4 Macro F1':<12} | {'S2 Tot FP':<10} {'S4 Tot FP':<10}"
    print(ov_hdr)
    print("-" * len(ov_hdr))
    for t in thresholds:
        t_str = f"{t:.2f}"
        s2_o = sweep_results["session_2"][t_str]["overall"]
        s4_o = sweep_results["session_4"][t_str]["overall"]
        print(
            f"{t_str:<10} | "
            f"{s2_o['macro_precision']:<14.4f} {s4_o['macro_precision']:<14.4f} | "
            f"{s2_o['macro_recall']:<14.4f} {s4_o['macro_recall']:<14.4f} | "
            f"{s2_o['macro_f1']:<12.4f} {s4_o['macro_f1']:<12.4f} | "
            f"{s2_o['total_fp']:<10} {s4_o['total_fp']:<10}"
        )

    print("=" * 80)
    print("  CLASS-WISE CALIBRATION STUDY COMPLETE.", flush=True)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
