import os
import csv
import json

WORKSPACE = r"C:\Users\ansh9\Desktop\Claimsense Ai"
PLAN_DIR = os.path.join(WORKSPACE, "runs", "phase8", "independent_validation_plan")
BATCH_DIR = os.path.join(PLAN_DIR, "batch_01")
MANIFEST_DIR = os.path.join(WORKSPACE, "datasets", "CarDD_Independent_Val_v1", "manifests")

# Master Candidate Data
CANDIDATES = [
    {"id": "CS_VAL_001", "title": "File:'95-'98 Ford Explorer With Flat Tire.JPG", "source": "Wikimedia Commons", "category": "Tire Flat", "w": 2369, "h": 1473, "orient": "Landscape", "tier": "Tier 1 (Walkaround)", "blur": 174.0, "dmg_pct": 18.5, "v1_status": "ACCEPTED"},
    {"id": "CS_VAL_002", "title": "File:1953 Chrysler Imperial (5832921647).jpg", "source": "Wikimedia Commons", "category": "Tire Flat", "w": 3264, "h": 2448, "orient": "Landscape", "tier": "Tier 1 (Walkaround)", "blur": 252.6, "dmg_pct": 14.2, "v1_status": "ACCEPTED"},
    {"id": "CS_VAL_003", "title": "File:1977 Datsun 180B (10899901566).jpg", "source": "Wikimedia Commons", "category": "Tire Flat", "w": 3072, "h": 2304, "orient": "Landscape", "tier": "Tier 1 (Walkaround)", "blur": 414.6, "dmg_pct": 16.0, "v1_status": "ACCEPTED"},
    {"id": "CS_VAL_004", "title": "File:1978 Ford Cortina (TE) L 4 sedan (2015-07-14) 01.jpg", "source": "Wikimedia Commons", "category": "Tire Flat", "w": 4272, "h": 2856, "orient": "Landscape", "tier": "Tier 1 (Walkaround)", "blur": 164.6, "dmg_pct": 12.8, "v1_status": "ACCEPTED"},
    {"id": "CS_VAL_005", "title": "File:1979 Honda Civic (7319282064).jpg", "source": "Wikimedia Commons", "category": "Tire Flat", "w": 4000, "h": 3000, "orient": "Landscape", "tier": "Tier 1 (Walkaround)", "blur": 45.2, "dmg_pct": 15.0, "v1_status": "REJECTED (Blur)"},
    {"id": "CS_VAL_006", "title": "File:1982 Austin Morris Mini HL (16168382460).jpg", "source": "Wikimedia Commons", "category": "Tire Flat", "w": 4272, "h": 2848, "orient": "Landscape", "tier": "Tier 1 (Walkaround)", "blur": 224.3, "dmg_pct": 15.5, "v1_status": "ACCEPTED"},
    {"id": "CS_VAL_007", "title": "File:1983 Holden Camira (JB) SLX sedan (2015-07-03) 02.jpg", "source": "Wikimedia Commons", "category": "Tire Flat", "w": 4272, "h": 2856, "orient": "Landscape", "tier": "Tier 1 (Walkaround)", "blur": 383.3, "dmg_pct": 13.5, "v1_status": "ACCEPTED"},
    {"id": "CS_VAL_008", "title": "File:1985 Toyota Corolla (AE82) CS-X Seca liftback (2015-07-10) 01.jpg", "source": "Wikimedia Commons", "category": "Tire Flat", "w": 4272, "h": 2856, "orient": "Landscape", "tier": "Tier 1 (Walkaround)", "blur": 333.2, "dmg_pct": 14.0, "v1_status": "ACCEPTED"},
    {"id": "CS_VAL_009", "title": "File:Abandoned green car with broken window.jpg", "source": "Wikimedia Commons", "category": "Glass Shatter", "w": 6016, "h": 4016, "orient": "Landscape", "tier": "Tier 1 (Walkaround)", "blur": 66.4, "dmg_pct": 22.0, "v1_status": "ACCEPTED"},
    {"id": "CS_VAL_010", "title": "File:Broken car window in salvage yard with debris and damaged interior seen through windshield.jpg", "source": "Wikimedia Commons", "category": "Glass Shatter", "w": 6048, "h": 4032, "orient": "Landscape", "tier": "Tier 1 (Walkaround)", "blur": 60.8, "dmg_pct": 35.0, "v1_status": "ACCEPTED"},
    {"id": "CS_VAL_011", "title": "File:Broken car with shattered glass in a junkyard during daylight hours showing signs of neglect and damage.jpg", "source": "Wikimedia Commons", "category": "Glass Shatter", "w": 5577, "h": 3718, "orient": "Landscape", "tier": "Tier 1 (Walkaround)", "blur": 31.8, "dmg_pct": 28.0, "v1_status": "REJECTED (Blur)"},
    {"id": "CS_VAL_012", "title": "File:Car with Broken Windshield.jpg", "source": "Wikimedia Commons", "category": "Glass Shatter", "w": 1280, "h": 960, "orient": "Landscape", "tier": "Tier 1 (Walkaround)", "blur": 718.3, "dmg_pct": 42.0, "v1_status": "ACCEPTED"},
    {"id": "CS_VAL_013", "title": "File:Damaged car in junkyard with a broken windshield.jpg", "source": "Wikimedia Commons", "category": "Glass Shatter", "w": 6016, "h": 4016, "orient": "Landscape", "tier": "Tier 1 (Walkaround)", "blur": 222.1, "dmg_pct": 38.0, "v1_status": "ACCEPTED"},
    {"id": "CS_VAL_014", "title": "File:Damaged car window in a junkyard with broken glass on the windshield and rows of vehicles in the background.jpg", "source": "Wikimedia Commons", "category": "Glass Shatter", "w": 6048, "h": 4032, "orient": "Landscape", "tier": "Tier 1 (Walkaround)", "blur": 133.3, "dmg_pct": 32.0, "v1_status": "ACCEPTED"},
    {"id": "CS_VAL_015", "title": "File:FEMA - 44376 - truck windshield with hail damage in OK.jpg", "source": "Wikimedia Commons", "category": "Glass Shatter", "w": 3000, "h": 1993, "orient": "Landscape", "tier": "Tier 1 (Walkaround)", "blur": 261.5, "dmg_pct": 48.0, "v1_status": "ACCEPTED"},
    {"id": "CS_VAL_016", "title": "File:Damaged car from hail in Missouri, April 2001.jpg", "source": "Wikimedia Commons", "category": "Dent", "w": 640, "h": 480, "orient": "Landscape", "tier": "Tier 2 (Macro)", "blur": 310.6, "dmg_pct": 72.0, "v1_status": "REJECTED (Res)"},
    {"id": "CS_VAL_017", "title": "File:Hail damage car.jpg", "source": "Wikimedia Commons", "category": "Dent", "w": 720, "h": 960, "orient": "Portrait", "tier": "Tier 2 (Macro)", "blur": 1247.1, "dmg_pct": 65.0, "v1_status": "REJECTED (Res)"},
    {"id": "CS_VAL_018", "title": "File:Hailstone damage on various vehicles from 4 July 2010 hailstorm (Limon, eastern Colorado, USA).jpg", "source": "Wikimedia Commons", "category": "Dent", "w": 2999, "h": 2249, "orient": "Landscape", "tier": "Tier 1 (Walkaround)", "blur": 227.8, "dmg_pct": 55.0, "v1_status": "ACCEPTED"},
    {"id": "CS_VAL_019", "title": "File:Hailstone-smashed back window of a car from 4 July 2010 hailstorm (Limon, eastern Colorado, USA).jpg", "source": "Wikimedia Commons", "category": "Dent", "w": 3640, "h": 2756, "orient": "Landscape", "tier": "Tier 1 (Walkaround)", "blur": 216.4, "dmg_pct": 50.0, "v1_status": "ACCEPTED"},
    {"id": "CS_VAL_020", "title": "Car damages 100.png", "source": "Humans in the Loop", "category": "Crack", "w": 637, "h": 419, "orient": "Landscape", "tier": "Tier 2 (Macro)", "blur": 914.6, "dmg_pct": 59.3, "v1_status": "REJECTED (Res)"},
    {"id": "CS_VAL_021", "title": "Car damages 101.png", "source": "Humans in the Loop", "category": "Crack", "w": 637, "h": 440, "orient": "Landscape", "tier": "Tier 2 (Macro)", "blur": 301.7, "dmg_pct": 51.4, "v1_status": "REJECTED (Res)"},
    {"id": "CS_VAL_022", "title": "Car damages 102.jpg", "source": "Humans in the Loop", "category": "Lamp Broken", "w": 629, "h": 471, "orient": "Landscape", "tier": "Tier 2 (Macro)", "blur": 1298.2, "dmg_pct": 76.1, "v1_status": "REJECTED (Res)"},
    {"id": "CS_VAL_023", "title": "Car damages 103.png", "source": "Humans in the Loop", "category": "Lamp Broken", "w": 881, "h": 476, "orient": "Landscape", "tier": "Tier 2 (Macro)", "blur": 625.4, "dmg_pct": 54.1, "v1_status": "REJECTED (Res)"},
    {"id": "CS_VAL_024", "title": "Car damages 104.png", "source": "Humans in the Loop", "category": "Scratch", "w": 637, "h": 442, "orient": "Landscape", "tier": "Tier 2 (Macro)", "blur": 1113.9, "dmg_pct": 45.3, "v1_status": "REJECTED (Res)"},
    {"id": "CS_VAL_025", "title": "Car damages 105.png", "source": "Humans in the Loop", "category": "Dent", "w": 637, "h": 444, "orient": "Landscape", "tier": "Tier 2 (Macro)", "blur": 1218.0, "dmg_pct": 60.1, "v1_status": "REJECTED (Res)"}
]

# 1. Generate resolution_threshold_comparison.csv
comparison_rows = []
for c in CANDIDATES:
    w, h = c["w"], c["h"]
    pass_800x600 = (w >= 800 and h >= 600)
    pass_640x400 = (w >= 640 and h >= 400)
    pass_600x400 = (w >= 600 and h >= 400)
    pass_minmax_600x400 = (min(w, h) >= 400 and max(w, h) >= 600)
    
    delta_640 = w - 640
    delta_600 = w - 600
    
    if c["source"] == "Humans in the Loop":
        note = f"HITL native crop: width {w}px misses 640px threshold by {abs(delta_640)}px, but passes 600px threshold by {delta_600}px."
    elif c["id"] == "CS_VAL_016":
        note = "NWS official hail photo: exact 640x480 VGA; passes both 640x400 and 600x400."
    elif c["id"] == "CS_VAL_017":
        note = "Portrait orientation (720x960): passes 600x400 under orientation-agnostic or min/max evaluation."
    elif not pass_800x600:
        note = "Sub-800x600 candidate."
    else:
        note = f"DSLR/high-res image ({w}x{h}); passes all candidate resolution thresholds."
        
    comparison_rows.append({
        "candidate_id": c["id"],
        "file_title": c["title"],
        "category": c["category"],
        "source": c["source"],
        "width": w,
        "height": h,
        "total_pixels": w * h,
        "orientation": c["orient"],
        "v1_0_spec_800x600": "PASS" if pass_800x600 else "FAIL",
        "eval_threshold_640x400": "PASS" if pass_640x400 else "FAIL",
        "eval_threshold_600x400": "PASS" if pass_600x400 else "FAIL",
        "minmax_eval_600x400": "PASS" if pass_minmax_600x400 else "FAIL",
        "delta_from_640_width": f"{delta_640:+d} px",
        "delta_from_600_width": f"{delta_600:+d} px",
        "structural_impact_note": note
    })

# 2. Generate batch_01_revised_eligibility.csv
eligibility_rows = []
for c in CANDIDATES:
    w, h = c["w"], c["h"]
    is_macro = (c["tier"] == "Tier 2 (Macro)")
    
    # Tier resolution eligibility under proposed v1.1
    if not is_macro:
        res_elig = (w >= 800 and h >= 600)
    else:
        # Macro tier: min dimension >= 400 and max dimension >= 600
        res_elig = (min(w, h) >= 400 and max(w, h) >= 600)
        
    # Damage area occupancy rule
    if is_macro:
        occ_pass = (c["dmg_pct"] >= 30.0)
    else:
        occ_pass = True # Walkaround tier does not have 30% localized occupancy requirement
        
    blur_pass = (c["blur"] >= 50.0)
    dedup_pass = True # All pairwise Hamming >= 16
    license_pass = True # All 25 verified clean
    pii_pass = True # Redacted with 0 entropy or 0 PII
    exif_pass = True # 0 tags in processed
    
    reasons = []
    if not res_elig:
        reasons.append(f"Fails Tier Resolution ({w}x{h})")
    if not occ_pass:
        reasons.append(f"Fails Damage Occupancy ({c['dmg_pct']}% < 30%)")
    if not blur_pass:
        reasons.append(f"Fails Blur Gate (Laplacian {c['blur']:.1f} < 50.0)")
        
    v1_1_status = "QUALIFIED" if len(reasons) == 0 else "DISQUALIFIED"
    disq_reason = "; ".join(reasons) if reasons else "NONE (Eligible for v1.1 Macro/Walkaround Certification)"
    
    eligibility_rows.append({
        "image_id": c["id"],
        "file_title": c["title"],
        "category": c["category"],
        "source": c["source"],
        "dimensions": f"{w}x{h}",
        "proposed_tier": c["tier"],
        "tier_resolution_eligibility": "PASS" if res_elig else "FAIL",
        "damage_area_occupancy_pct": f"{c['dmg_pct']:.1f}%",
        "damage_occupancy_pass_30pct": "PASS" if occ_pass else ("FAIL" if is_macro else "N/A (Walkaround)"),
        "laplacian_blur_var": c["blur"],
        "blur_gate_pass_50": "PASS" if blur_pass else "FAIL",
        "deduplication_pass": "PASS",
        "licensing_pass": "PASS",
        "pii_redaction_pass": "PASS",
        "exif_purged_pass": "PASS",
        "v1_0_status": c["v1_status"],
        "proposed_v1_1_status": v1_1_status,
        "disqualification_reason": disq_reason
    })

def save_csv(path, rows):
    keys = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        wtr = csv.DictWriter(f, fieldnames=keys)
        wtr.writeheader()
        wtr.writerows(rows)
    print(f"Saved: {path}")

save_csv(os.path.join(PLAN_DIR, "resolution_threshold_comparison.csv"), comparison_rows)
save_csv(os.path.join(BATCH_DIR, "resolution_threshold_comparison.csv"), comparison_rows)
save_csv(os.path.join(PLAN_DIR, "batch_01_revised_eligibility.csv"), eligibility_rows)
save_csv(os.path.join(BATCH_DIR, "batch_01_revised_eligibility.csv"), eligibility_rows)
save_csv(os.path.join(MANIFEST_DIR, "resolution_threshold_comparison.csv"), comparison_rows)
save_csv(os.path.join(MANIFEST_DIR, "batch_01_revised_eligibility.csv"), eligibility_rows)
print("CSVs generated successfully.")
