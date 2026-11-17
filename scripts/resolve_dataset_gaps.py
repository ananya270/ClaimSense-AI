"""
scripts/resolve_dataset_gaps.py
Targeted Wikimedia Commons Discovery for Tire Flat and Glass Shatter gaps.
Queries MediaWiki Action API across multilingual search terms and subcategories.
Filters strictly for CC0, Public Domain, and CC BY (excluding CC BY-SA, GFDL, unknown).
Saves tire_candidates.csv, glass_candidates.csv, and audit metadata.
"""

import os
import sys
import csv
import json
import time
import urllib.request
import urllib.parse
import re

OUTPUT_DIR = os.path.join(
    "runs", "phase8", "independent_validation_plan", "stage_1_preparation", "gap_resolution"
)
os.makedirs(OUTPUT_DIR, exist_ok=True)

USER_AGENT = "ClaimSenseAuditBot/2.0 (claimsense-ai-research; contact@claimsense.ai)"
BASE_API = "https://commons.wikimedia.org/w/api.php"

def clean_html(raw_html):
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', str(raw_html))
    return cleantext.strip().replace('\n', ' ').replace('\r', '')

def fetch_json(params):
    url = f"{BASE_API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching API: {e}", file=sys.stderr)
        return None

def search_files_by_query(query_str, limit=50):
    params = {
        "action": "query",
        "list": "search",
        "srsearch": f"{query_str} filetype:bitmap",
        "srnamespace": "6", # File:
        "srlimit": str(min(limit, 50)),
        "format": "json"
    }
    data = fetch_json(params)
    if not data:
        return []
    results = data.get("query", {}).get("search", [])
    return [r["title"] for r in results]

def get_category_members(cat_title, limit=50):
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": cat_title,
        "cmlimit": str(min(limit, 50)),
        "format": "json"
    }
    data = fetch_json(params)
    if not data:
        return []
    members = data.get("query", {}).get("categorymembers", [])
    return [m["title"] for m in members if m.get("ns") == 6]

def get_file_metadata_batch(titles):
    if not titles:
        return []
    records = []
    chunk_size = 25
    for i in range(0, len(titles), chunk_size):
        chunk = titles[i:i+chunk_size]
        params = {
            "action": "query",
            "titles": "|".join(chunk),
            "prop": "imageinfo",
            "iiprop": "url|extmetadata|user|size",
            "format": "json"
        }
        data = fetch_json(params)
        if not data:
            continue
        pages = data.get("query", {}).get("pages", {})
        for pid, pdata in pages.items():
            title = pdata.get("title", "")
            if "imageinfo" not in pdata:
                continue
            imginfo = pdata["imageinfo"][0]
            desc_url = imginfo.get("descriptionurl", f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(title)}")
            direct_url = imginfo.get("url", "")
            user = imginfo.get("user", "")
            w = imginfo.get("width", 0)
            h = imginfo.get("height", 0)
            
            ext = imginfo.get("extmetadata", {})
            lic_short = ext.get("LicenseShortName", {}).get("value", "")
            lic_url = ext.get("LicenseUrl", {}).get("value", "")
            artist = clean_html(ext.get("Artist", {}).get("value", user)) or user
            
            lic_lower = lic_short.lower()
            lic_url_lower = lic_url.lower()
            
            is_cc0 = "cc0" in lic_lower or "zero" in lic_lower or "public domain" in lic_lower or "pd" == lic_lower
            is_cc_by = ("cc by" in lic_lower or "cc-by" in lic_lower) and not ("sa" in lic_lower or "sharealike" in lic_lower)
            is_cc_by_sa = "sa" in lic_lower or "sharealike" in lic_lower or "share alike" in lic_lower or "by-sa" in lic_url_lower
            is_gfdl = "gfdl" in lic_lower or "gnu" in lic_lower
            
            if is_cc0:
                norm_lic = "CC0 / Public Domain"
                comm = "PERMITTED"
                exclude = False
                reason = "NONE"
                attribution = f"Public domain / CC0 dedication (Uploaded by {user} to Wikimedia Commons)"
            elif is_cc_by:
                norm_lic = lic_short
                comm = "PERMITTED"
                exclude = False
                reason = "NONE"
                attribution = f"Photo by {artist}, Wikimedia Commons, {lic_short}"
            elif is_cc_by_sa:
                norm_lic = lic_short
                comm = "CONDITIONAL_SHARE_ALIKE"
                exclude = True
                reason = "COPYLEFT_SHARE_ALIKE (CC BY-SA)"
                attribution = f"Photo by {artist}, {lic_short}"
            elif is_gfdl:
                norm_lic = lic_short
                comm = "RESTRICTIVE_GFDL"
                exclude = True
                reason = "GFDL_COPYLEFT"
                attribution = f"Photo by {artist}, {lic_short}"
            else:
                norm_lic = lic_short or "Unknown"
                comm = "UNVERIFIED"
                exclude = True
                reason = f"UNKNOWN_OR_RESTRICTIVE ({lic_short})"
                attribution = f"Unknown / {user}"

            records.append({
                "file_title": title,
                "source_page_url": desc_url,
                "direct_image_url": direct_url,
                "dimensions": f"{w}x{h}",
                "author": artist,
                "license_name": lic_short,
                "normalized_license": norm_lic,
                "license_url": lic_url,
                "is_cc0_pd_or_cc_by": "TRUE" if (is_cc0 or is_cc_by) else "FALSE",
                "commercial_reuse_status": comm,
                "must_exclude": "TRUE" if exclude else "FALSE",
                "exclusion_reason": reason,
                "required_attribution": attribution
            })
        time.sleep(0.5)
    return records

def discover_tire_candidates():
    print("\n--- 1. TIRE FLAT DISCOVERY ---")
    titles = set()
    
    # Categories
    cats = [
        "Category:Flat_tires",
        "Category:Punctured tires",
        "Category:Damaged tires"
    ]
    for c in cats:
        print(f"Checking category: {c}...")
        res = get_category_members(c, limit=50)
        print(f" -> Found {len(res)} files")
        titles.update(res)
        time.sleep(0.5)
        
    # Search terms (Multilingual)
    queries = [
        "flat tire car",
        "flat tyre car",
        "punctured tire vehicle",
        "damaged vehicle tire",
        "pneu crevé voiture",
        "Reifenpanne auto",
        "rueda pinchada coche",
        "pneumatico forato auto"
    ]
    for q in queries:
        print(f"Searching: '{q}'...")
        res = search_files_by_query(q, limit=25)
        print(f" -> Found {len(res)} files")
        titles.update(res)
        time.sleep(0.5)
        
    print(f"Total Unique Tire Candidates Identified: {len(titles)}")
    metadata = get_file_metadata_batch(sorted(list(titles)))
    return metadata

def discover_glass_candidates():
    print("\n--- 2. GLASS SHATTER DISCOVERY ---")
    titles = set()
    
    # Categories
    cats = [
        "Category:Broken car windows",
        "Category:Broken automobile windows",
        "Category:Broken windshields",
        "Category:Vandalized vehicles"
    ]
    for c in cats:
        print(f"Checking category: {c}...")
        res = get_category_members(c, limit=50)
        print(f" -> Found {len(res)} files")
        titles.update(res)
        time.sleep(0.5)
        
    # Search terms (Multilingual)
    queries = [
        "broken vehicle windows",
        "shattered car glass",
        "broken windshield car",
        "cracked car windshield",
        "shattered car window",
        "pare-brise cassé",
        "zerbrochene Windschutzscheibe"
    ]
    for q in queries:
        print(f"Searching: '{q}'...")
        res = search_files_by_query(q, limit=25)
        print(f" -> Found {len(res)} files")
        titles.update(res)
        time.sleep(0.5)
        
    print(f"Total Unique Glass Candidates Identified: {len(titles)}")
    metadata = get_file_metadata_batch(sorted(list(titles)))
    return metadata

def save_manifest_csv(filepath, records):
    fields = [
        "file_title", "source_page_url", "dimensions", "author",
        "license_name", "normalized_license", "license_url",
        "is_cc0_pd_or_cc_by", "commercial_reuse_status", "required_attribution"
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in records:
            writer.writerow({k: r[k] for k in fields})
    print(f"Saved: {filepath} ({len(records)} records)")

def main():
    print("="*70)
    print("ClaimSense AI — Targeted Dataset Gap Resolution Discovery")
    print("="*70)
    
    # 1. Tire discovery
    tire_meta = discover_tire_candidates()
    approved_tires = [r for r in tire_meta if r["must_exclude"] == "FALSE"]
    excluded_tires = [r for r in tire_meta if r["must_exclude"] == "TRUE"]
    
    tire_csv = os.path.join(OUTPUT_DIR, "tire_candidates.csv")
    save_manifest_csv(tire_csv, approved_tires)
    
    # 2. Glass discovery
    glass_meta = discover_glass_candidates()
    approved_glass = [r for r in glass_meta if r["must_exclude"] == "FALSE"]
    excluded_glass = [r for r in glass_meta if r["must_exclude"] == "TRUE"]
    
    glass_csv = os.path.join(OUTPUT_DIR, "glass_candidates.csv")
    save_manifest_csv(glass_csv, approved_glass)
    
    # 3. Save Summary JSON
    summary_data = {
        "execution_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tire_flat": {
            "total_inspected": len(tire_meta),
            "approved_candidates_cc0_pd_cc_by": len(approved_tires),
            "excluded_candidates_cc_by_sa_gfdl": len(excluded_tires),
            "approved_file_sample": [r["file_title"] for r in approved_tires[:10]]
        },
        "glass_shatter": {
            "total_inspected": len(glass_meta),
            "approved_candidates_cc0_pd_cc_by": len(approved_glass),
            "excluded_candidates_cc_by_sa_gfdl": len(excluded_glass),
            "approved_file_sample": [r["file_title"] for r in approved_glass[:10]]
        }
    }
    json_path = os.path.join(OUTPUT_DIR, "gap_discovery_raw.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)
    print(f"Saved: {json_path}")
    
    print("\nTargeted Discovery Complete.")
    print(f"Tire Flat: {len(approved_tires)} approved candidates (out of {len(tire_meta)} inspected)")
    print(f"Glass Shatter: {len(approved_glass)} approved candidates (out of {len(glass_meta)} inspected)")

if __name__ == "__main__":
    main()
