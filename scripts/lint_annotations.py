"""ClaimSense AI - Annotation Linter & Quality Assurance Validator.

Validates YOLO format annotations against Phase 8 Standard Guidelines:
1. Coordinate boundaries (0.0 <= x, y, w, h <= 1.0)
2. Valid class indices (0 to 5)
3. Minimum box dimensions (>= 16px native width and height)
4. Same-class overlapping bounding boxes (IoU > 0.35)
5. Aspect ratio anomalies (> 20:1)
"""

import sys
import json
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent

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


def lint_label_file(lbl_path: Path, img_path: Path):
    """Lints a single label file against image dimensions."""
    errors = []
    warnings = []

    if not lbl_path.exists():
        return errors, warnings

    with Image.open(img_path) as im:
        img_w, img_h = im.size

    with open(lbl_path, "r") as f:
        lines = [l.strip() for l in f if l.strip()]

    boxes = []
    for line_idx, line in enumerate(lines):
        parts = line.split()
        if len(parts) != 5:
            errors.append(f"Line {line_idx+1}: Invalid column count ({len(parts)} != 5)")
            continue

        try:
            cls_id = int(parts[0])
            xc, yc, bw, bh = map(float, parts[1:5])
        except ValueError:
            errors.append(f"Line {line_idx+1}: Non-numeric values in line")
            continue

        # Class ID check
        if cls_id not in CLASS_NAMES:
            errors.append(f"Line {line_idx+1}: Invalid class ID {cls_id} (allowed 0-5)")

        # Coordinate boundary check
        if not (0.0 <= xc <= 1.0 and 0.0 <= yc <= 1.0 and 0.0 < bw <= 1.0 and 0.0 < bh <= 1.0):
            errors.append(f"Line {line_idx+1}: Coordinates out of [0, 1] range: {[xc, yc, bw, bh]}")

        # Check box corners inside image
        x1 = xc - bw / 2
        y1 = yc - bh / 2
        x2 = xc + bw / 2
        y2 = yc + bh / 2
        if x1 < -0.01 or y1 < -0.01 or x2 > 1.01 or y2 > 1.01:
            warnings.append(f"Line {line_idx+1}: Box extends significantly outside image frame: [{x1:.3f}, {y1:.3f}, {x2:.3f}, {y2:.3f}]")

        # Pixel dimension check (< 16px)
        px_w = bw * img_w
        px_h = bh * img_h
        if px_w < 16.0 or px_h < 16.0:
            warnings.append(f"Line {line_idx+1} ({CLASS_NAMES.get(cls_id, cls_id)}): Sub-16px dimension ({px_w:.1f}x{px_h:.1f} px). Violates minimum scale guideline.")

        # Aspect ratio check (> 20:1)
        if bw > 0 and bh > 0:
            aspect = max(bw / bh, bh / bw)
            if aspect > 20.0 and cls_id != 1:  # Allow scratches
                warnings.append(f"Line {line_idx+1} ({CLASS_NAMES.get(cls_id, cls_id)}): Extreme aspect ratio ({aspect:.1f}:1). Check for line-artifact error.")

        boxes.append((cls_id, [xc, yc, bw, bh], line_idx + 1))

    # Overlapping boxes check
    n = len(boxes)
    for i in range(n):
        for j in range(i + 1, n):
            c_i, b_i, l_i = boxes[i]
            c_j, b_j, l_j = boxes[j]
            if c_i == c_j:
                iou = box_iou(b_i, b_j)
                if iou > 0.35:
                    warnings.append(f"Lines {l_i} & {l_j} ({CLASS_NAMES.get(c_i, c_i)}): High same-class overlap (IoU={iou:.3f} > 0.35). Consider consolidating.")

    return errors, warnings


def main():
    print("==========================================================")
    print("  CLAIMSENSE AI - ANNOTATION LINTER & INTEGRITY AUDITOR")
    print("==========================================================")

    if len(sys.argv) > 1:
        target_dir = Path(sys.argv[1]).resolve()
    else:
        target_dir = PROJECT_ROOT / "datasets" / "CarDD_300" / "train"

    img_dir = target_dir / "images"
    lbl_dir = target_dir / "labels"

    print(f"Target Directory: {target_dir}")
    print(f"Image Directory:  {img_dir}")
    print(f"Label Directory:  {lbl_dir}")

    all_errors = 0
    all_warnings = 0
    flagged_files = 0
    detailed_reports = []

    lbl_files = sorted(lbl_dir.glob("*.txt"))
    for lbl_path in lbl_files:
        img_path = img_dir / f"{lbl_path.stem}.jpg"
        if not img_path.exists():
            img_path = img_dir / f"{lbl_path.stem}.png"
            if not img_path.exists():
                continue

        errors, warnings = lint_label_file(lbl_path, img_path)
        if errors or warnings:
            flagged_files += 1
            all_errors += len(errors)
            all_warnings += len(warnings)
            detailed_reports.append({
                "file": lbl_path.name,
                "errors": errors,
                "warnings": warnings,
            })

    print(f"\nLinting completed on {len(lbl_files)} training label files:")
    print(f"  - Files with warnings/errors: {flagged_files}")
    print(f"  - Total syntax errors:        {all_errors} (Hard failures)")
    print(f"  - Total guideline warnings:   {all_warnings} (Sub-16px, aspect ratio, overlap)")
    print(f"  - Validation Status:          {'PASSED (0 Syntax Errors)' if all_errors == 0 else 'FAILED'}")

    return {
        "target_dir": str(target_dir),
        "total_files": len(lbl_files),
        "flagged_files": flagged_files,
        "total_errors": all_errors,
        "total_warnings": all_warnings,
        "detailed_reports": detailed_reports,
    }


if __name__ == "__main__":
    main()
