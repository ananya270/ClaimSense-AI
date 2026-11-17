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

def compute_dhash(image, hash_size=8):
    resized = image.convert('L').resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = np.array(resized)
    difference = pixels[:, 1:] > pixels[:, :-1]
    return hex(int("".join(["1" if b else "0" for b in difference.flatten()]), 2))[2:].zfill(hash_size * hash_size // 4)

def hamming_dist(h1, h2):
    return bin(int(h1, 16) ^ int(h2, 16)).count('1')

def compute_laplacian_var(image, downscale=True):
    w, h = image.size
    if downscale and max(w, h) > 1920:
        scale = 1920 / max(w, h)
        img = image.resize((int(w * scale), int(h * scale)), Image.Resampling.BILINEAR)
    else:
        img = image
    gray = np.array(img.convert('L'), dtype=np.float32)
    lap = (
        gray[1:-1, :-2] + gray[1:-1, 2:] + gray[:-2, 1:-1] + gray[2:, 1:-1]
        - 4 * gray[1:-1, 1:-1]
    )
    return float(np.var(lap))

# Master candidate catalog
CANDIDATE_DATA = [
    {"id": "CS_VAL_001", "title": "File:'95-'98 Ford Explorer With Flat Tire.JPG", "source": "Wikimedia Commons", "category": "Tire Flat", "license": "Public Domain", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/", "author": "Bull-Doser", "plate_box": [850, 981, 1281, 1154]},
    {"id": "CS_VAL_002", "title": "File:1953 Chrysler Imperial (5832921647).jpg", "source": "Wikimedia Commons", "category": "Tire Flat", "license": "CC BY 2.0", "license_url": "https://creativecommons.org/licenses/by/2.0", "author": "Greg Gjerdingen", "plate_box": [1731, 1638, 2283, 1862]},
    {"id": "CS_VAL_003", "title": "File:1977 Datsun 180B (10899901566).jpg", "source": "Wikimedia Commons", "category": "Tire Flat", "license": "CC BY 2.0", "license_url": "https://creativecommons.org/licenses/by/2.0", "author": "Riley", "plate_box": [1235, 1591, 1713, 1772]},
    {"id": "CS_VAL_004", "title": "File:1978 Ford Cortina (TE) L 4 sedan (2015-07-14) 01.jpg", "source": "Wikimedia Commons", "category": "Tire Flat", "license": "Public Domain", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/", "author": "OSX", "plate_box": [1802, 2022, 2469, 2318]},
    {"id": "CS_VAL_005", "title": "File:1979 Honda Civic (7319282064).jpg", "source": "Wikimedia Commons", "category": "Tire Flat", "license": "CC BY 2.0", "license_url": "https://creativecommons.org/licenses/by/2.0", "author": "Riley", "plate_box": None},
    {"id": "CS_VAL_006", "title": "File:1982 Austin Morris Mini HL (16168382460).jpg", "source": "Wikimedia Commons", "category": "Tire Flat", "license": "CC BY 2.0", "license_url": "https://creativecommons.org/licenses/by/2.0", "author": "Charlie", "plate_box": [1508, 1902, 2507, 2198]},
    {"id": "CS_VAL_007", "title": "File:1983 Holden Camira (JB) SLX sedan (2015-07-03) 02.jpg", "source": "Wikimedia Commons", "category": "Tire Flat", "license": "Public Domain", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/", "author": "OSX", "plate_box": [1618, 1965, 2396, 2261]},
    {"id": "CS_VAL_008", "title": "File:1985 Toyota Corolla (AE82) CS-X Seca liftback (2015-07-10) 01.jpg", "source": "Wikimedia Commons", "category": "Tire Flat", "license": "Public Domain", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/", "author": "OSX", "plate_box": [1802, 1908, 2469, 2204]},
    {"id": "CS_VAL_009", "title": "File:Abandoned green car with broken window.jpg", "source": "Wikimedia Commons", "category": "Glass Shatter", "license": "CC BY 2.0", "license_url": "https://creativecommons.org/licenses/by/2.0", "author": "Shixart1985", "plate_box": None},
    {"id": "CS_VAL_010", "title": "File:Broken car window in salvage yard with debris and damaged interior seen through windshield.jpg", "source": "Wikimedia Commons", "category": "Glass Shatter", "license": "CC BY 2.0", "license_url": "https://creativecommons.org/licenses/by/2.0", "author": "Shixart1985", "plate_box": None},
    {"id": "CS_VAL_011", "title": "File:Broken car with shattered glass in a junkyard during daylight hours showing signs of neglect and damage.jpg", "source": "Wikimedia Commons", "category": "Glass Shatter", "license": "CC BY 2.0", "license_url": "https://creativecommons.org/licenses/by/2.0", "author": "Shixart1985", "plate_box": None},
    {"id": "CS_VAL_012", "title": "File:Car with Broken Windshield.jpg", "source": "Wikimedia Commons", "category": "Glass Shatter", "license": "CC BY 2.0", "license_url": "https://creativecommons.org/licenses/by/2.0", "author": "Daniel Ramirez", "plate_box": None},
    {"id": "CS_VAL_013", "title": "File:Damaged car in junkyard with a broken windshield.jpg", "source": "Wikimedia Commons", "category": "Glass Shatter", "license": "CC BY 2.0", "license_url": "https://creativecommons.org/licenses/by/2.0", "author": "Shixart1985", "plate_box": None},
    {"id": "CS_VAL_014", "title": "File:Damaged car window in a junkyard with broken glass on the windshield and rows of vehicles in the background.jpg", "source": "Wikimedia Commons", "category": "Glass Shatter", "license": "CC BY 2.0", "license_url": "https://creativecommons.org/licenses/by/2.0", "author": "Shixart1985", "plate_box": None},
    {"id": "CS_VAL_015", "title": "File:FEMA - 44376 - truck windshield with hail damage in OK.jpg", "source": "Wikimedia Commons", "category": "Glass Shatter", "license": "Public Domain", "license_url": "https://www.fema.gov", "author": "Win Henderson / FEMA", "plate_box": None},
    {"id": "CS_VAL_016", "title": "File:Damaged car from hail in Missouri, April 2001.jpg", "source": "Wikimedia Commons", "category": "Dent", "license": "Public Domain", "license_url": "https://www.weather.gov", "author": "US National Weather Service", "plate_box": None},
    {"id": "CS_VAL_017", "title": "File:Hail damage car.jpg", "source": "Wikimedia Commons", "category": "Dent", "license": "Public Domain", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/", "author": "Simiprof", "plate_box": None},
    {"id": "CS_VAL_018", "title": "File:Hailstone damage on various vehicles from 4 July 2010 hailstorm (Limon, eastern Colorado, USA).jpg", "source": "Wikimedia Commons", "category": "Dent", "license": "CC BY 2.0", "license_url": "https://creativecommons.org/licenses/by/2.0", "author": "James St. John", "plate_box": None},
    {"id": "CS_VAL_019", "title": "File:Hailstone-smashed back window of a car from 4 July 2010 hailstorm (Limon, eastern Colorado, USA).jpg", "source": "Wikimedia Commons", "category": "Dent", "license": "CC BY 2.0", "license_url": "https://creativecommons.org/licenses/by/2.0", "author": "James St. John", "plate_box": None},
    {"id": "CS_VAL_020", "title": "Car damages 100.png", "source": "Humans in the Loop", "category": "Crack", "license": "CC0 1.0 Universal", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/", "author": "Humans in the Loop", "plate_box": None},
    {"id": "CS_VAL_021", "title": "Car damages 101.png", "source": "Humans in the Loop", "category": "Crack", "license": "CC0 1.0 Universal", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/", "author": "Humans in the Loop", "plate_box": None},
    {"id": "CS_VAL_022", "title": "Car damages 102.jpg", "source": "Humans in the Loop", "category": "Lamp Broken", "license": "CC0 1.0 Universal", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/", "author": "Humans in the Loop", "plate_box": None},
    {"id": "CS_VAL_023", "title": "Car damages 103.png", "source": "Humans in the Loop", "category": "Lamp Broken", "license": "CC0 1.0 Universal", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/", "author": "Humans in the Loop", "plate_box": None},
    {"id": "CS_VAL_024", "title": "Car damages 104.png", "source": "Humans in the Loop", "category": "Scratch", "license": "CC0 1.0 Universal", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/", "author": "Humans in the Loop", "plate_box": None},
    {"id": "CS_VAL_025", "title": "Car damages 105.png", "source": "Humans in the Loop", "category": "Dent", "license": "CC0 1.0 Universal", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/", "author": "Humans in the Loop", "plate_box": None}
]

audit_records = []
all_dhashes = {}

for item in CANDIDATE_DATA:
    cid = item["id"]
    # Find raw file
    raw_candidates = [f for f in os.listdir(RAW_DIR) if f.startswith(f"{cid}_raw")]
    assert len(raw_candidates) == 1, f"Missing raw for {cid}"
    raw_fname = raw_candidates[0]
    raw_fpath = os.path.join(RAW_DIR, raw_fname)
    
    with open(raw_fpath, "rb") as rf:
        raw_bytes = rf.read()
    raw_sha = hashlib.sha256(raw_bytes).hexdigest()
    
    img = Image.open(raw_fpath)
    w, h = img.size
    raw_exif_count = len(img.getexif())
    dhash = compute_dhash(img)
    all_dhashes[cid] = dhash
    
    lap_downscale = compute_laplacian_var(img, downscale=True)
    lap_full = compute_laplacian_var(img, downscale=False)
    
    # Processed copy inspection
    proc_fname = f"{cid}.jpg"
    proc_fpath = os.path.join(PROC_DIR, proc_fname)
    in_proc = os.path.exists(proc_fpath)
    proc_sha = ""
    proc_exif_count = None
    pii_solid_verified = None
    
    if in_proc:
        with open(proc_fpath, "rb") as pf:
            proc_bytes = pf.read()
        proc_sha = hashlib.sha256(proc_bytes).hexdigest()
        pimg = Image.open(proc_fpath)
        proc_exif_count = len(pimg.getexif())
        
        # Verify PII masking
        if item["plate_box"]:
            box = item["plate_box"]
            p_arr = np.array(pimg)
            patch = p_arr[box[1]:box[3], box[0]:box[2]]
            is_zero = np.all(patch == 0)
            pii_solid_verified = is_zero
        else:
            pii_solid_verified = "N/A (No PII)"
            
    # Hard criteria checks
    res_pass = (w >= 800 and h >= 600)
    blur_pass_50 = (lap_downscale >= 50.0)
    blur_pass_100 = (lap_downscale >= 100.0 or lap_full >= 100.0)
    
    # Rejection diagnosis under strict 800x600 gate
    rejection_reasons = []
    if not res_pass:
        fail_dims = []
        if w < 800:
            fail_dims.append(f"Width {w} < 800")
        if h < 600:
            fail_dims.append(f"Height {h} < 600")
        rejection_reasons.append(f"RESOLUTION_GATE_FAILED ({', '.join(fail_dims)})")
    if not blur_pass_50:
        rejection_reasons.append(f"BLUR_GATE_FAILED (Laplacian {lap_downscale:.1f} < 50.0)")
        
    status_strict_800x600 = "REJECTED" if len(rejection_reasons) > 0 else "ACCEPTED"
    primary_failure = "; ".join(rejection_reasons) if rejection_reasons else "NONE (Passed all gates)"
    
    audit_records.append({
        "image_id": cid,
        "title": item["title"],
        "source": item["source"],
        "category": item["category"],
        "license": item["license"],
        "license_url": item["license_url"],
        "author": item["author"],
        "width": w,
        "height": h,
        "dimensions": f"{w}x{h}",
        "raw_sha256": raw_sha,
        "raw_size_bytes": len(raw_bytes),
        "raw_exif_count": raw_exif_count,
        "dhash": dhash,
        "laplacian_downscale": round(lap_downscale, 1),
        "laplacian_full": round(lap_full, 1),
        "in_processed": in_proc,
        "proc_sha256": proc_sha,
        "proc_exif_count": proc_exif_count,
        "pii_masked": "YES" if item["plate_box"] else "NO",
        "pii_solid_verified": pii_solid_verified,
        "res_pass_800x600": res_pass,
        "blur_pass_50": blur_pass_50,
        "blur_pass_100": blur_pass_100,
        "status_strict_800x600": status_strict_800x600,
        "primary_failure": primary_failure
    })

# Check pairwise dHash distances
min_hamming = 999
closest_pair = None
for i in range(len(audit_records)):
    for j in range(i + 1, len(audit_records)):
        c1 = audit_records[i]["image_id"]
        c2 = audit_records[j]["image_id"]
        dist = hamming_dist(audit_records[i]["dhash"], audit_records[j]["dhash"])
        if dist < min_hamming:
            min_hamming = dist
            closest_pair = (c1, c2, dist)

print(f"Minimum pairwise dHash Hamming distance: {min_hamming} between {closest_pair}")
assert min_hamming > 4, f"Perceptual near-duplicate detected! {closest_pair}"

# Summary counts
strict_accepted = [r for r in audit_records if r["status_strict_800x600"] == "ACCEPTED"]
strict_rejected = [r for r in audit_records if r["status_strict_800x600"] == "REJECTED"]
res_failures = [r for r in audit_records if not r["res_pass_800x600"]]

print("\n--- FORENSIC AUDIT SUMMARY ---")
print(f"Total Candidates Attempted: {len(audit_records)}")
print(f"Strict Accepted (Width >= 800 AND Height >= 600, Blur >= 50): {len(strict_accepted)}")
print(f"Strict Rejected: {len(strict_rejected)}")
print(f"Resolution Gate Failures: {len(res_failures)}")
print("Resolution Gate Failure IDs:", [r["image_id"] for r in res_failures])

print("\nStrict Accepted Class Distribution:")
cat_hist = {}
for r in strict_accepted:
    cat_hist[r["category"]] = cat_hist.get(r["category"], 0) + 1
for cat, cnt in cat_hist.items():
    print(f"  {cat}: {cnt}")
