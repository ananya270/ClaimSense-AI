"""Detailed error case analysis for dent, scratch, and crack."""

import json
from pathlib import Path
from PIL import Image
import numpy as np
from ultralytics import YOLO

model = YOLO("runs/phase8/session_2/weights/best.pt")
test_img_dir = Path("datasets/CarDD_300/test/images")
test_lbl_dir = Path("datasets/CarDD_300/test/labels")

target_classes = {0: "dent", 1: "scratch", 2: "crack"}

fn_cases = {c: [] for c in target_classes.values()}
fp_cases = {c: [] for c in target_classes.values()}
tp_cases = {c: [] for c in target_classes.values()}
box_sizes = {c: [] for c in target_classes.values()}

def calc_iou(b1, b2):
    x1_a, y1_a, x2_a, y2_a = b1[0]-b1[2]/2, b1[1]-b1[3]/2, b1[0]+b1[2]/2, b1[1]+b1[3]/2
    x1_b, y1_b, x2_b, y2_b = b2[0]-b2[2]/2, b2[1]-b2[3]/2, b2[0]+b2[2]/2, b2[1]+b2[3]/2
    inter_x1, inter_y1 = max(x1_a, x1_b), max(y1_a, y1_b)
    inter_x2, inter_y2 = min(x2_a, x2_b), min(y2_a, y2_b)
    if inter_x2 < inter_x1 or inter_y2 < inter_y1:
        return 0.0
    inter = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
    union = (b1[2]*b1[3]) + (b2[2]*b2[3]) - inter
    return inter / union if union > 0 else 0.0

for img_p in sorted(test_img_dir.glob("*.jpg")):
    lbl_p = test_lbl_dir / f"{img_p.stem}.txt"
    gt_boxes = []
    if lbl_p.exists():
        with open(lbl_p) as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue
                c_id = int(parts[0])
                coords = [float(x) for x in parts[1:5]]
                gt_boxes.append((c_id, coords))
                if c_id in target_classes:
                    box_sizes[target_classes[c_id]].append(coords[2] * coords[3])

    res = model.predict(str(img_p), device=0, imgsz=640, conf=0.25, verbose=False)[0]
    pred_boxes = []
    if res.boxes is not None and len(res.boxes) > 0:
        for b in res.boxes:
            c_id = int(b.cls[0].item())
            conf = float(b.conf[0].item())
            xywhn = b.xywhn[0].tolist()
            pred_boxes.append((c_id, conf, xywhn))

    matched_gt = set()
    matched_pred = set()

    for g_idx, (g_cls, g_coords) in enumerate(gt_boxes):
        if g_cls not in target_classes:
            continue
        c_name = target_classes[g_cls]
        best_iou = 0.0
        best_p_idx = -1
        for p_idx, (p_cls, p_conf, p_coords) in enumerate(pred_boxes):
            if p_idx in matched_pred or p_cls != g_cls:
                continue
            sim = calc_iou(g_coords, p_coords)
            if sim > best_iou:
                best_iou = sim
                best_p_idx = p_idx
        if best_iou >= 0.3:
            matched_gt.add(g_idx)
            matched_pred.add(best_p_idx)
            tp_cases[c_name].append({
                "image": img_p.name,
                "iou": round(best_iou, 3),
                "conf": round(pred_boxes[best_p_idx][1], 3),
                "gt_box": [round(x, 4) for x in g_coords]
            })
        else:
            fn_cases[c_name].append({
                "image": img_p.name,
                "gt_box": [round(x, 4) for x in g_coords],
                "area": round(g_coords[2] * g_coords[3], 5)
            })

    for p_idx, (p_cls, p_conf, p_coords) in enumerate(pred_boxes):
        if p_cls in target_classes and p_idx not in matched_pred:
            fp_cases[target_classes[p_cls]].append({
                "image": img_p.name,
                "conf": round(p_conf, 3),
                "pred_box": [round(x, 4) for x in p_coords],
                "area": round(p_coords[2] * p_coords[3], 5)
            })

print("=== ERROR QUANTIFICATION (conf=0.25, IoU=0.3) ===")
for c in target_classes.values():
    areas = box_sizes[c]
    mean_area = np.mean(areas) if areas else 0
    median_area = np.median(areas) if areas else 0
    print(f"\nClass: {c}")
    print(f"  True Positives:  {len(tp_cases[c])}")
    print(f"  False Negatives: {len(fn_cases[c])}")
    print(f"  False Positives: {len(fp_cases[c])}")
    print(f"  GT Box Area (Mean / Median): {mean_area:.5f} / {median_area:.5f}")
    if fn_cases[c]:
        fn_imgs = [x["image"] for x in fn_cases[c][:5]]
        print(f"  Sample FN images: {fn_imgs}")
    if fp_cases[c]:
        fp_imgs = [f"{x['image']} (conf={x['conf']})" for x in fp_cases[c][:5]]
        print(f"  Sample FP images: {fp_imgs}")

# Dump detailed error analysis to file
analysis_out = Path("runs/phase8/post_benchmark_analysis")
analysis_out.mkdir(parents=True, exist_ok=True)
with open(analysis_out / "error_cases_raw.json", "w") as f:
    json.dump({
        "box_size_distribution": {
            c: {
                "count": len(box_sizes[c]),
                "mean_area": float(np.mean(box_sizes[c])) if box_sizes[c] else 0.0,
                "median_area": float(np.median(box_sizes[c])) if box_sizes[c] else 0.0,
                "min_area": float(np.min(box_sizes[c])) if box_sizes[c] else 0.0,
                "max_area": float(np.max(box_sizes[c])) if box_sizes[c] else 0.0,
            }
            for c in target_classes.values()
        },
        "true_positives": tp_cases,
        "false_negatives": fn_cases,
        "false_positives": fp_cases,
    }, f, indent=2)

print("\nRaw error analysis written to runs/phase8/post_benchmark_analysis/error_cases_raw.json")
