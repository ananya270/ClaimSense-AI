import os
import hashlib
import json
import csv
import numpy as np
from PIL import Image

WORKSPACE = r"C:\Users\ansh9\Desktop\Claimsense Ai"
DATASET_ROOT = os.path.join(WORKSPACE, "datasets", "CarDD_Independent_Val_v1")
RAW_DIR = os.path.join(DATASET_ROOT, "batch_01", "raw_restricted")
PROC_DIR = os.path.join(DATASET_ROOT, "batch_01", "processed")
REJ_DIR = os.path.join(DATASET_ROOT, "batch_01", "rejected")
PROV_DIR = os.path.join(DATASET_ROOT, "manifests", "provenance")
MANIFEST_PATH = os.path.join(DATASET_ROOT, "manifests", "acquisition_manifest.csv")

print("="*70)
print("VERIFYING BATCH 01 ACQUISITION & INTEGRITY")
print("="*70)

# 1. Directory Counts
raw_files = sorted(os.listdir(RAW_DIR))
proc_files = sorted(os.listdir(PROC_DIR))
rej_files = sorted(os.listdir(REJ_DIR))
prov_files = sorted(os.listdir(PROV_DIR))

print(f"Raw Restricted Images: {len(raw_files)} (Target: 25)")
print(f"Processed Images:     {len(proc_files)} (Target: 23)")
print(f"Rejected Images:      {len(rej_files)} (Target: 2)")
print(f"Provenance Sidecars:  {len(prov_files)} (Target: 23)")

assert len(raw_files) == 25, f"Expected 25 raw files, found {len(raw_files)}"
assert len(proc_files) == 23, f"Expected 23 processed files, found {len(proc_files)}"
assert len(rej_files) == 2, f"Expected 2 rejected files, found {len(rej_files)}"
assert len(prov_files) == 23, f"Expected 23 provenance files, found {len(prov_files)}"

# 2. EXIF Tag Verification
print("\nVerifying EXIF Stripping on Processed Images...")
for pf in proc_files:
    img_path = os.path.join(PROC_DIR, pf)
    img = Image.open(img_path)
    exif = img.getexif()
    assert len(exif) == 0, f"FAILED: {pf} has {len(exif)} EXIF tags!"
print("PASS: All 23 processed images have strictly 0 EXIF tags.")

# 3. Cryptographic Hash Integrity Verification
print("\nVerifying SHA-256 Hashes against Manifest...")
manifest_rows = []
with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        manifest_rows.append(r)

assert len(manifest_rows) == 23, f"Expected 23 manifest rows, found {len(manifest_rows)}"

for row in manifest_rows:
    cid = row["image_id"]
    p_fn = row["filename"]
    p_path = os.path.join(PROC_DIR, p_fn)
    with open(p_path, "rb") as f:
        actual_proc_sha = hashlib.sha256(f.read()).hexdigest()
    assert actual_proc_sha == row["processed_sha256"], f"SHA256 mismatch for {p_fn}!"

    # Raw check
    # raw extension
    raw_match = [f for f in raw_files if f.startswith(f"{cid}_raw")]
    assert len(raw_match) == 1, f"Missing raw file for {cid}"
    raw_path = os.path.join(RAW_DIR, raw_match[0])
    with open(raw_path, "rb") as f:
        actual_raw_sha = hashlib.sha256(f.read()).hexdigest()
    assert actual_raw_sha == row["raw_sha256"], f"Raw SHA256 mismatch for {cid}!"

print("PASS: All 23 raw and processed SHA-256 hashes match manifest perfectly.")

# 4. Check Frozen Checkpoints
print("\nVerifying Frozen Checkpoints...")
checkpoints = {
    "Production Baseline": (os.path.join(WORKSPACE, "models", "phase5", "best.pt"), "90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565"),
    "Session 2 Best": (os.path.join(WORKSPACE, "runs", "phase8", "session_2", "weights", "best.pt"), "2ee0a56749ceba72da863fd3496f080ee06f26409daa4e9588fb69ee149333c5"),
    "Session 4 Best": (os.path.join(WORKSPACE, "runs", "phase8", "session_4_training_01", "weights", "best.pt"), "ea53eee94e508bbb81620b47b2a23c9826341b6b5a6981d9371e476cb9d0594f")
}

for name, (path, expected_sha) in checkpoints.items():
    assert os.path.exists(path), f"Checkpoint not found: {path}"
    with open(path, "rb") as f:
        actual_sha = hashlib.sha256(f.read()).hexdigest()
    assert actual_sha == expected_sha, f"CHECKPOINT COMPROMISED! {name}: {actual_sha} != {expected_sha}"
    print(f"PASS: {name} UNTOUCHED (SHA256: {actual_sha[:16]}...)")

print("\n" + "="*70)
print("ALL POST-ACQUISITION INTEGRITY CHECKS PASSED (100%)")
print("="*70)
