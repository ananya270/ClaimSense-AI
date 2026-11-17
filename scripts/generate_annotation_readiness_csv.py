import os
import csv

WORKSPACE = r"C:\Users\ansh9\Desktop\Claimsense Ai"
PLAN_DIR = os.path.join(WORKSPACE, "runs", "phase8", "independent_validation_plan")
BATCH_DIR = os.path.join(PLAN_DIR, "batch_01")
MANIFEST_DIR = os.path.join(WORKSPACE, "datasets", "CarDD_Independent_Val_v1", "manifests")

# 8 Quarantined Macro Candidates
QUARANTINED_CANDIDATES = [
    {
        "candidate_id": "CS_VAL_016",
        "file_title": "File:Damaged car from hail in Missouri, April 2001.jpg",
        "source": "Wikimedia Commons (FEMA/NWS)",
        "category": "Dent",
        "dimensions": "640x480",
        "provisional_aabb_occupancy": "72.0%",
        "certification_prerequisite": "Requires dual-blind annotation of multi-dent hail cluster",
        "evidence_status": "PROVISIONAL_AABB (High Confidence)",
        "annotation_challenge": "Hail cluster boundary: bounding individual dimples vs entire dimpled hood assembly",
        "adjudication_risk": "Low (Dent cluster easily exceeds 30% of frame)",
        "current_status": "QUARANTINED (Pending Annotation)",
        "certification_readiness": "READY_FOR_ANNOTATION"
    },
    {
        "candidate_id": "CS_VAL_017",
        "file_title": "File:Hail damage car.jpg",
        "source": "Wikimedia Commons (Simiprof)",
        "category": "Dent",
        "dimensions": "720x960",
        "provisional_aabb_occupancy": "65.0%",
        "certification_prerequisite": "Requires dual-blind annotation and orientation-agnostic Tier 2 ratification",
        "evidence_status": "PROVISIONAL_AABB (High Confidence)",
        "annotation_challenge": "Vertical portrait orientation; annotators must bound sheet metal hail dents across frame",
        "adjudication_risk": "Low (Hail damage spans majority of frame)",
        "current_status": "QUARANTINED (Pending Annotation)",
        "certification_readiness": "READY_FOR_ANNOTATION"
    },
    {
        "candidate_id": "CS_VAL_020",
        "file_title": "Car damages 100.png",
        "source": "Humans in the Loop",
        "category": "Crack",
        "dimensions": "637x419",
        "provisional_aabb_occupancy": "59.3%",
        "certification_prerequisite": "Requires dual-blind annotation of plastic bumper fracture",
        "evidence_status": "PROVISIONAL_AABB (Moderate Confidence)",
        "annotation_challenge": "Delineating crack propagation tip-to-tip vs displaced plastic edge",
        "adjudication_risk": "Medium (Annotators must agree on crack start/end endpoints)",
        "current_status": "QUARANTINED (Pending Annotation)",
        "certification_readiness": "READY_FOR_ANNOTATION"
    },
    {
        "candidate_id": "CS_VAL_021",
        "file_title": "Car damages 101.png",
        "source": "Humans in the Loop",
        "category": "Crack",
        "dimensions": "637x440",
        "provisional_aabb_occupancy": "51.4%",
        "certification_prerequisite": "Requires dual-blind annotation of bumper split and flange displacement",
        "evidence_status": "PROVISIONAL_AABB (Moderate Confidence)",
        "annotation_challenge": "Distinguishing true crack line from bumper-to-chassis mounting seam",
        "adjudication_risk": "Medium (Seam vs crack confusion risk)",
        "current_status": "QUARANTINED (Pending Annotation)",
        "certification_readiness": "READY_FOR_ANNOTATION"
    },
    {
        "candidate_id": "CS_VAL_022",
        "file_title": "Car damages 102.jpg",
        "source": "Humans in the Loop",
        "category": "Lamp Broken",
        "dimensions": "629x471",
        "provisional_aabb_occupancy": "76.1%",
        "certification_prerequisite": "Requires dual-blind annotation of shattered headlamp assembly",
        "evidence_status": "UNRESOLVED_BOUNDARY_EVIDENCE",
        "annotation_challenge": "Scope of label: bounding broken glass lens only vs entire crushed lamp assembly",
        "adjudication_risk": "Medium-High (Both exceed 30%, but class label 'glass' vs 'lamp' could cause reviewer conflict)",
        "current_status": "QUARANTINED (Pending Boundary Clarification)",
        "certification_readiness": "CONDITIONAL (Requires Adjudication Rule)"
    },
    {
        "candidate_id": "CS_VAL_023",
        "file_title": "Car damages 103.png",
        "source": "Humans in the Loop",
        "category": "Lamp Broken",
        "dimensions": "881x476",
        "provisional_aabb_occupancy": "54.1%",
        "certification_prerequisite": "Requires dual-blind annotation of cracked red taillight lens",
        "evidence_status": "PROVISIONAL_AABB (High Confidence)",
        "annotation_challenge": "Taillight housing clearly defined; annotators must enclose fractured outer lens",
        "adjudication_risk": "Low (Clear component boundary)",
        "current_status": "QUARANTINED (Pending Annotation)",
        "certification_readiness": "READY_FOR_ANNOTATION"
    },
    {
        "candidate_id": "CS_VAL_024",
        "file_title": "Car damages 104.png",
        "source": "Humans in the Loop",
        "category": "Scratch",
        "dimensions": "637x442",
        "provisional_aabb_occupancy": "45.3%",
        "certification_prerequisite": "Requires dual-blind annotation under strict AABB definition of scratch footprint",
        "evidence_status": "UNRESOLVED_AREA_EVIDENCE",
        "annotation_challenge": "Long diagonal scratch: AABB box occupies 45.3%, but linear scratch pixels occupy < 1.5%",
        "adjudication_risk": "HIGH (If annotator breaks into small sub-boxes, each sub-box is < 30%)",
        "current_status": "QUARANTINED (Pending Guideline Ratification)",
        "certification_readiness": "CONDITIONAL (Requires AABB Rule Clarification)"
    },
    {
        "candidate_id": "CS_VAL_025",
        "file_title": "Car damages 105.png",
        "source": "Humans in the Loop",
        "category": "Dent",
        "dimensions": "637x444",
        "provisional_aabb_occupancy": "60.1%",
        "certification_prerequisite": "Requires dual-blind annotation of concave fender impact deformation",
        "evidence_status": "PROVISIONAL_AABB (High Confidence)",
        "annotation_challenge": "Delineating outer inflection rim of soft dent across curved fender wheel arch",
        "adjudication_risk": "Low-Medium (Inflection point boundary variation between annotators)",
        "current_status": "QUARANTINED (Pending Annotation)",
        "certification_readiness": "READY_FOR_ANNOTATION"
    }
]

def save_csv(path, rows):
    keys = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        wtr = csv.DictWriter(f, fieldnames=keys)
        wtr.writeheader()
        wtr.writerows(rows)
    print(f"Saved: {path}")

for d in [PLAN_DIR, BATCH_DIR, MANIFEST_DIR]:
    save_csv(os.path.join(d, "annotation_readiness_matrix.csv"), QUARANTINED_CANDIDATES)

print("annotation_readiness_matrix.csv generated successfully.")
