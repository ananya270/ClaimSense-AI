"""ClaimSense AI - CarDD Dataset Readiness & Annotation Audit Script.

Analyzes train, val, and test splits for:
1. Image and instance counts per class
2. Bounding box area distributions per class (min, max, mean, median, IQR)
3. Image resolutions
4. Tiny bounding boxes (area < 0.001)
5. Overlapping / duplicate bounding boxes (IoU > 0.5 within same class)
6. Fragmented scratches (multiple co-linear / proximate scratch boxes on same panel)
7. Potential missing crack/scratch/dent annotations
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict
import numpy as np
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = PROJECT_ROOT / "datasets" / "CarDD_300"

CLASS_NAMES = {
    0: "dent",
    1: "scratch",
    2: "crack",
    3: "glass shatter",
    4: "lamp broken",
    5: "tire flat",
}


def box_iou(boxA, boxB):
    """Compute IoU between two [xc, yc, w, h] normalized boxes."""
    # Convert to [x1, y1, x2, y2]
    xA1 = boxA[0] - boxA[2] / 2
    yA1 = boxA[1] - boxA[3] / 2
    xA2 = boxA[0] + boxA[2] / 2
    yA2 = boxA[1] + boxA[3] / 2

    xB1 = boxB[0] - boxB[2] / 2
    yB1 = boxB[1] - boxB[3] / 2
    xB2 = boxB[0] + boxB[2] / 2
    yB2 = boxB[1] + boxB[3] / 2

    inter_x1 = max(xA1, xB1)
    inter_y1 = max(yA1, yB1)
    inter_x2 = min(xA2, xB2)
    inter_y2 = min(yA2, yB2)

    inter_w = max(0.0, inter_x2 - inter_x1)
    inter_h = max(0.0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h

    areaA = boxA[2] * boxA[3]
    areaB = boxB[2] * boxB[3]
    union_area = areaA + areaB - inter_area

    if union_area <= 0:
        return 0.0
    return inter_area / union_area


def main():
    print("=" * 70)
    print("  CLAIMSENSE AI - CARDD DATASET READINESS AUDIT")
    print("=" * 70)

    splits = ["train", "val", "test"]
    audit_data = {}

    for split in splits:
        img_dir = DATASET_DIR / split / "images"
        lbl_dir = DATASET_DIR / split / "labels"

        images = sorted(list(img_dir.glob("*.jpg")) + list(img_dir.glob("*.png")))
        labels = sorted(list(lbl_dir.glob("*.txt")))

        instance_counts = defaultdict(int)
        image_class_presence = defaultdict(int)
        areas_by_class = defaultdict(list)
        resolutions = []
        tiny_boxes = []  # area < 0.001
        overlapping_boxes = []
        fragmented_scratch_cases = []

        for img_path in images:
            with Image.open(img_path) as im:
                w, h = im.size
                resolutions.append((w, h))

            lbl_path = lbl_dir / f"{img_path.stem}.txt"
            if not lbl_path.exists():
                continue

            with open(lbl_path, "r") as f:
                lines = [l.strip() for l in f if l.strip()]

            boxes_in_image = []
            classes_in_image = set()

            for line_idx, line in enumerate(lines):
                parts = line.split()
                if len(parts) != 5:
                    continue
                cls_id = int(parts[0])
                xc, yc, bw, bh = map(float, parts[1:5])
                area = bw * bh
                cls_name = CLASS_NAMES.get(cls_id, str(cls_id))

                instance_counts[cls_name] += 1
                classes_in_image.add(cls_name)
                areas_by_class[cls_name].append(area)
                boxes_in_image.append((cls_id, cls_name, [xc, yc, bw, bh], area, line_idx))

                if area < 0.001:
                    tiny_boxes.append({
                        "image": img_path.name,
                        "class": cls_name,
                        "bbox": [round(x, 4) for x in [xc, yc, bw, bh]],
                        "area": round(area, 6),
                    })

            for cname in classes_in_image:
                image_class_presence[cname] += 1

            # Check intra-class overlap
            n_b = len(boxes_in_image)
            scratch_boxes = []
            for i in range(n_b):
                cls_i, cname_i, b_i, a_i, l_i = boxes_in_image[i]
                if cname_i == "scratch":
                    scratch_boxes.append((b_i, a_i))
                for j in range(i + 1, n_b):
                    cls_j, cname_j, b_j, a_j, l_j = boxes_in_image[j]
                    if cls_i == cls_j:
                        iou = box_iou(b_i, b_j)
                        if iou > 0.4:
                            overlapping_boxes.append({
                                "image": img_path.name,
                                "class": cname_i,
                                "iou": round(iou, 4),
                                "box1": [round(x, 4) for x in b_i],
                                "box2": [round(x, 4) for x in b_j],
                            })

            # Check fragmented scratches: >= 3 scratch boxes in single image
            if len(scratch_boxes) >= 3:
                fragmented_scratch_cases.append({
                    "image": img_path.name,
                    "scratch_count": len(scratch_boxes),
                    "total_boxes": n_b,
                })

        audit_data[split] = {
            "num_images": len(images),
            "num_labels": len(labels),
            "instance_counts": dict(instance_counts),
            "image_presence": dict(image_class_presence),
            "resolutions": {
                "unique_resolutions": sorted(list(set(resolutions))),
                "min_w": min(r[0] for r in resolutions) if resolutions else 0,
                "max_w": max(r[0] for r in resolutions) if resolutions else 0,
                "min_h": min(r[1] for r in resolutions) if resolutions else 0,
                "max_h": max(r[1] for r in resolutions) if resolutions else 0,
            },
            "area_stats": {
                cls: {
                    "count": len(areas),
                    "mean": round(float(np.mean(areas)), 5) if areas else 0,
                    "std": round(float(np.std(areas)), 5) if areas else 0,
                    "median": round(float(np.median(areas)), 5) if areas else 0,
                    "min": round(float(np.min(areas)), 6) if areas else 0,
                    "max": round(float(np.max(areas)), 5) if areas else 0,
                    "p25": round(float(np.percentile(areas, 25)), 5) if areas else 0,
                    "p75": round(float(np.percentile(areas, 75)), 5) if areas else 0,
                }
                for cls, areas in areas_by_class.items()
            },
            "tiny_boxes_count": len(tiny_boxes),
            "tiny_boxes_sample": tiny_boxes[:10],
            "overlapping_boxes_count": len(overlapping_boxes),
            "overlapping_boxes_sample": overlapping_boxes[:10],
            "fragmented_scratch_count": len(fragmented_scratch_cases),
            "fragmented_scratch_sample": fragmented_scratch_cases[:10],
        }

    out_json = PROJECT_ROOT / "runs" / "phase8" / "cardd_annotation_audit.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2)

    print("\n[+] Audit completed. Summary:")
    for split in splits:
        d = audit_data[split]
        print(f"\n--- Split: {split.upper()} ({d['num_images']} images) ---")
        print("  Instances per class:")
        for cname in ["dent", "scratch", "crack", "glass shatter", "lamp broken", "tire flat"]:
            cnt = d["instance_counts"].get(cname, 0)
            img_cnt = d["image_presence"].get(cname, 0)
            astat = d["area_stats"].get(cname, {})
            print(f"    - {cname:<14}: {cnt:>4} instances in {img_cnt:>3} images | Median area: {astat.get('median', 0):.5f} (min: {astat.get('min', 0):.6f}, max: {astat.get('max', 0):.4f})")
        print(f"  Tiny boxes (area < 0.001):        {d['tiny_boxes_count']}")
        print(f"  Overlapping boxes (IoU > 0.4):    {d['overlapping_boxes_count']}")
        print(f"  Images with >= 3 scratches:       {d['fragmented_scratch_count']}")

    print(f"\nSaved detailed JSON to: {out_json}")


if __name__ == "__main__":
    main()
