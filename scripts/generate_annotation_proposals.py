"""ClaimSense AI - Generate Annotation Correction Proposals for Training Set.

Inspects all 210 training images and label files to produce:
1. Fragmented continuous scratch consolidation proposals
2. Suspicious tiny dent box review items (< 0.001 normalized area)
3. Potential missing crack annotation candidates on collision-impact panels
"""

import sys
import json
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRAIN_IMG_DIR = PROJECT_ROOT / "datasets" / "CarDD_300" / "train" / "images"
TRAIN_LBL_DIR = PROJECT_ROOT / "datasets" / "CarDD_300" / "train" / "labels"

CLASS_NAMES = {
    0: "dent",
    1: "scratch",
    2: "crack",
    3: "glass shatter",
    4: "lamp broken",
    5: "tire flat",
}


def yolo_to_xyxy(xc, yc, w, h, img_w, img_h):
    x1 = (xc - w / 2) * img_w
    y1 = (yc - h / 2) * img_h
    x2 = (xc + w / 2) * img_w
    y2 = (yc + h / 2) * img_h
    return max(0, x1), max(0, y1), min(img_w, x2), min(img_h, y2)


def xyxy_to_yolo(x1, y1, x2, y2, img_w, img_h):
    w = (x2 - x1) / img_w
    h = (y2 - y1) / img_h
    xc = (x1 + x2) / (2 * img_w)
    yc = (y1 + y2) / (2 * img_h)
    return xc, yc, w, h


def main():
    print("Scanning training dataset annotations...")
    label_files = sorted(TRAIN_LBL_DIR.glob("*.txt"))

    fragmented_scratches = []
    suspicious_tiny_dents = []
    missing_crack_candidates = []

    for lbl_path in label_files:
        stem = lbl_path.stem
        img_path = TRAIN_IMG_DIR / f"{stem}.jpg"
        if not img_path.exists():
            img_path = TRAIN_IMG_DIR / f"{stem}.png"
            if not img_path.exists():
                continue

        with Image.open(img_path) as im:
            img_w, img_h = im.size

        with open(lbl_path, "r") as f:
            lines = [l.strip() for l in f if l.strip()]

        annotations = []
        for line_idx, line in enumerate(lines):
            parts = line.split()
            if len(parts) != 5:
                continue
            cls_id = int(parts[0])
            xc, yc, bw, bh = map(float, parts[1:5])
            area = bw * bh
            pixel_w = bw * img_w
            pixel_h = bh * img_h
            annotations.append({
                "line_idx": line_idx,
                "cls_id": cls_id,
                "cls_name": CLASS_NAMES.get(cls_id, str(cls_id)),
                "yolo": [xc, yc, bw, bh],
                "area": area,
                "pixel_dims": [round(pixel_w, 1), round(pixel_h, 1)],
                "xyxy": yolo_to_xyxy(xc, yc, bw, bh, img_w, img_h),
            })

        # 1. Check for fragmented scratches
        scratch_boxes = [a for a in annotations if a["cls_id"] == 1]
        if len(scratch_boxes) >= 2:
            # Check proximity: if any pair is closer than 10% of image size or overlapping
            # Check if all scratch boxes can be merged into 1 or 2 consolidated regions
            all_x1 = min(b["xyxy"][0] for b in scratch_boxes)
            all_y1 = min(b["xyxy"][1] for b in scratch_boxes)
            all_x2 = max(b["xyxy"][2] for b in scratch_boxes)
            all_y2 = max(b["xyxy"][3] for b in scratch_boxes)
            merged_xc, merged_yc, merged_w, merged_h = xyxy_to_yolo(all_x1, all_y1, all_x2, all_y2, img_w, img_h)
            merged_area = merged_w * merged_h

            # If sum of individual box areas is a substantial portion of merged box, or if boxes are closely chain-linked
            sum_area = sum(b["area"] for b in scratch_boxes)
            density = sum_area / merged_area if merged_area > 0 else 0

            # Catalog images with >= 3 scratches or dense fragmented scrape patterns
            if len(scratch_boxes) >= 3 or (len(scratch_boxes) == 2 and density > 0.45):
                fragmented_scratches.append({
                    "image": img_path.name,
                    "resolution": [img_w, img_h],
                    "fragment_count": len(scratch_boxes),
                    "fragments": [
                        {
                            "line": b["line_idx"] + 1,
                            "yolo": [round(x, 4) for x in b["yolo"]],
                            "pixel_dims": b["pixel_dims"],
                            "area": round(b["area"], 6),
                        }
                        for b in scratch_boxes
                    ],
                    "proposed_consolidation": {
                        "yolo": [round(merged_xc, 4), round(merged_yc, 4), round(merged_w, 4), round(merged_h, 4)],
                        "pixel_dims": [round((all_x2 - all_x1), 1), round((all_y2 - all_y1), 1)],
                        "area": round(merged_area, 4),
                    },
                    "reasoning": f"Replaces {len(scratch_boxes)} fragmented slice boxes with a single unified bounding box covering the continuous damage trajectory."
                })

        # 2. Check for suspicious tiny dent boxes
        dent_boxes = [a for a in annotations if a["cls_id"] == 0]
        for b in dent_boxes:
            if b["area"] < 0.001 or b["pixel_dims"][0] < 20 or b["pixel_dims"][1] < 20:
                suspicious_tiny_dents.append({
                    "image": img_path.name,
                    "resolution": [img_w, img_h],
                    "line": b["line_idx"] + 1,
                    "yolo": [round(x, 4) for x in b["yolo"]],
                    "pixel_dims": b["pixel_dims"],
                    "area": round(b["area"], 6),
                    "action_recommendation": "Inspect for hail/gravel artifact or merge with adjacent panel dent.",
                })

        # 3. Check for potential missing crack labels in collision photos
        classes_present = {a["cls_id"] for a in annotations}
        has_dent = 0 in classes_present
        has_lamp = 4 in classes_present
        has_glass = 3 in classes_present
        has_crack = 2 in classes_present

        if (has_dent or has_lamp or has_glass) and not has_crack:
            # Check if there are large dents on bumpers/fenders
            large_dents = [a for a in annotations if a["cls_id"] == 0 and a["area"] > 0.10]
            lamps = [a for a in annotations if a["cls_id"] == 4]
            if large_dents or lamps:
                missing_crack_candidates.append({
                    "image": img_path.name,
                    "resolution": [img_w, img_h],
                    "classes_present": [CLASS_NAMES[c] for c in sorted(classes_present)],
                    "indicator": f"Severe impact: {len(large_dents)} large dent(s) and {len(lamps)} broken lamp(s). Plastic bumper seam/bracket fracture likely.",
                    "action_recommendation": "Manual human review: Inspect bumper tear-out seams and lamp mounting brackets for unannotated hairline cracks.",
                })

    out_file = PROJECT_ROOT / "runs" / "phase8" / "annotation_proposals_data.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "total_training_images": len(label_files),
            "fragmented_scratch_cases": fragmented_scratches,
            "suspicious_tiny_dent_cases": suspicious_tiny_dents,
            "missing_crack_candidate_cases": missing_crack_candidates,
        }, f, indent=2)

    print(f"\n[+] Analysis complete:")
    print(f"    - Fragmented scratch cases identified:   {len(fragmented_scratches)}")
    print(f"    - Suspicious tiny dent boxes identified: {len(suspicious_tiny_dents)}")
    print(f"    - Missing crack candidate images flagged:{len(missing_crack_candidates)}")
    print(f"    - Proposals JSON saved to: {out_file}")


if __name__ == "__main__":
    main()
