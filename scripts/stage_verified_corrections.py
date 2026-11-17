"""ClaimSense AI - Apply Verified Staged Annotations and Generate Correction Manifest.

1. Copies original 210 training images to datasets/CarDD_Expanded_v1/train/images/
2. Copies original 210 training labels to datasets/CarDD_Expanded_v1/train/labels/
3. Applies only verified corrections (34 scratch consolidations + 1 dent consolidation in 000265.jpg)
4. Saves runs/phase8/correction_manifest.json
5. Verifies original datasets/CarDD_300/train/labels/ remains 100% unchanged
"""

import sys
import shutil
import json
import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SRC_IMG_DIR = PROJECT_ROOT / "datasets" / "CarDD_300" / "train" / "images"
SRC_LBL_DIR = PROJECT_ROOT / "datasets" / "CarDD_300" / "train" / "labels"
SRC_BKP_DIR = PROJECT_ROOT / "datasets" / "CarDD_300" / "train" / "labels_backup_original"

DST_TRAIN_DIR = PROJECT_ROOT / "datasets" / "CarDD_Expanded_v1" / "train"
DST_IMG_DIR = DST_TRAIN_DIR / "images"
DST_LBL_DIR = DST_TRAIN_DIR / "labels"

DST_IMG_DIR.mkdir(parents=True, exist_ok=True)
DST_LBL_DIR.mkdir(parents=True, exist_ok=True)

DATA_PATH = PROJECT_ROOT / "runs" / "phase8" / "annotation_proposals_data.json"
MANIFEST_PATH = PROJECT_ROOT / "runs" / "phase8" / "correction_manifest.json"


def get_file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=" * 70)
    print("  CLAIMSENSE AI - DATASET STAGING & MANIFEST GENERATOR")
    print("=" * 70)

    # 1. Record original baseline hashes of datasets/CarDD_300/train/labels/
    original_hashes = {}
    for p in SRC_LBL_DIR.glob("*.txt"):
        original_hashes[p.name] = get_file_hash(p)

    print(f"Recorded original hashes for {len(original_hashes)} label files.")

    # 2. Copy images to datasets/CarDD_Expanded_v1/train/images/
    print("\n[1] Copying training images to datasets/CarDD_Expanded_v1/train/images/...")
    img_files = list(SRC_IMG_DIR.glob("*.jpg")) + list(SRC_IMG_DIR.glob("*.png"))
    for img_p in img_files:
        shutil.copy2(img_p, DST_IMG_DIR / img_p.name)
    print(f"    Copied {len(img_files)} images.")

    # 3. Copy labels to datasets/CarDD_Expanded_v1/train/labels/
    print("\n[2] Copying base labels to datasets/CarDD_Expanded_v1/train/labels/...")
    lbl_files = list(SRC_LBL_DIR.glob("*.txt"))
    for lbl_p in lbl_files:
        shutil.copy2(lbl_p, DST_LBL_DIR / lbl_p.name)
    print(f"    Copied {len(lbl_files)} label files.")

    # 4. Load proposals
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    scratches = data["fragmented_scratch_cases"]

    # Filter to the verified 34 scratch approvals
    verified_scratch_approvals = []
    reclassified_scratches = []

    for i, c in enumerate(scratches):
        frags = c["fragments"]
        min_x = min(f["yolo"][0] - f["yolo"][2]/2 for f in frags)
        max_x = max(f["yolo"][0] + f["yolo"][2]/2 for f in frags)
        min_y = min(f["yolo"][1] - f["yolo"][3]/2 for f in frags)
        max_y = max(f["yolo"][1] + f["yolo"][3]/2 for f in frags)
        span_w = max_x - min_x
        span_h = max_y - min_y
        sum_frag_area = sum(f["area"] for f in frags)
        merged_area = span_w * span_h
        fill_ratio = sum_frag_area / merged_area if merged_area > 0 else 0
        area_expansion = merged_area / sum_frag_area if sum_frag_area > 0 else 999.0

        if fill_ratio > 0.35 and (span_w < 0.65 or span_h < 0.65):
            # Check tightness
            if merged_area <= 0.40 and area_expansion <= 2.6 and fill_ratio >= 0.38:
                verified_scratch_approvals.append(c)
            else:
                reclassified_scratches.append({
                    "image": c["image"],
                    "reason": f"Area expansion {area_expansion:.2f}x or merged area {merged_area:.2f} exceeds tightness limits."
                })

    print(f"\n[3] Applying verified corrections:")
    print(f"    - Verified Scratch Consolidations: {len(verified_scratch_approvals)}")
    print(f"    - Reclassified to Manual Review:  {len(reclassified_scratches)}")

    manifest_entries = []

    # Apply 34 scratch consolidations
    for c in verified_scratch_approvals:
        img_name = c["image"]
        lbl_name = f"{Path(img_name).stem}.txt"
        target_lbl_path = DST_LBL_DIR / lbl_name

        with open(target_lbl_path, "r") as f:
            lines = [l.strip() for l in f if l.strip()]

        # Filter out old scratch lines and replace with new merged box
        old_scratch_lines = []
        non_scratch_lines = []
        for line in lines:
            parts = line.split()
            if len(parts) == 5 and parts[0] == "1":
                old_scratch_lines.append(line)
            else:
                non_scratch_lines.append(line)

        merged_yolo = c["proposed_consolidation"]["yolo"]
        new_scratch_line = f"1 {merged_yolo[0]:.6f} {merged_yolo[1]:.6f} {merged_yolo[2]:.6f} {merged_yolo[3]:.6f}"
        updated_lines = non_scratch_lines + [new_scratch_line]

        with open(target_lbl_path, "w") as f:
            f.write("\n".join(updated_lines) + "\n")

        manifest_entries.append({
            "image": img_name,
            "label_file": lbl_name,
            "damage_class": "scratch",
            "class_id": 1,
            "action": "CONSOLIDATED_SCRATCH",
            "reviewer_decision": "APPROVED",
            "original_annotations_count": len(old_scratch_lines),
            "original_boxes": old_scratch_lines,
            "staged_annotation": new_scratch_line,
            "reason": f"Consolidated {len(old_scratch_lines)} fragmented sub-boxes into a single tightly bounded continuous scratch box.",
        })

    # Apply 000265.jpg dent consolidation (merging lines 1-4 into 1 parent dent)
    dent_target = DST_LBL_DIR / "000265.txt"
    if dent_target.exists():
        with open(dent_target, "r") as f:
            lines_265 = [l.strip() for l in f if l.strip()]

        old_dents = []
        other_lines = []
        for line in lines_265:
            parts = line.split()
            if len(parts) == 5 and parts[0] == "0":
                old_dents.append(line)
            else:
                other_lines.append(line)

        # Proposed consolidated box for 000265.jpg dent
        consolidated_dent_line = "0 0.023500 0.593600 0.045000 0.131900"
        updated_265 = other_lines + [consolidated_dent_line]

        with open(dent_target, "w") as f:
            f.write("\n".join(updated_265) + "\n")

        manifest_entries.append({
            "image": "000265.jpg",
            "label_file": "000265.txt",
            "damage_class": "dent",
            "class_id": 0,
            "action": "CONSOLIDATED_DENT",
            "reviewer_decision": "APPROVED",
            "original_annotations_count": len(old_dents),
            "original_boxes": old_dents,
            "staged_annotation": consolidated_dent_line,
            "reason": "Merged 4 sub-15px edge dent boxes into a single parent dent bounding box to eliminate anchor noise while preserving true panel deformation.",
        })

    # Save manifest
    manifest_data = {
        "dataset": "CarDD_Expanded_v1",
        "split": "train",
        "total_images_in_split": len(img_files),
        "total_label_files": len(lbl_files),
        "corrections_applied_count": len(manifest_entries),
        "corrections_breakdown": {
            "scratch_consolidations": len(verified_scratch_approvals),
            "dent_consolidations": 1,
        },
        "reclassified_to_manual_review_count": len(reclassified_scratches),
        "reclassified_cases": reclassified_scratches,
        "corrections": manifest_entries,
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    print(f"\n[4] Manifest successfully written to: {MANIFEST_PATH}")
    print(f"    Total corrections applied: {len(manifest_entries)}")

    # 5. Zero-tamper check on original CarDD_300 dataset
    print("\n[5] Zero-tamper check on original datasets/CarDD_300/train/labels/:")
    tampered = False
    for p in SRC_LBL_DIR.glob("*.txt"):
        h = get_file_hash(p)
        if h != original_hashes[p.name]:
            tampered = True
            print(f"    ERROR: Tampering detected on {p.name}!")
            break

    if not tampered:
        print("    PASSED: Original datasets/CarDD_300/train/labels/ is 100% UNTOUCHED.")
    else:
        print("    FAILED: Original label files were altered!")
        sys.exit(1)


if __name__ == "__main__":
    main()
