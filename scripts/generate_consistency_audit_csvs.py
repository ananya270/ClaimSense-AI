import os
import csv
import json

WORKSPACE = r"C:\Users\ansh9\Desktop\Claimsense Ai"
PLAN_DIR = os.path.join(WORKSPACE, "runs", "phase8", "independent_validation_plan")
BATCH_DIR = os.path.join(PLAN_DIR, "batch_01")
MANIFEST_DIR = os.path.join(WORKSPACE, "datasets", "CarDD_Independent_Val_v1", "manifests")

# 1. Corrected Tier Classification CSV Data
# Reconcile all 25 candidate IDs against proposed v1.1 resolution rules
CANDIDATES = [
    {"id": "CS_VAL_001", "title": "File:'95-'98 Ford Explorer With Flat Tire.JPG", "source": "Wikimedia Commons", "category": "Tire Flat", "w": 2369, "h": 1473, "orient": "Landscape", "v1_0_status": "ACCEPTED", "v1_1_tier": "Tier 1 (Walkaround)", "v1_1_status": "QUALIFIED", "res_rule": "Width >= 800 AND Height >= 600", "stance": "Full-vehicle rear 3/4 walkaround view"},
    {"id": "CS_VAL_002", "title": "File:1953 Chrysler Imperial (5832921647).jpg", "source": "Wikimedia Commons", "category": "Tire Flat", "w": 3264, "h": 2448, "orient": "Landscape", "v1_0_status": "ACCEPTED", "v1_1_tier": "Tier 1 (Walkaround)", "v1_1_status": "QUALIFIED", "res_rule": "Width >= 800 AND Height >= 600", "stance": "Full-vehicle front 3/4 walkaround view"},
    {"id": "CS_VAL_003", "title": "File:1977 Datsun 180B (10899901566).jpg", "source": "Wikimedia Commons", "category": "Tire Flat", "w": 3072, "h": 2304, "orient": "Landscape", "v1_0_status": "ACCEPTED", "v1_1_tier": "Tier 1 (Walkaround)", "v1_1_status": "QUALIFIED", "res_rule": "Width >= 800 AND Height >= 600", "stance": "Full-vehicle front 3/4 walkaround view"},
    {"id": "CS_VAL_004", "title": "File:1978 Ford Cortina (TE) L 4 sedan (2015-07-14) 01.jpg", "source": "Wikimedia Commons", "category": "Tire Flat", "w": 4272, "h": 2856, "orient": "Landscape", "v1_0_status": "ACCEPTED", "v1_1_tier": "Tier 1 (Walkaround)", "v1_1_status": "QUALIFIED", "res_rule": "Width >= 800 AND Height >= 600", "stance": "Full-vehicle rear 3/4 walkaround view"},
    {"id": "CS_VAL_005", "title": "File:1979 Honda Civic (7319282064).jpg", "source": "Wikimedia Commons", "category": "Tire Flat", "w": 4000, "h": 3000, "orient": "Landscape", "v1_0_status": "REJECTED (Blur)", "v1_1_tier": "Disqualified (Blur)", "v1_1_status": "DISQUALIFIED", "res_rule": "Width >= 800 AND Height >= 600 (Failed Blur Gate: 45.2 < 50.0)", "stance": "Full-vehicle front walkaround view"},
    {"id": "CS_VAL_006", "title": "File:1982 Austin Morris Mini HL (16168382460).jpg", "source": "Wikimedia Commons", "category": "Tire Flat", "w": 4272, "h": 2848, "orient": "Landscape", "v1_0_status": "ACCEPTED", "v1_1_tier": "Tier 1 (Walkaround)", "v1_1_status": "QUALIFIED", "res_rule": "Width >= 800 AND Height >= 600", "stance": "Full-vehicle front 3/4 walkaround view"},
    {"id": "CS_VAL_007", "title": "File:1983 Holden Camira (JB) SLX sedan (2015-07-03) 02.jpg", "source": "Wikimedia Commons", "category": "Tire Flat", "w": 4272, "h": 2856, "orient": "Landscape", "v1_0_status": "ACCEPTED", "v1_1_tier": "Tier 1 (Walkaround)", "v1_1_status": "QUALIFIED", "res_rule": "Width >= 800 AND Height >= 600", "stance": "Full-vehicle rear 3/4 walkaround view"},
    {"id": "CS_VAL_008", "title": "File:1985 Toyota Corolla (AE82) CS-X Seca liftback (2015-07-10) 01.jpg", "source": "Wikimedia Commons", "category": "Tire Flat", "w": 4272, "h": 2856, "orient": "Landscape", "v1_0_status": "ACCEPTED", "v1_1_tier": "Tier 1 (Walkaround)", "v1_1_status": "QUALIFIED", "res_rule": "Width >= 800 AND Height >= 600", "stance": "Full-vehicle front 3/4 walkaround view"},
    {"id": "CS_VAL_009", "title": "File:Abandoned green car with broken window.jpg", "source": "Wikimedia Commons", "category": "Glass Shatter", "w": 6016, "h": 4016, "orient": "Landscape", "v1_0_status": "ACCEPTED", "v1_1_tier": "Tier 1 (Walkaround)", "v1_1_status": "QUALIFIED", "res_rule": "Width >= 800 AND Height >= 600", "stance": "Full-vehicle side profile walkaround view"},
    {"id": "CS_VAL_010", "title": "File:Broken car window in salvage yard with debris and damaged interior seen through windshield.jpg", "source": "Wikimedia Commons", "category": "Glass Shatter", "w": 6048, "h": 4032, "orient": "Landscape", "v1_0_status": "ACCEPTED", "v1_1_tier": "Tier 1 (Walkaround)", "v1_1_status": "QUALIFIED", "res_rule": "Width >= 800 AND Height >= 600", "stance": "Multi-component front cabin / windshield view"},
    {"id": "CS_VAL_011", "title": "File:Broken car with shattered glass in a junkyard during daylight hours showing signs of neglect and damage.jpg", "source": "Wikimedia Commons", "category": "Glass Shatter", "w": 5577, "h": 3718, "orient": "Landscape", "v1_0_status": "REJECTED (Blur)", "v1_1_tier": "Disqualified (Blur)", "v1_1_status": "DISQUALIFIED", "res_rule": "Width >= 800 AND Height >= 600 (Failed Blur Gate: 31.8 < 50.0)", "stance": "Multi-component side window view"},
    {"id": "CS_VAL_012", "title": "File:Car with Broken Windshield.jpg", "source": "Wikimedia Commons", "category": "Glass Shatter", "w": 1280, "h": 960, "orient": "Landscape", "v1_0_status": "ACCEPTED", "v1_1_tier": "Tier 1 (Walkaround)", "v1_1_status": "QUALIFIED", "res_rule": "Width >= 800 AND Height >= 600", "stance": "Full front windshield and hood assembly view"},
    {"id": "CS_VAL_013", "title": "File:Damaged car in junkyard with a broken windshield.jpg", "source": "Wikimedia Commons", "category": "Glass Shatter", "w": 6016, "h": 4016, "orient": "Landscape", "v1_0_status": "ACCEPTED", "v1_1_tier": "Tier 1 (Walkaround)", "v1_1_status": "QUALIFIED", "res_rule": "Width >= 800 AND Height >= 600", "stance": "Front windshield and A-pillar assembly view"},
    {"id": "CS_VAL_014", "title": "File:Damaged car window in a junkyard with broken glass on the windshield and rows of vehicles in the background.jpg", "source": "Wikimedia Commons", "category": "Glass Shatter", "w": 6048, "h": 4032, "orient": "Landscape", "v1_0_status": "ACCEPTED", "v1_1_tier": "Tier 1 (Walkaround)", "v1_1_status": "QUALIFIED", "res_rule": "Width >= 800 AND Height >= 600", "stance": "Multi-vehicle junkyard windshield view"},
    {"id": "CS_VAL_015", "title": "File:FEMA - 44376 - truck windshield with hail damage in OK.jpg", "source": "Wikimedia Commons", "category": "Glass Shatter", "w": 3000, "h": 1993, "orient": "Landscape", "v1_0_status": "ACCEPTED", "v1_1_tier": "Tier 1 (Walkaround)", "v1_1_status": "QUALIFIED", "res_rule": "Width >= 800 AND Height >= 600", "stance": "Truck cab and windshield assembly view"},
    {"id": "CS_VAL_016", "title": "File:Damaged car from hail in Missouri, April 2001.jpg", "source": "Wikimedia Commons", "category": "Dent", "w": 640, "h": 480, "orient": "Landscape", "v1_0_status": "REJECTED (Res)", "v1_1_tier": "Tier 2 (Macro)", "v1_1_status": "QUALIFIED", "res_rule": "min(w,h) >= 400 and max(w,h) >= 600; Damage >= 30%", "stance": "Close-up macro inspection of hail dimples on car hood"},
    {"id": "CS_VAL_017", "title": "File:Hail damage car.jpg", "source": "Wikimedia Commons", "category": "Dent", "w": 720, "h": 960, "orient": "Portrait", "v1_0_status": "REJECTED (Res)", "v1_1_tier": "Tier 2 (Macro)", "v1_1_status": "QUALIFIED", "res_rule": "min(w,h) >= 400 and max(w,h) >= 600; Damage >= 30%", "stance": "Close-up portrait macro inspection of hail-dented car roof/hood"},
    {"id": "CS_VAL_018", "title": "File:Hailstone damage on various vehicles from 4 July 2010 hailstorm (Limon, eastern Colorado, USA).jpg", "source": "Wikimedia Commons", "category": "Dent", "w": 2999, "h": 2249, "orient": "Landscape", "v1_0_status": "ACCEPTED", "v1_1_tier": "Tier 1 (Walkaround)", "v1_1_status": "QUALIFIED", "res_rule": "Width >= 800 AND Height >= 600", "stance": "Full hood, windshield and roof hail inspection view"},
    {"id": "CS_VAL_019", "title": "File:Hailstone-smashed back window of a car from 4 July 2010 hailstorm (Limon, eastern Colorado, USA).jpg", "source": "Wikimedia Commons", "category": "Dent", "w": 3640, "h": 2756, "orient": "Landscape", "v1_0_status": "ACCEPTED", "v1_1_tier": "Tier 1 (Walkaround)", "v1_1_status": "QUALIFIED", "res_rule": "Width >= 800 AND Height >= 600", "stance": "Rear windshield and trunk lid assembly view"},
    {"id": "CS_VAL_020", "title": "Car damages 100.png", "source": "Humans in the Loop", "category": "Crack", "w": 637, "h": 419, "orient": "Landscape", "v1_0_status": "REJECTED (Res)", "v1_1_tier": "Tier 2 (Macro)", "v1_1_status": "QUALIFIED", "res_rule": "min(w,h) >= 400 and max(w,h) >= 600; Damage >= 30%", "stance": "Close-up macro crop of cracked plastic bumper lip"},
    {"id": "CS_VAL_021", "title": "Car damages 101.png", "source": "Humans in the Loop", "category": "Crack", "w": 637, "h": 440, "orient": "Landscape", "v1_0_status": "REJECTED (Res)", "v1_1_tier": "Tier 2 (Macro)", "v1_1_status": "QUALIFIED", "res_rule": "min(w,h) >= 400 and max(w,h) >= 600; Damage >= 30%", "stance": "Close-up macro crop of fractured rear bumper flange"},
    {"id": "CS_VAL_022", "title": "Car damages 102.jpg", "source": "Humans in the Loop", "category": "Lamp Broken", "w": 629, "h": 471, "orient": "Landscape", "v1_0_status": "REJECTED (Res)", "v1_1_tier": "Tier 2 (Macro)", "v1_1_status": "QUALIFIED", "res_rule": "min(w,h) >= 400 and max(w,h) >= 600; Damage >= 30%", "stance": "Close-up macro crop of smashed front headlight lens"},
    {"id": "CS_VAL_023", "title": "Car damages 103.png", "source": "Humans in the Loop", "category": "Lamp Broken", "w": 881, "h": 476, "orient": "Landscape", "v1_0_status": "REJECTED (Res)", "v1_1_tier": "Tier 2 (Macro)", "v1_1_status": "QUALIFIED", "res_rule": "min(w,h) >= 400 and max(w,h) >= 600; Damage >= 30%", "stance": "Close-up macro crop of broken red taillight assembly"},
    {"id": "CS_VAL_024", "title": "Car damages 104.png", "source": "Humans in the Loop", "category": "Scratch", "w": 637, "h": 442, "orient": "Landscape", "v1_0_status": "REJECTED (Res)", "v1_1_tier": "Tier 2 (Macro)", "v1_1_status": "QUALIFIED", "res_rule": "min(w,h) >= 400 and max(w,h) >= 600; Damage >= 30%", "stance": "Close-up macro crop of longitudinal door panel key scratch"},
    {"id": "CS_VAL_025", "title": "Car damages 105.png", "source": "Humans in the Loop", "category": "Dent", "w": 637, "h": 444, "orient": "Landscape", "v1_0_status": "REJECTED (Res)", "v1_1_tier": "Tier 2 (Macro)", "v1_1_status": "QUALIFIED", "res_rule": "min(w,h) >= 400 and max(w,h) >= 600; Damage >= 30%", "stance": "Close-up macro crop of concave front fender impact dent"}
]

tier_rows = []
for c in CANDIDATES:
    tier_rows.append({
        "candidate_id": c["id"],
        "file_title": c["title"],
        "damage_category": c["category"],
        "source_repository": c["source"],
        "width_px": c["w"],
        "height_px": c["h"],
        "orientation": c["orient"],
        "v1_0_status": c["v1_0_status"],
        "proposed_v1_1_tier": c["v1_1_tier"],
        "proposed_v1_1_status": c["v1_1_status"],
        "applicable_resolution_rule": c["res_rule"],
        "visual_stance_classification": c["stance"]
    })

# 2. Macro Quota Scenarios CSV Data
quota_rows = [
    {
        "scenario_name": "Batch 1 Actual Status Quo",
        "total_dataset_size": 23,
        "tier_1_count": 15,
        "tier_2_count": 8,
        "actual_macro_percentage": "34.78%",
        "quota_ceiling": "30.00%",
        "quota_compliance": "EXCEEDS_QUOTA (+4.78%)",
        "additional_tier_1_needed": 4,
        "notes": "In Batch 1 alone, 8/23 exceeds 30%. Requires 4 more Tier 1 images to achieve <= 30%."
    },
    {
        "scenario_name": "Minimum Compliant Dataset Size",
        "total_dataset_size": 27,
        "tier_1_count": 19,
        "tier_2_count": 8,
        "actual_macro_percentage": "29.63%",
        "quota_ceiling": "30.00%",
        "quota_compliance": "COMPLIANT",
        "additional_tier_1_needed": 4,
        "notes": "Smallest dataset size that absorbs all 8 Batch 1 macro images within 30% ceiling."
    },
    {
        "scenario_name": "Full Target N=200 (Max 30% Macro)",
        "total_dataset_size": 200,
        "tier_1_count": 140,
        "tier_2_count": 60,
        "actual_macro_percentage": "30.00%",
        "quota_ceiling": "30.00%",
        "quota_compliance": "COMPLIANT",
        "additional_tier_1_needed": 125,
        "notes": "Final N=200 utilizing full 30% macro allowance. Requires 125 more Tier 1 and 52 more Tier 2."
    },
    {
        "scenario_name": "Full Target N=200 (Frozen Macro = 8)",
        "total_dataset_size": 200,
        "tier_1_count": 192,
        "tier_2_count": 8,
        "actual_macro_percentage": "4.00%",
        "quota_ceiling": "30.00%",
        "quota_compliance": "COMPLIANT",
        "additional_tier_1_needed": 177,
        "notes": "No further macro acquisitions after Batch 1. Requires 177 more Tier 1 images."
    },
    {
        "scenario_name": "Target N=220 (Max 30% Macro)",
        "total_dataset_size": 220,
        "tier_1_count": 154,
        "tier_2_count": 66,
        "actual_macro_percentage": "30.00%",
        "quota_ceiling": "30.00%",
        "quota_compliance": "COMPLIANT",
        "additional_tier_1_needed": 139,
        "notes": "Midpoint target N=220 utilizing full 30% macro quota. Requires 139 more Tier 1 images."
    },
    {
        "scenario_name": "Target N=220 (Frozen Macro = 8)",
        "total_dataset_size": 220,
        "tier_1_count": 212,
        "tier_2_count": 8,
        "actual_macro_percentage": "3.64%",
        "quota_ceiling": "30.00%",
        "quota_compliance": "COMPLIANT",
        "additional_tier_1_needed": 197,
        "notes": "Midpoint target N=220 with no further macro acquisitions. Requires 197 more Tier 1 images."
    },
    {
        "scenario_name": "Upper Target N=250 (Max 30% Macro)",
        "total_dataset_size": 250,
        "tier_1_count": 175,
        "tier_2_count": 75,
        "actual_macro_percentage": "30.00%",
        "quota_ceiling": "30.00%",
        "quota_compliance": "COMPLIANT",
        "additional_tier_1_needed": 160,
        "notes": "Upper bound target N=250 utilizing full 30% macro quota. Requires 160 more Tier 1 images."
    },
    {
        "scenario_name": "Upper Target N=250 (Frozen Macro = 8)",
        "total_dataset_size": 250,
        "tier_1_count": 242,
        "tier_2_count": 8,
        "actual_macro_percentage": "3.20%",
        "quota_ceiling": "30.00%",
        "quota_compliance": "COMPLIANT",
        "additional_tier_1_needed": 227,
        "notes": "Upper bound target N=250 with no further macro acquisitions. Requires 227 more Tier 1 images."
    }
]

# 3. Occupancy Evidence Audit CSV Data
# Detail exact derivation of occupancy, flags, evidence source
occupancy_rows = [
    {
        "candidate_id": "CS_VAL_016",
        "category": "Dent",
        "source": "Wikimedia Commons (FEMA/NWS)",
        "dimensions": "640x480",
        "total_image_pixels": 307200,
        "reported_occupancy_pct": "72.0%",
        "calculation_method": "Axis-Aligned Bounding Box (AABB) Approximation [40, 30, 600, 450]",
        "source_of_evidence": "Pre-screening heuristic visual estimate by script author",
        "upstream_annotation_exists": "NO (FEMA public archive does not provide bounding box JSON)",
        "substantiation_status": "PROVISIONAL_ESTIMATE",
        "passes_30pct_threshold": "PASS (High Confidence - multi-dent hail covers full hood)",
        "governance_flag": "FLAG-01: Provisional visual estimate; must be validated during formal blind annotation."
    },
    {
        "candidate_id": "CS_VAL_017",
        "category": "Dent",
        "source": "Wikimedia Commons (Simiprof)",
        "dimensions": "720x960",
        "total_image_pixels": 691200,
        "reported_occupancy_pct": "65.0%",
        "calculation_method": "Axis-Aligned Bounding Box (AABB) Approximation [60, 80, 660, 880]",
        "source_of_evidence": "Pre-screening heuristic visual estimate by script author",
        "upstream_annotation_exists": "NO (Wikimedia Commons community upload does not provide JSON)",
        "substantiation_status": "PROVISIONAL_ESTIMATE",
        "passes_30pct_threshold": "PASS (High Confidence - roof denting spans 65% of vertical frame)",
        "governance_flag": "FLAG-01: Provisional visual estimate; must be validated during formal blind annotation."
    },
    {
        "candidate_id": "CS_VAL_020",
        "category": "Crack",
        "source": "Humans in the Loop (DrBimmer)",
        "dimensions": "637x419",
        "total_image_pixels": 266903,
        "reported_occupancy_pct": "59.3%",
        "calculation_method": "Axis-Aligned Bounding Box (AABB) Approximation [80, 50, 560, 380]",
        "source_of_evidence": "Pre-screening heuristic visual estimate by script author",
        "upstream_annotation_exists": "YES (Upstream DrBimmer COCO polygons exist in HF repo, not ingested)",
        "substantiation_status": "PROVISIONAL_ESTIMATE",
        "passes_30pct_threshold": "PASS (Defect spans center of bumper; AABB easily exceeds 30%)",
        "governance_flag": "FLAG-02: Bounding box AABB is 59.3%, but narrow crack polygon mask area is ~3.5%."
    },
    {
        "candidate_id": "CS_VAL_021",
        "category": "Crack",
        "source": "Humans in the Loop (DrBimmer)",
        "dimensions": "637x440",
        "total_image_pixels": 280280,
        "reported_occupancy_pct": "51.4%",
        "calculation_method": "Axis-Aligned Bounding Box (AABB) Approximation [120, 40, 520, 400]",
        "source_of_evidence": "Pre-screening heuristic visual estimate by script author",
        "upstream_annotation_exists": "YES (Upstream DrBimmer COCO polygons exist in HF repo, not ingested)",
        "substantiation_status": "PROVISIONAL_ESTIMATE",
        "passes_30pct_threshold": "PASS (Vertical split with displaced bumper flange)",
        "governance_flag": "FLAG-02: Bounding box AABB is 51.4%, but crack line polygon mask area is ~2.8%."
    },
    {
        "candidate_id": "CS_VAL_022",
        "category": "Lamp Broken",
        "source": "Humans in the Loop (DrBimmer)",
        "dimensions": "629x471",
        "total_image_pixels": 296259,
        "reported_occupancy_pct": "76.1%",
        "calculation_method": "Axis-Aligned Bounding Box (AABB) Approximation [40, 30, 590, 440]",
        "source_of_evidence": "Pre-screening heuristic visual estimate by script author",
        "upstream_annotation_exists": "YES (Upstream DrBimmer COCO polygons exist in HF repo, not ingested)",
        "substantiation_status": "PROVISIONAL_ESTIMATE",
        "passes_30pct_threshold": "PASS (High Confidence - shattered headlamp fills majority of frame)",
        "governance_flag": "FLAG-03: Lamp housing vs shattered lens distinction must be unified in annotation protocol."
    },
    {
        "candidate_id": "CS_VAL_023",
        "category": "Lamp Broken",
        "source": "Humans in the Loop (DrBimmer)",
        "dimensions": "881x476",
        "total_image_pixels": 419356,
        "reported_occupancy_pct": "54.1%",
        "calculation_method": "Axis-Aligned Bounding Box (AABB) Approximation [150, 60, 780, 420]",
        "source_of_evidence": "Pre-screening heuristic visual estimate by script author",
        "upstream_annotation_exists": "YES (Upstream DrBimmer COCO polygons exist in HF repo, not ingested)",
        "substantiation_status": "PROVISIONAL_ESTIMATE",
        "passes_30pct_threshold": "PASS (Cracked red taillight casing spans center right)",
        "governance_flag": "FLAG-01: Provisional visual estimate; must be validated during formal blind annotation."
    },
    {
        "candidate_id": "CS_VAL_024",
        "category": "Scratch",
        "source": "Humans in the Loop (DrBimmer)",
        "dimensions": "637x442",
        "total_image_pixels": 281554,
        "reported_occupancy_pct": "45.3%",
        "calculation_method": "Axis-Aligned Bounding Box (AABB) Approximation [30, 110, 610, 330]",
        "source_of_evidence": "Pre-screening heuristic visual estimate by script author",
        "upstream_annotation_exists": "YES (Upstream DrBimmer COCO polygons exist in HF repo, not ingested)",
        "substantiation_status": "PROVISIONAL_ESTIMATE",
        "passes_30pct_threshold": "PASS (Under AABB rule: 45.3%; FAILS under strict polygon mask rule: < 1.5%)",
        "governance_flag": "FLAG-04: CRITICAL - Scratch AABB box is 45.3%, but linear scratch pixel area is < 1.5%."
    },
    {
        "candidate_id": "CS_VAL_025",
        "category": "Dent",
        "source": "Humans in the Loop (DrBimmer)",
        "dimensions": "637x444",
        "total_image_pixels": 282828,
        "reported_occupancy_pct": "60.1%",
        "calculation_method": "Axis-Aligned Bounding Box (AABB) Approximation [70, 50, 570, 390]",
        "source_of_evidence": "Pre-screening heuristic visual estimate by script author",
        "upstream_annotation_exists": "YES (Upstream DrBimmer COCO polygons exist in HF repo, not ingested)",
        "substantiation_status": "PROVISIONAL_ESTIMATE",
        "passes_30pct_threshold": "PASS (Concave dent depression fills frame center)",
        "governance_flag": "FLAG-01: Provisional visual estimate; must be validated during formal blind annotation."
    }
]

def save_csv(path, rows):
    keys = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        wtr = csv.DictWriter(f, fieldnames=keys)
        wtr.writeheader()
        wtr.writerows(rows)
    print(f"Saved: {path}")

# Write to PLAN_DIR, BATCH_DIR, MANIFEST_DIR
for d in [PLAN_DIR, BATCH_DIR, MANIFEST_DIR]:
    save_csv(os.path.join(d, "corrected_tier_classification.csv"), tier_rows)
    save_csv(os.path.join(d, "macro_quota_scenarios.csv"), quota_rows)
    save_csv(os.path.join(d, "occupancy_evidence_audit.csv"), occupancy_rows)

print("All 3 audit CSVs created successfully.")
