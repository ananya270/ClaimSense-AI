"""
scripts/setup_gate_n_datasets.py
ClaimSense AI — Phase 8: Gate N Dataset Setup & Verification.

Prepares:
  1. datasets/domain_adaptation_dev/ (30 images, 30 labels)
  2. datasets/exp01_dataset/ (Train: 310 CarDD + 34 Clean; Val: 30 Dev)
  3. datasets/exp02_dataset/ (Train: 310 CarDD + 34 Clean + 19 Lamp + 19 Tire; Val: 30 Dev)
  4. datasets/exp03_dataset/ (Train: 310 CarDD + 90 DA Train; Val: 30 Dev)
  5. YAML configuration files for all datasets.
"""

import os
import sys
import csv
import shutil
import hashlib
from pathlib import Path

WORKSPACE = Path(r"c:\Users\ansh9\Desktop\Claimsense Ai")
CARDD_TRAIN_IMG = WORKSPACE / "datasets" / "CarDD_Expanded_v1" / "train" / "images"
CARDD_TRAIN_LBL = WORKSPACE / "datasets" / "CarDD_Expanded_v1" / "train" / "labels"

DA_PROCESSED = WORKSPACE / "datasets" / "CarDD_DomainAdaptation_v1" / "processed"
DA_LABELS = WORKSPACE / "datasets" / "CarDD_DomainAdaptation_v1" / "labels"
MANIFESTS = WORKSPACE / "datasets" / "CarDD_DomainAdaptation_v1" / "manifests"

SESSION4_CKPT = WORKSPACE / "runs" / "phase8" / "session_4_training_01" / "weights" / "best.pt"
EXPECTED_S4_HASH = "ea53eee94e508bbb81620b47b2a23c9826341b6b5a6981d9371e476cb9d0594f"

def get_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def copy_or_link(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return
    # Use copyfile for maximum cross-filesystem reliability
    shutil.copyfile(src, dst)

def main():
    print("=" * 80)
    print("CLAIM SENSE AI — PHASE 8: GATE N DATASET SETUP")
    print("=" * 80)

    # 1. Verify starting checkpoint
    assert SESSION4_CKPT.exists(), f"Session 4 checkpoint not found: {SESSION4_CKPT}"
    s4_hash = get_sha256(SESSION4_CKPT)
    print(f"Session 4 Starting Checkpoint: {SESSION4_CKPT}")
    print(f"SHA-256: {s4_hash}")
    assert s4_hash == EXPECTED_S4_HASH, f"Hash mismatch! Expected {EXPECTED_S4_HASH}, got {s4_hash}"
    print("Starting checkpoint integrity verified: MATCH OK.")

    # 2. Read train and dev split manifests
    with open(MANIFESTS / "dev_split.csv", "r", encoding="utf-8") as f:
        dev_rows = list(csv.DictReader(f))
    with open(MANIFESTS / "train_split.csv", "r", encoding="utf-8") as f:
        train_rows = list(csv.DictReader(f))

    assert len(dev_rows) == 30, f"Expected 30 dev rows, got {len(dev_rows)}"
    assert len(train_rows) == 90, f"Expected 90 train rows, got {len(train_rows)}"
    print(f"Loaded {len(train_rows)} train images and {len(dev_rows)} dev images.")

    # 3. Build Dev Dataset
    dev_dir = WORKSPACE / "datasets" / "domain_adaptation_dev"
    dev_img_dir = dev_dir / "images"
    dev_lbl_dir = dev_dir / "labels"
    dev_img_dir.mkdir(parents=True, exist_ok=True)
    dev_lbl_dir.mkdir(parents=True, exist_ok=True)

    for r in dev_rows:
        img_id = r["image_id"]
        src_img = DA_PROCESSED / f"{img_id}.jpg"
        src_lbl = DA_LABELS / f"{img_id}.txt"
        copy_or_link(src_img, dev_img_dir / f"{img_id}.jpg")
        copy_or_link(src_lbl, dev_lbl_dir / f"{img_id}.txt")

    print(f"Dev dataset populated: {len(list(dev_img_dir.glob('*.jpg')))} images, {len(list(dev_lbl_dir.glob('*.txt')))} labels.")

    # Write da_dev.yaml
    yaml_dev = WORKSPACE / "data" / "da_dev.yaml"
    with open(yaml_dev, "w", encoding="utf-8") as f:
        f.write(f"""# ClaimSense AI - Domain Adaptation Dev Set (30 images)
path: {dev_dir.as_posix()}
train: images
val: images

nc: 6
names:
  0: dent
  1: scratch
  2: crack
  3: glass shatter
  4: lamp broken
  5: tire flat
""")
    print(f"Wrote {yaml_dev}")

    # Helper to populate experiment train datasets
    def setup_exp_dataset(exp_name, extra_da_rows):
        exp_dir = WORKSPACE / "datasets" / f"{exp_name}_dataset"
        tr_img = exp_dir / "train" / "images"
        tr_lbl = exp_dir / "train" / "labels"
        val_img = exp_dir / "val" / "images"
        val_lbl = exp_dir / "val" / "labels"

        for d in [tr_img, tr_lbl, val_img, val_lbl]:
            d.mkdir(parents=True, exist_ok=True)

        # 1. CarDD train baseline (310 images)
        for cardd_img in CARDD_TRAIN_IMG.glob("*.jpg"):
            stem = cardd_img.stem
            cardd_lbl = CARDD_TRAIN_LBL / f"{stem}.txt"
            copy_or_link(cardd_img, tr_img / cardd_img.name)
            if cardd_lbl.exists():
                copy_or_link(cardd_lbl, tr_lbl / cardd_lbl.name)
            else:
                # empty label
                (tr_lbl / f"{stem}.txt").touch()

        # 2. Add extra DA images
        for r in extra_da_rows:
            img_id = r["image_id"]
            src_img = DA_PROCESSED / f"{img_id}.jpg"
            src_lbl = DA_LABELS / f"{img_id}.txt"
            copy_or_link(src_img, tr_img / f"{img_id}.jpg")
            copy_or_link(src_lbl, tr_lbl / f"{img_id}.txt")

        # 3. Populate val from dev
        for r in dev_rows:
            img_id = r["image_id"]
            src_img = DA_PROCESSED / f"{img_id}.jpg"
            src_lbl = DA_LABELS / f"{img_id}.txt"
            copy_or_link(src_img, val_img / f"{img_id}.jpg")
            copy_or_link(src_lbl, val_lbl / f"{img_id}.txt")

        # Write dataset yaml
        yaml_path = WORKSPACE / "data" / f"{exp_name}.yaml"
        with open(yaml_path, "w", encoding="utf-8") as f:
            f.write(f"""# ClaimSense AI - {exp_name.upper()} Dataset
path: {exp_dir.as_posix()}
train: train/images
val: val/images

nc: 6
names:
  0: dent
  1: scratch
  2: crack
  3: glass shatter
  4: lamp broken
  5: tire flat
""")
        print(f"[{exp_name}] Setup complete: Train={len(list(tr_img.glob('*.jpg')))} imgs, Val={len(list(val_img.glob('*.jpg')))} imgs. Config: {yaml_path}")

    # EXP01: CarDD (310) + 34 Clean Negative Images
    clean_train = [r for r in train_rows if r["category"] == "Clean, Undamaged Vehicles"]
    assert len(clean_train) == 34, f"Expected 34 clean train images, got {len(clean_train)}"
    setup_exp_dataset("exp01", clean_train)

    # EXP02: EXP01 (344) + 19 Lamp Broken + 19 Flat Tire
    exp02_rows = [r for r in train_rows if r["category"] in [
        "Clean, Undamaged Vehicles", "Broken Lamp / Light Assembly", "Deflated / Flat Tire"
    ]]
    assert len(exp02_rows) == 34 + 19 + 19, f"Expected 72 DA images for EXP02, got {len(exp02_rows)}"
    setup_exp_dataset("exp02", exp02_rows)

    # EXP03: All 90 Domain Adaptation Train Images
    assert len(train_rows) == 90, f"Expected 90 DA train images, got {len(train_rows)}"
    setup_exp_dataset("exp03", train_rows)

    print("\nGate N dataset preparation successfully finished!")

if __name__ == "__main__":
    main()
