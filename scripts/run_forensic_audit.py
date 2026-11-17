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

# Load candidate definitions from provenance and manifests
prov_files = sorted(os.listdir(PROV_DIR))
print(f"Found {len(prov_files)} provenance files.")

# Also get rejected candidates info
rej_manifest_path = os.path.join(DATASET_ROOT, "manifests", "rejected_images.csv")
rej_info = {}
if os.path.exists(rej_manifest_path):
    with open(rej_manifest_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rej_info[r["image_id"]] = r

# Let's inspect all 25 files in RAW_DIR
raw_files = sorted(os.listdir(RAW_DIR))
print(f"Found {len(raw_files)} raw files.")

results = []

def compute_dhash(image, hash_size=8):
    resized = image.convert('L').resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = np.array(resized)
    difference = pixels[:, 1:] > pixels[:, :-1]
    return hex(int("".join(["1" if b else "0" for b in difference.flatten()]), 2))[2:].zfill(hash_size * hash_size // 4)

def compute_laplacian_var(image):
    # standard calculation on full-res and downscaled
    w, h = image.size
    if max(w, h) > 1920:
        scale = 1920 / max(w, h)
        scaled_img = image.resize((int(w * scale), int(h * scale)), Image.Resampling.BILINEAR)
    else:
        scaled_img = image
    gray = np.array(scaled_img.convert('L'), dtype=np.float32)
    lap = (
        gray[1:-1, :-2] + gray[1:-1, 2:] + gray[:-2, 1:-1] + gray[2:, 1:-1]
        - 4 * gray[1:-1, 1:-1]
    )
    return float(np.var(lap))

for rf in raw_files:
    cid = rf.split("_raw")[0]
    rpath = os.path.join(RAW_DIR, rf)
    with open(rpath, "rb") as f:
        rbytes = f.read()
    rsha = hashlib.sha256(rbytes).hexdigest()
    
    img = Image.open(rpath)
    w, h = img.size
    raw_exif = img.getexif()
    dhash = compute_dhash(img)
    lap_var = compute_laplacian_var(img)
    
    # Check if present in processed
    p_fn = f"{cid}.jpg"
    p_path = os.path.join(PROC_DIR, p_fn)
    in_processed = os.path.exists(p_path)
    proc_sha = ""
    proc_exif_count = -1
    proc_dims = ""
    if in_processed:
        with open(p_path, "rb") as pf:
            pbytes = pf.read()
        proc_sha = hashlib.sha256(pbytes).hexdigest()
        pimg = Image.open(p_path)
        proc_exif_count = len(pimg.getexif())
        proc_dims = f"{pimg.size[0]}x{pimg.size[1]}"
        
    # Provenance data
    prov_path = os.path.join(PROV_DIR, f"{cid}_provenance.json")
    prov_data = {}
    if os.path.exists(prov_path):
        with open(prov_path, "r", encoding="utf-8") as pf:
            prov_data = json.load(pf)
            
    results.append({
        "image_id": cid,
        "raw_file": rf,
        "raw_sha256": rsha,
        "raw_size": len(rbytes),
        "width": w,
        "height": h,
        "dimensions": f"{w}x{h}",
        "raw_exif_count": len(raw_exif),
        "dhash": dhash,
        "laplacian_var": round(lap_var, 2),
        "in_processed": in_processed,
        "proc_sha256": proc_sha,
        "proc_exif_count": proc_exif_count,
        "proc_dims": proc_dims,
        "source": prov_data.get("source", "Wikimedia Commons" if cid in ["CS_VAL_005", "CS_VAL_011"] else "Unknown"),
        "category": prov_data.get("category", "Tire Flat" if cid == "CS_VAL_005" else ("Glass Shatter" if cid == "CS_VAL_011" else "Unknown")),
        "license_name": prov_data.get("license_name", "CC BY 2.0" if cid in ["CS_VAL_005", "CS_VAL_011"] else ""),
        "license_url": prov_data.get("license_url", "https://creativecommons.org/licenses/by/2.0" if cid in ["CS_VAL_005", "CS_VAL_011"] else ""),
        "author": prov_data.get("author", "Riley" if cid == "CS_VAL_005" else ("Shixart1985" if cid == "CS_VAL_011" else "")),
        "source_page_url": prov_data.get("source_page_url", rej_info.get(cid, {}).get("source_url", "")),
        "attribution": prov_data.get("attribution", "")
    })

print(f"Processed audit for {len(results)} images.")
for r in results:
    res_pass_800x600 = (r["width"] >= 800 and r["height"] >= 600)
    blur_pass_100 = (r["laplacian_var"] >= 100.0)
    blur_pass_50 = (r["laplacian_var"] >= 50.0)
    print(f"{r['image_id']}: {r['dimensions']} | Res >= 800x600: {res_pass_800x600} | Blur: {r['laplacian_var']} (>=100: {blur_pass_100}, >=50: {blur_pass_50}) | in_proc: {r['in_processed']}")
