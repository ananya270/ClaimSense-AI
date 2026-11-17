"""Phase 8: Integrate 100 verified CarDD images and labels into CarDD_Expanded_v1/train."""

import json
import shutil
import hashlib
from pathlib import Path
from collections import Counter
from datetime import datetime
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_INCOMING = PROJECT_ROOT / "datasets" / "CarDD_Expanded_v1" / "raw_incoming"
ANNOTATIONS_PILOT = PROJECT_ROOT / "datasets" / "CarDD_Expanded_v1" / "annotations_pilot"

TRAIN_IMG_DIR = PROJECT_ROOT / "datasets" / "CarDD_Expanded_v1" / "train" / "images"
TRAIN_LBL_DIR = PROJECT_ROOT / "datasets" / "CarDD_Expanded_v1" / "train" / "labels"
VAL_IMG_DIR = PROJECT_ROOT / "datasets" / "CarDD_Expanded_v1" / "val" / "images"
VAL_LBL_DIR = PROJECT_ROOT / "datasets" / "CarDD_Expanded_v1" / "val" / "labels"
TEST_IMG_DIR = PROJECT_ROOT / "datasets" / "CarDD_300" / "test" / "images"
TEST_LBL_DIR = PROJECT_ROOT / "datasets" / "CarDD_300" / "test" / "labels"

MANIFEST_OUT = PROJECT_ROOT / "runs" / "phase8" / "integration_manifest.json"
DISTRIBUTION_OUT = PROJECT_ROOT / "runs" / "phase8" / "final_class_distribution.json"

CLASS_NAMES = {
    0: "dent",
    1: "scratch",
    2: "crack",
    3: "glass shatter",
    4: "lamp broken",
    5: "tire flat",
}

print("=== 1. PRE-INTEGRATION AUDIT ===")

incoming_imgs = sorted(RAW_INCOMING.glob("*.jpg"))
incoming_lbls = sorted(ANNOTATIONS_PILOT.glob("*.txt"))

assert len(incoming_imgs) == 100, f"Expected 100 incoming images, found {len(incoming_imgs)}"
assert len(incoming_lbls) == 100, f"Expected 100 incoming labels, found {len(incoming_lbls)}"

existing_train_imgs = sorted(TRAIN_IMG_DIR.glob("*.*"))
existing_train_lbls = sorted(TRAIN_LBL_DIR.glob("*.txt"))

assert len(existing_train_imgs) == 210, f"Expected 210 existing train images, found {len(existing_train_imgs)}"
assert len(existing_train_lbls) == 210, f"Expected 210 existing train labels, found {len(existing_train_lbls)}"

# Check for filename collisions
incoming_img_stems = {f.stem for f in incoming_imgs}
existing_img_stems = {f.stem for f in existing_train_imgs}
collision = incoming_img_stems & existing_img_stems
assert len(collision) == 0, f"Filename collision detected: {collision}"
print("Zero filename collisions between incoming and existing training data.")

# Verify each incoming image and label before copying
incoming_records = []
incoming_class_counts = Counter()

for img_file in incoming_imgs:
    lbl_file = ANNOTATIONS_PILOT / f"{img_file.stem}.txt"
    assert lbl_file.exists(), f"Missing label file for {img_file.name}"
    
    with Image.open(img_file) as im:
        w, h = im.size
        
    sha256 = hashlib.sha256(img_file.read_bytes()).hexdigest()
    
    lines = [l.strip().split() for l in lbl_file.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) > 0, f"Empty label file: {lbl_file.name}"
    
    file_classes = []
    for line in lines:
        cls_id = int(line[0])
        coords = [float(x) for x in line[1:5]]
        for c in coords:
            assert 0.0 <= c <= 1.0, f"Out of bounds coord {c} in {lbl_file.name}"
        cls_name = CLASS_NAMES[cls_id]
        incoming_class_counts[cls_name] += 1
        file_classes.append(cls_name)
        
    incoming_records.append({
        "filename": img_file.name,
        "stem": img_file.stem,
        "sha256": sha256,
        "width": w,
        "height": h,
        "instances": len(lines),
        "classes": file_classes
    })

print(f"Pre-integration verified {len(incoming_records)} incoming images and labels.")
print(f"Incoming instance distribution: {dict(incoming_class_counts)}")

print("\n=== 2. EXECUTING INTEGRATION ===")
# Copy images and labels into active train directory
for rec in incoming_records:
    fname = rec["filename"]
    stem = rec["stem"]
    
    src_img = RAW_INCOMING / fname
    dst_img = TRAIN_IMG_DIR / fname
    shutil.copy2(src_img, dst_img)
    
    src_lbl = ANNOTATIONS_PILOT / f"{stem}.txt"
    dst_lbl = TRAIN_LBL_DIR / f"{stem}.txt"
    shutil.copy2(src_lbl, dst_lbl)

print(f"Integrated 100 images into {TRAIN_IMG_DIR}")
print(f"Integrated 100 labels into {TRAIN_LBL_DIR}")

print("\n=== 3. POST-INTEGRATION AUDIT ===")

post_train_imgs = sorted(TRAIN_IMG_DIR.glob("*.*"))
post_train_lbls = sorted(TRAIN_LBL_DIR.glob("*.txt"))

print(f"Post-integration training images: {len(post_train_imgs)} (Expected: 310)")
print(f"Post-integration training labels: {len(post_train_lbls)} (Expected: 310)")
assert len(post_train_imgs) == 310
assert len(post_train_lbls) == 310

# Image-label pairing check
post_img_stems = {f.stem for f in post_train_imgs}
post_lbl_stems = {f.stem for f in post_train_lbls}
assert post_img_stems == post_lbl_stems, f"Pairing mismatch: {post_img_stems ^ post_lbl_stems}"
print("Pairing check: 100% paired (310 pairs, 0 orphaned files).")

# Count all active instances in train
train_class_counts = Counter()
total_train_boxes = 0
for lbl_file in post_train_lbls:
    lines = [l.strip().split() for l in lbl_file.read_text(encoding="utf-8").splitlines() if l.strip()]
    for line in lines:
        cls_id = int(line[0])
        train_class_counts[CLASS_NAMES[cls_id]] += 1
        total_train_boxes += 1

print(f"Total active training instances: {total_train_boxes} (Expected: 829)")
print("Active training per-class breakdown:")
for cls_id in range(6):
    name = CLASS_NAMES[cls_id]
    cnt = train_class_counts[name]
    print(f"  {cls_id}: {name:15s} = {cnt}")

assert train_class_counts["dent"] == 269, f"Expected 269 dents, got {train_class_counts['dent']}"
assert train_class_counts["scratch"] == 260, f"Expected 260 scratches, got {train_class_counts['scratch']}"
assert train_class_counts["crack"] == 169, f"Expected 169 cracks, got {train_class_counts['crack']}"
assert train_class_counts["glass shatter"] == 45, f"Expected 45 glass shatter, got {train_class_counts['glass shatter']}"
assert train_class_counts["lamp broken"] == 64, f"Expected 64 lamp broken, got {train_class_counts['lamp broken']}"
assert train_class_counts["tire flat"] == 22, f"Expected 22 tire flat, got {train_class_counts['tire flat']}"
assert total_train_boxes == 829

# Validation split audit (Untouched)
val_imgs = sorted(VAL_IMG_DIR.glob("*.*"))
val_lbls = sorted(VAL_LBL_DIR.glob("*.txt"))
assert len(val_imgs) == 45 and len(val_lbls) == 45
val_class_counts = Counter()
for lbl_file in val_lbls:
    for line in lbl_file.read_text(encoding="utf-8").splitlines():
        if line.strip():
            val_class_counts[CLASS_NAMES[int(line.split()[0])]] += 1

# Test split audit (Untouched Frozen)
test_imgs = sorted(TEST_IMG_DIR.glob("*.*"))
test_lbls = sorted(TEST_LBL_DIR.glob("*.txt"))
assert len(test_imgs) == 45 and len(test_lbls) == 45
test_class_counts = Counter()
for lbl_file in test_lbls:
    for line in lbl_file.read_text(encoding="utf-8").splitlines():
        if line.strip():
            test_class_counts[CLASS_NAMES[int(line.split()[0])]] += 1

# Leakage checks
train_stems = {f.stem for f in post_train_imgs}
val_stems = {f.stem for f in val_imgs}
test_stems = {f.stem for f in test_imgs}

assert len(train_stems & val_stems) == 0, "Train-Val filename leak!"
assert len(train_stems & test_stems) == 0, "Train-Test filename leak!"
assert len(val_stems & test_stems) == 0, "Val-Test filename leak!"

train_hashes = {hashlib.sha256(f.read_bytes()).hexdigest(): f.name for f in post_train_imgs}
val_hashes = {hashlib.sha256(f.read_bytes()).hexdigest(): f.name for f in val_imgs}
test_hashes = {hashlib.sha256(f.read_bytes()).hexdigest(): f.name for f in test_imgs}

assert len(set(train_hashes.keys()) & set(val_hashes.keys())) == 0, "Train-Val SHA256 leak!"
assert len(set(train_hashes.keys()) & set(test_hashes.keys())) == 0, "Train-Test SHA256 leak!"
assert len(set(val_hashes.keys()) & set(test_hashes.keys())) == 0, "Val-Test SHA256 leak!"
print("Zero leakage between Train, Val, and Test splits verified.")

# Save integration manifest
integration_manifest = {
    "manifest_version": "1.0.0",
    "integration_timestamp": datetime.now().isoformat(),
    "approved_scope": "Integration of 100 official CarDD train2017 images into CarDD_Expanded_v1/train",
    "pre_integration_train_count": 210,
    "integrated_count": 100,
    "post_integration_train_count": 310,
    "total_train_instances": total_train_boxes,
    "class_distribution_train": dict(train_class_counts),
    "class_distribution_val": dict(val_class_counts),
    "class_distribution_test": dict(test_class_counts),
    "rollback_file_list": [r["filename"] for r in incoming_records],
    "integrated_images": incoming_records
}

with open(MANIFEST_OUT, "w", encoding="utf-8") as f:
    json.dump(integration_manifest, f, indent=2)

print(f"Saved integration manifest: {MANIFEST_OUT}")

# Save final class distribution summary
class_distribution_payload = {
    "dataset": "CarDD_Expanded_v1",
    "updated_at": datetime.now().isoformat(),
    "total_images": {
        "train": len(post_train_imgs),
        "val": len(val_imgs),
        "test": len(test_imgs),
        "total": len(post_train_imgs) + len(val_imgs) + len(test_imgs)
    },
    "total_instances": {
        "train": total_train_boxes,
        "val": sum(val_class_counts.values()),
        "test": sum(test_class_counts.values()),
        "total": total_train_boxes + sum(val_class_counts.values()) + sum(test_class_counts.values())
    },
    "splits": {
        "train": {
            "images": len(post_train_imgs),
            "instances": total_train_boxes,
            "classes": dict(train_class_counts)
        },
        "val": {
            "images": len(val_imgs),
            "instances": sum(val_class_counts.values()),
            "classes": dict(val_class_counts)
        },
        "test": {
            "images": len(test_imgs),
            "instances": sum(test_class_counts.values()),
            "classes": dict(test_class_counts)
        }
    }
}

with open(DISTRIBUTION_OUT, "w", encoding="utf-8") as f:
    json.dump(class_distribution_payload, f, indent=2)

print(f"Saved class distribution payload: {DISTRIBUTION_OUT}")
print("Integration and post-integration verification COMPLETE!")
