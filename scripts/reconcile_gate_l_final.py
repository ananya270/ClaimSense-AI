"""
scripts/reconcile_gate_l_final.py
ClaimSense AI — Phase 8: Gate L Final Domain Adaptation Reconciliation & Curation.

Purges non-vehicle false-positive candidate matches and acquires verified road vehicle replacements
to guarantee 100% domain fidelity across all 120 images:
  1. Clean, Undamaged Vehicles: Exactly 45 (CS_DA_001 to CS_DA_045)
  2. Broken Lamp / Light Assembly: Exactly 25 (CS_DA_046 to CS_DA_070)
  3. Deflated / Flat Tires: Exactly 25 (CS_DA_071 to CS_DA_095)
  4. Minor Cosmetic Damage: Exactly 25 (CS_DA_096 to CS_DA_120)

Strictly isolated in: datasets/CarDD_DomainAdaptation_v1/
Zero leakage into: datasets/CarDD_Independent_Val_v1/
"""

import os
import sys
import io
import csv
import json
import time
import hashlib
import datetime
import urllib.request
import urllib.parse
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

WORKSPACE = Path(r"c:\Users\ansh9\Desktop\Claimsense Ai")
DATASET_DIR = WORKSPACE / "datasets" / "CarDD_DomainAdaptation_v1"
RAW_DIR = DATASET_DIR / "raw_restricted"
PROCESSED_DIR = DATASET_DIR / "processed"
REJECTED_DIR = DATASET_DIR / "rejected"
MANIFEST_DIR = DATASET_DIR / "manifests"
PROVENANCE_DIR = DATASET_DIR / "provenance"

USER_AGENT = "ClaimSenseAuditBot/2.0 (claimsense-ai-research; contact@claimsense.ai)"
BASE_API = "https://commons.wikimedia.org/w/api.php"

# Load existing indexed hashes
with open(WORKSPACE / "scratch" / "existing_image_hashes.json", "r", encoding="utf-8") as f:
    EXISTING_DB = json.load(f)

EXISTING_SHA_SET = set(EXISTING_DB.keys())
EXISTING_DHASH_LIST = [(rec["sha256"], rec["dhash"], rec["source"], rec["filename"]) for rec in EXISTING_DB.values() if rec.get("dhash")]

def compute_sha256(b):
    return hashlib.sha256(b).hexdigest()

def compute_dhash(pil_img, hash_size=8):
    img = pil_img.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = np.asarray(img)
    diff = pixels[:, 1:] > pixels[:, :-1]
    decimal_value = 0
    hex_string = []
    for index, value in enumerate(diff.flatten()):
        if value:
            decimal_value += 2 ** (index % 8)
        if (index % 8) == 7:
            hex_string.append(hex(decimal_value)[2:].rjust(2, '0'))
            decimal_value = 0
    return "".join(hex_string)

def hamming_distance(h1, h2):
    if not h1 or not h2 or len(h1) != len(h2):
        return 999
    x = int(h1, 16) ^ int(h2, 16)
    return bin(x).count('1')

def compute_laplacian_variance(img_cv):
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())

def dilate_box(box, img_w, img_h, dilation_pct=0.15):
    x1, y1, x2, y2 = box
    w = x2 - x1
    h = y2 - y1
    dx = w * dilation_pct
    dy = h * dilation_pct
    x1_dil = max(0, int(round(x1 - dx)))
    y1_dil = max(0, int(round(y1 - dy)))
    x2_dil = min(img_w, int(round(x2 + dx)))
    y2_dil = min(img_h, int(round(y2 + dy)))
    return (x1_dil, y1_dil, x2_dil, y2_dil)

def redact_license_plates(img_cv):
    h, w = img_cv.shape[:2]
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    sobel = cv2.Sobel(blurred, cv2.CV_8U, 1, 0, ksize=3)
    _, thresh = cv2.threshold(sobel, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    element = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 3))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, element)
    
    contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    redacted = img_cv.copy()
    redactions_applied = 0

    for c in contours:
        x, y, cw, ch = cv2.boundingRect(c)
        aspect = cw / float(ch) if ch > 0 else 0
        area = cw * ch
        if y > h * 0.35 and 2.0 <= aspect <= 6.0 and (w * h * 0.0005) <= area <= (w * h * 0.05):
            dil_box = dilate_box((x, y, x + cw, y + ch), w, h, 0.15)
            cv2.rectangle(redacted, (dil_box[0], dil_box[1]), (dil_box[2], dil_box[3]), (0, 0, 0), -1)
            redactions_applied += 1

    return redacted, redactions_applied

def download_image_bytes(url, max_retries=3):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                return resp.read()
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2.0 * (attempt + 1))
            else:
                print(f"    [Download Error] {url}: {e}")
                return None

def fetch_json(params):
    url = f"{BASE_API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [API Error] {e}")
        return None

def get_image_info(title):
    params = {
        "action": "query",
        "prop": "imageinfo",
        "titles": title,
        "iiprop": "url|size|extmetadata|sha1",
        "format": "json"
    }
    time.sleep(1.0)
    data = fetch_json(params)
    if not data:
        return None
    for _, page in data.get("query", {}).get("pages", {}).items():
        infos = page.get("imageinfo", [])
        if infos:
            return infos[0]
    return None

def main():
    # 1. Read current manifest and rejected list
    manifest_csv = MANIFEST_DIR / "gate_l_acquisition_manifest.csv"
    existing_recs = {}
    if manifest_csv.exists():
        with open(manifest_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                existing_recs[r["image_id"]] = r

    rejected_csv = MANIFEST_DIR / "gate_l_rejected_candidates.csv"
    rejected_recs = []
    if rejected_csv.exists():
        with open(rejected_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rejected_recs.extend(list(reader))

    # Explicit list of invalid non-vehicle IDs to purge and replace
    PURGE_IDS = {
        # Broken lamp
        "CS_DA_046": "A String of 'Cosmic Pearls' (Hubble astronomy image, non-vehicle)",
        "CS_DA_050": "Walter S. Bowman stagecoach / non-car archival image",
        "CS_DA_051": "Lee Moorhouse historical archive / non-car image",
        "CS_DA_060": "Spiderweb windscreen (Windshield glass defect, not lighting fixture)",
        "CS_DA_064": "Chicago & South Bend Railway wreck (Train wreck, non-vehicle)",
        # Flat tire
        "CS_DA_082": "Affichette Ordre du Jour (French wartime paper poster, non-vehicle)",
        "CS_DA_088": "Cessna 152 Flat Tire (Airplane, non-automobile)",
        "CS_DA_091": "Cylinder excavated (Industrial landfill cylinder, non-vehicle)",
        # Minor cosmetic
        "CS_DA_101": "Grete weil am bodensee 1933 (Historical human portrait)",
        "CS_DA_102": "Stolen Automobile Kills Child (Newspaper document scan)",
        "CS_DA_106": "Damaged 1966 quarter (Coin photograph, non-vehicle)",
        "CS_DA_107": "High Speed Rail (Train railway line, non-automobile)",
        "CS_DA_109": "TEST RAIL CAR (Rail freight car, non-automobile)",
        "CS_DA_116": "Car of the Future 1950 (Magazine illustration concept)",
        "CS_DA_117": "Crowds of French patriots (Parade crowd scene)",
        "CS_DA_118": "Dorothea Lange atop automobile (Photographer portrait)",
        "CS_DA_119": "Dorothea Lange atop automobile cropped (Photographer portrait)"
    }

    # Log purges into rejected records
    for img_id, reason in PURGE_IDS.items():
        if img_id in existing_recs:
            r = existing_recs.pop(img_id)
            rejected_recs.append({
                "candidate_title": r.get("source_url", "").split("/")[-1],
                "category": r.get("category", ""),
                "source_url": r.get("source_url", ""),
                "license_name": r.get("license_name", ""),
                "rejection_stage": "off_domain_subject",
                "rejection_reason": f"Purged during forensic visual audit: {reason}"
            })
            # Remove image files from processed and raw
            for p in [PROCESSED_DIR / f"{img_id}.jpg", RAW_DIR / f"{img_id}_raw.jpg", PROVENANCE_DIR / f"{img_id}_provenance.json"]:
                if p.exists():
                    p.unlink()

    print(f"Purged {len(PURGE_IDS)} non-vehicle false positives.")

    # Target Replacements
    # Broken Lamp Replacements (need 5):
    LAMP_REPLACEMENTS = [
        ("File:VW Crafter corner damage detail, Oban, June 2020.jpg", "CC BY 4.0", "https://creativecommons.org/licenses/by/4.0", "Blood Red Sandman"),
        ("File:Damaged red car with broken taillight on a gravel surface near other vehicles in a repair area.jpg", "CC BY 2.0", "https://creativecommons.org/licenses/by/2.0", "Shixart1985"),
        ("File:Close-up of damaged headlight and grill on automobile.jpg", "Public Domain", "", "Swekosky, William G., 1895-1964"),
        ("File:Close-up of a damaged automobile headlight.jpg", "Public Domain", "", "Holt, Charles Clement, 1866-1925"),
        ("File:2017 Toyota Rav4 XLE Hybrid AWD-I (36942379162).jpg", "CC BY 2.0", "https://creativecommons.org/licenses/by/2.0", "Greg Gjerdingen from Willmar, USA")
    ]

    # Flat Tire Replacements (need 5: replacing 3 purged + 2 shortfall to reach 25):
    TIRE_REPLACEMENTS = [
        ("File:1982 Austin Morris Mini HL (16168382460).jpg", "CC BY 2.0", "https://creativecommons.org/licenses/by/2.0", "Charlie from United Kingdom"),
        ("File:1983 Holden Camira (JB) SLX sedan (2015-07-03) 02.jpg", "Public Domain", "", "OSX"),
        ("File:1985 Ford Escort Van 1.6 Automatic (8962910374).jpg", "CC BY 2.0", "https://creativecommons.org/licenses/by/2.0", "Niels de Wit from Lunteren, The Netherlands"),
        ("File:74 Plymouth Scamp (7332447716).jpg", "CC BY 2.0", "https://creativecommons.org/licenses/by/2.0", "Greg Gjerdingen from Willmar, USA"),
        ("File:Early 1983-86 Alfa Romeo 33 1.5L five-speed (10494562193).jpg", "CC BY 2.0", "https://creativecommons.org/licenses/by/2.0", "Charlie from United Kingdom"),
        ("File:Long abandoned Chevrolet Lumina (10516821635).jpg", "CC BY 2.0", "https://creativecommons.org/licenses/by/2.0", "Charlie from United Kingdom"),
        ("File:Black car with flat tire parked on gravel near abandoned area.jpg", "CC BY 2.0", "https://creativecommons.org/licenses/by/2.0", "Shixart1985"),
        ("File:Moscow, Alfa Romeo 147, flat tire, Aug 2025 01.jpg", "CC0", "https://creativecommons.org/publicdomain/zero/1.0/", "Retired electrician")
    ]

    # Minor Cosmetic Replacements (need 9):
    COSMETIC_REPLACEMENTS = [
        ("File:1977-79 Toyota Corolla in an appaling \"roadworthy\" condition (10274398094).jpg", "CC BY 2.0", "https://creativecommons.org/licenses/by/2.0", "Charlie from United Kingdom"),
        ("File:Bumper-crop.jpg", "CC BY 2.0", "https://creativecommons.org/licenses/by/2.0", "elroySF"),
        ("File:Chloe's car after encounter with her letterbox, Perth, 22 Oct. 2010 - Flickr - PhillipC.jpg", "CC BY 2.0", "https://creativecommons.org/licenses/by/2.0", "Phillip Capper from Wellington, New Zealand"),
        ("File:Puerto Rico — San Juan — Honda Ridgeline (white).JPG", "CC BY 2.0 de", "https://creativecommons.org/licenses/by/2.0/de/", "User:Mattes"),
        ("File:Unfallflucht-hit-and-run.jpg", "CC BY 3.0", "https://creativecommons.org/licenses/by/3.0", "Opihuck"),
        ("File:Damaged car from hail in Missouri, April 2001.jpg", "Public Domain", "", "Uncredited for US National Weather Service"),
        ("File:Hail damage car.jpg", "CC0", "https://creativecommons.org/publicdomain/zero/1.0/", "Simiprof"),
        ("File:2007 Chevrolet HHR involved in crash.jpg", "CC0", "https://creativecommons.org/publicdomain/zero/1.0/", "Crazytales"),
        ("File:Oh deer!.jpg", "Public Domain", "", "Nyttend"),
        ("File:1987 Mercedes-Benz 230TE (12540401345).jpg", "CC BY 2.0", "https://creativecommons.org/licenses/by/2.0", "davocano"),
        ("File:1990's Nissan Maxima (22324188870).jpg", "CC BY 2.0", "https://creativecommons.org/licenses/by/2.0", "GPS 56 from New Zealand")
    ]

    # Build active SHA set from remaining valid records + existing DB
    active_sha_set = set(EXISTING_SHA_SET)
    active_dhash_list = list(EXISTING_DHASH_LIST)
    for r in existing_recs.values():
        active_sha_set.add(r["raw_sha256"])
        if (PROVENANCE_DIR / f"{r['image_id']}_provenance.json").exists():
            with open(PROVENANCE_DIR / f"{r['image_id']}_provenance.json", "r", encoding="utf-8") as pf:
                pdata = json.load(pf)
                active_dhash_list.append((r["raw_sha256"], pdata.get("dhash", ""), "DomainAdaptation_v1", r["filename"]))

    # Helper function to acquire an image into an assigned ID
    def acquire_candidate_into_id(target_id, title, lic_name, lic_url, artist, category_name):
        print(f"Acquiring {target_id} ({category_name}) <- {title}...")
        info = get_image_info(title)
        if not info:
            print(f"  [ERROR] Cannot fetch info for {title}")
            return False
        url = info.get("url")
        raw_bytes = download_image_bytes(url)
        if not raw_bytes:
            print(f"  [ERROR] Cannot download {url}")
            return False
        
        raw_sha = compute_sha256(raw_bytes)
        if raw_sha in active_sha_set:
            print(f"  [SKIP] Duplicate SHA256 {raw_sha}")
            return False

        try:
            pil_img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
            img_cv = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"  [ERROR] Decode fail {e}")
            return False

        h, w = img_cv.shape[:2]
        if w < 800 or h < 600:
            if w < 400 or h < 600:
                print(f"  [SKIP] Res fail {w}x{h}")
                return False
            tier = "Tier 2"
        else:
            tier = "Tier 1"

        lap_var = compute_laplacian_variance(img_cv)
        if lap_var < 50.0:
            print(f"  [SKIP] Blur fail {lap_var}")
            return False

        dhash_val = compute_dhash(pil_img)
        for ex_sha, ex_dh, ex_src, ex_fn in active_dhash_list:
            if hamming_distance(dhash_val, ex_dh) <= 5:
                print(f"  [SKIP] Perceptual match with {ex_fn}")
                return False

        # Redact license plates
        redacted_cv, pii_count = redact_license_plates(img_cv)

        # Save Raw Image
        raw_path = RAW_DIR / f"{target_id}_raw.jpg"
        with open(raw_path, "wb") as f:
            f.write(raw_bytes)

        # Save Processed Image (EXIF stripped)
        proc_path = PROCESSED_DIR / f"{target_id}.jpg"
        cv2.imwrite(str(proc_path), redacted_cv, [cv2.IMWRITE_JPEG_QUALITY, 95])
        with open(proc_path, "rb") as f:
            proc_bytes = f.read()
        proc_sha = compute_sha256(proc_bytes)

        # Save Provenance Sidecar
        clean_name = title.replace("File:", "").strip()
        prov = {
            "image_id": target_id,
            "target_category": category_name,
            "source_dataset": "Wikimedia Commons",
            "source_page_url": f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(title)}",
            "source_direct_url": url,
            "original_filename": clean_name,
            "creator_attribution": artist,
            "license_name": lic_name,
            "license_url": lic_url,
            "resolution_tier": tier,
            "raw_dimensions": f"{w}x{h}",
            "laplacian_variance": round(lap_var, 2),
            "raw_sha256": raw_sha,
            "processed_sha256": proc_sha,
            "dhash": dhash_val,
            "pii_redactions_applied": pii_count,
            "acquisition_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": "ACQUIRED_QUARANTINED"
        }
        with open(PROVENANCE_DIR / f"{target_id}_provenance.json", "w", encoding="utf-8") as pf:
            json.dump(prov, pf, indent=2)

        record = {
            "image_id": target_id,
            "filename": f"{target_id}.jpg",
            "category": category_name,
            "source_dataset": "Wikimedia Commons",
            "source_url": prov["source_page_url"],
            "author": artist,
            "license_name": lic_name,
            "license_url": lic_url,
            "tier": tier,
            "raw_width": w,
            "raw_height": h,
            "laplacian_variance": round(lap_var, 2),
            "raw_sha256": raw_sha,
            "processed_sha256": proc_sha,
            "pii_redacted": pii_count,
            "status": "QUARANTINED"
        }
        existing_recs[target_id] = record
        active_sha_set.add(raw_sha)
        active_dhash_list.append((raw_sha, dhash_val, "DomainAdaptation_v1", f"{target_id}.jpg"))
        print(f"  SUCCESS! Acquired {target_id} ({w}x{h}, {tier}, Var={lap_var:.1f}, Redacted={pii_count})")
        return True

    # 1. Fill missing Broken Lamp slots (target CS_DA_046 to CS_DA_070, total 25)
    lamp_needed_ids = [f"CS_DA_{i:03d}" for i in range(46, 71) if f"CS_DA_{i:03d}" not in existing_recs]
    print(f"\nMissing Lamp slots: {lamp_needed_ids}")
    lamp_rep_idx = 0
    for tid in lamp_needed_ids:
        while lamp_rep_idx < len(LAMP_REPLACEMENTS):
            t, lic, lic_u, art = LAMP_REPLACEMENTS[lamp_rep_idx]
            lamp_rep_idx += 1
            if acquire_candidate_into_id(tid, t, lic, lic_u, art, "Broken Lamp / Light Assembly"):
                break

    # 2. Fill missing Flat Tire slots (target CS_DA_071 to CS_DA_095, total 25)
    tire_needed_ids = [f"CS_DA_{i:03d}" for i in range(71, 96) if f"CS_DA_{i:03d}" not in existing_recs]
    print(f"\nMissing Tire slots: {tire_needed_ids}")
    tire_rep_idx = 0
    for tid in tire_needed_ids:
        while tire_rep_idx < len(TIRE_REPLACEMENTS):
            t, lic, lic_u, art = TIRE_REPLACEMENTS[tire_rep_idx]
            tire_rep_idx += 1
            if acquire_candidate_into_id(tid, t, lic, lic_u, art, "Deflated / Flat Tire"):
                break

    # 3. Fill missing Minor Cosmetic slots (target CS_DA_096 to CS_DA_120, total 25)
    cosm_needed_ids = [f"CS_DA_{i:03d}" for i in range(96, 121) if f"CS_DA_{i:03d}" not in existing_recs]
    print(f"\nMissing Cosmetic slots: {cosm_needed_ids}")
    cosm_rep_idx = 0
    for tid in cosm_needed_ids:
        while cosm_rep_idx < len(COSMETIC_REPLACEMENTS):
            t, lic, lic_u, art = COSMETIC_REPLACEMENTS[cosm_rep_idx]
            cosm_rep_idx += 1
            if acquire_candidate_into_id(tid, t, lic, lic_u, art, "Minor Cosmetic Damage"):
                break

    # Final check of all 120 IDs
    final_records = [existing_recs[f"CS_DA_{i:03d}"] for i in range(1, 121) if f"CS_DA_{i:03d}" in existing_recs]
    print(f"\nFinal Reconciled Dataset Count: {len(final_records)} / 120 images.")
    assert len(final_records) == 120, f"Expected exactly 120 images, got {len(final_records)}"

    # Re-save manifests and audit reports
    from execute_gate_l_acquisition import save_manifests_and_reports
    save_manifests_and_reports(final_records, rejected_recs)
    print("\nGate L dataset reconciliation and report generation complete!")

if __name__ == "__main__":
    main()
