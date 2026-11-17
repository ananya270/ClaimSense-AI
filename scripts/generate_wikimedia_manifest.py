"""
scripts/generate_wikimedia_manifest.py
Query the official Wikimedia Commons MediaWiki Action API for candidate damage categories.
Extracts file-level license metadata, classifies CC0/PD/CC-BY vs CC BY-SA/GFDL/unknown,
and generates audit artifacts without downloading image binaries.
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
    "runs", "phase8", "independent_validation_plan", "source_discovery", "final_readiness_audit", "review_03"
)
os.makedirs(OUTPUT_DIR, exist_ok=True)

CATEGORIES = [
    ("Category:Flat_tires", "tire_flat", 40),
    ("Category:Broken_car_windows", "glass_shatter", 30),
    ("Category:Automobile_hail_damage", "dent_hail", 30),
    ("Category:Damaged_automobiles", "collision_general", 40),
]

USER_AGENT = "ClaimSenseAuditBot/2.0 (claimsense-ai-research; contact@claimsense.ai)"

def clean_html(raw_html):
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', str(raw_html))
    return cleantext.strip().replace('\n', ' ').replace('\r', '')

def query_category(category_name, category_focus, max_items=40):
    base_url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "categorymembers",
        "gcmtitle": category_name,
        "gcmnamespace": "6",  # File namespace
        "gcmlimit": str(min(max_items, 50)),
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|user|size",
        "format": "json"
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error querying {category_name}: {e}", file=sys.stderr)
        return []

    pages = data.get("query", {}).get("pages", {})
    records = []

    for page_id, page_data in pages.items():
        title = page_data.get("title", "")
        imageinfo = page_data.get("imageinfo", [{}])[0]
        file_url = imageinfo.get("descriptionurl", f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(title)}")
        direct_url = imageinfo.get("url", "")
        user = imageinfo.get("user", "")
        width = imageinfo.get("width", 0)
        height = imageinfo.get("height", 0)

        extmetadata = imageinfo.get("extmetadata", {})
        license_short = extmetadata.get("LicenseShortName", {}).get("value", "")
        license_url = extmetadata.get("LicenseUrl", {}).get("value", "")
        artist_raw = extmetadata.get("Artist", {}).get("value", user)
        artist = clean_html(artist_raw) or user
        credit_raw = extmetadata.get("Credit", {}).get("value", "")
        credit = clean_html(credit_raw)
        usage_terms = extmetadata.get("UsageTerms", {}).get("value", "")
        attribution_req = extmetadata.get("AttributionRequired", {}).get("value", "")

        lic_lower = license_short.lower()
        lic_url_lower = license_url.lower()

        is_cc0 = "cc0" in lic_lower or "zero" in lic_lower or "public domain" in lic_lower or "pd" == lic_lower
        is_cc_by = ("cc by" in lic_lower or "cc-by" in lic_lower) and not ("sa" in lic_lower or "sharealike" in lic_lower)
        is_cc_by_sa = "sa" in lic_lower or "sharealike" in lic_lower or "share alike" in lic_lower or "by-sa" in lic_url_lower
        is_gfdl = "gfdl" in lic_lower or "gnu" in lic_lower

        if is_cc0:
            classification = "APPROVED_CANDIDATE"
            norm_license = "CC0 / Public Domain"
            commercial_status = "PERMITTED"
            exclude = False
            exclusion_reason = "NONE"
            attribution_text = f"Public domain / CC0 dedication (Uploaded by {user} to Wikimedia Commons)"
        elif is_cc_by:
            classification = "APPROVED_CANDIDATE"
            norm_license = license_short
            commercial_status = "PERMITTED"
            exclude = False
            exclusion_reason = "NONE"
            attribution_text = f"Photo by {artist}, Wikimedia Commons, {license_short} ({license_url})"
        elif is_cc_by_sa:
            classification = "EXCLUDED"
            norm_license = license_short
            commercial_status = "CONDITIONAL_SHARE_ALIKE"
            exclude = True
            exclusion_reason = "COPYLEFT_SHARE_ALIKE_DISQUALIFIED (Model weight derivation ambiguity)"
            attribution_text = f"Photo by {artist}, Wikimedia Commons, {license_short}"
        elif is_gfdl:
            classification = "EXCLUDED"
            norm_license = license_short
            commercial_status = "RESTRICTIVE_COPYLEFT"
            exclude = True
            exclusion_reason = "GFDL_COPYLEFT_DISQUALIFIED"
            attribution_text = f"Photo by {artist}, {license_short}"
        else:
            classification = "EXCLUDED"
            norm_license = license_short or "Unknown"
            commercial_status = "UNVERIFIED"
            exclude = True
            exclusion_reason = f"UNKNOWN_OR_UNVERIFIED_LICENSE ({license_short})"
            attribution_text = f"Unknown / {user}"

        records.append({
            "category": category_name,
            "damage_focus": category_focus,
            "file_title": title,
            "source_page_url": file_url,
            "direct_image_url": direct_url,
            "dimensions": f"{width}x{height}",
            "author": artist,
            "license_name": license_short,
            "normalized_license": norm_license,
            "license_url": license_url,
            "is_cc0_pd_or_cc_by": "TRUE" if (is_cc0 or is_cc_by) else "FALSE",
            "commercial_reuse_status": commercial_status,
            "must_exclude": "TRUE" if exclude else "FALSE",
            "exclusion_reason": exclusion_reason,
            "required_attribution": attribution_text
        })
        
        if len(records) >= max_items:
            break

    return records

def main():
    print("Initiating Wikimedia Commons MediaWiki API Query (Read-Only)...")
    all_records = []
    for cat_name, focus, limit in CATEGORIES:
        print(f"Querying {cat_name} (limit={limit})...")
        recs = query_category(cat_name, focus, limit)
        print(f" -> Found {len(recs)} files in {cat_name}")
        all_records.extend(recs)
        time.sleep(1)  # Respect API polite rate limits

    approved = [r for r in all_records if r["must_exclude"] == "FALSE"]
    excluded = [r for r in all_records if r["must_exclude"] == "TRUE"]

    print(f"\nTotal Files Audited: {len(all_records)}")
    print(f"Approved (CC0 / PD / CC BY): {len(approved)}")
    print(f"Excluded (CC BY-SA / GFDL / Unknown): {len(excluded)}")

    # 1. Candidate manifest
    cand_path = os.path.join(OUTPUT_DIR, "wikimedia_candidate_manifest.csv")
    fieldnames = [
        "file_title", "damage_focus", "category", "source_page_url", "dimensions",
        "author", "license_name", "normalized_license", "license_url",
        "is_cc0_pd_or_cc_by", "commercial_reuse_status", "required_attribution"
    ]
    with open(cand_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in approved:
            row = {k: r[k] for k in fieldnames}
            writer.writerow(row)
    print(f"Saved: {cand_path}")

    # 2. Excluded manifest
    excl_path = os.path.join(OUTPUT_DIR, "wikimedia_excluded_files.csv")
    excl_fields = [
        "file_title", "category", "source_page_url", "author",
        "license_name", "exclusion_reason"
    ]
    with open(excl_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=excl_fields)
        writer.writeheader()
        for r in excluded:
            row = {k: r[k] for k in excl_fields}
            writer.writerow(row)
    print(f"Saved: {excl_path}")

    # 3. Summary Markdown
    sum_path = os.path.join(OUTPUT_DIR, "wikimedia_license_summary.md")
    with open(sum_path, "w", encoding="utf-8") as f:
        f.write("# ClaimSense AI — Wikimedia Commons License & Candidate Summary\n\n")
        f.write(f"**Audit Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**API Endpoint:** `https://commons.wikimedia.org/w/api.php`\n")
        f.write(f"**Execution Mode:** Strictly Read-Only API Query (Zero Binaries Downloaded)\n\n")
        f.write("## 1. Audit Summary Statistics\n\n")
        f.write(f"- **Total Candidate Files Audited:** {len(all_records)}\n")
        f.write(f"- **Approved Files (CC0, Public Domain, or CC BY):** {len(approved)}\n")
        f.write(f"- **Excluded Files (CC BY-SA, GFDL, Unknown):** {len(excluded)}\n")
        f.write(f"- **Exclusion Rate:** {(len(excluded)/len(all_records)*100 if all_records else 0):.1f}%\n\n")
        f.write("## 2. Category Breakdown\n\n")
        f.write("| Category | Focus | Audited | Approved (CC0/CC-BY) | Excluded (CC BY-SA/GFDL) |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: |\n")
        for cat_name, focus, _ in CATEGORIES:
            cat_all = [r for r in all_records if r["category"] == cat_name]
            cat_app = [r for r in cat_all if r["must_exclude"] == "FALSE"]
            cat_exc = [r for r in cat_all if r["must_exclude"] == "TRUE"]
            f.write(f"| `{cat_name}` | {focus} | {len(cat_all)} | **{len(cat_app)}** | {len(cat_exc)} |\n")
        f.write("\n## 3. Approved Candidates Overview\n\n")
        f.write("Approved candidates satisfy all of the following criteria:\n")
        f.write("1. Documented license is strictly **CC0 1.0, Public Domain, or CC BY (2.0, 2.5, 3.0, 4.0)**.\n")
        f.write("2. No copyleft / Share-Alike (SA) provisions that could trigger model weight licensing debates.\n")
        f.write("3. Commercial computational evaluation is explicitly permitted.\n")
        f.write("4. Required attribution strings are recorded in `wikimedia_candidate_manifest.csv`.\n\n")
        f.write("## 4. Exclusion Rationale\n\n")
        f.write("All excluded files in `wikimedia_excluded_files.csv` carry:\n")
        f.write("- **CC BY-SA 3.0 / 4.0:** Excluded under the precautionary principle regarding neural network weight derivations.\n")
        f.write("- **GFDL:** Excluded due to documentation-focused terms and burdensome reprint/distribution requirements.\n")
        f.write("- **Unknown / Unspecified:** Excluded due to missing machine-readable metadata in MediaWiki `extmetadata`.\n")
    print(f"Saved: {sum_path}")

if __name__ == "__main__":
    main()
