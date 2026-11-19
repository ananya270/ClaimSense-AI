# ClaimSense AI — Phase 9.9: API Contract & Schema Parity Comparison

**Project:** ClaimSense AI  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.9 — Controlled Candidate Integration & Compatibility Verification  
**Status:** 100% SCHEMA PARITY CONFIRMED (ZERO BREAKING CHANGES)

---

## 1. Executive Summary

This document presents a side-by-side comparison of the API contract, serialization format, and data structures produced by the authoritative Production Baseline (`models/phase5/best.pt`) versus Candidate Model `P9-T02` (`runs/phase9/retraining/P9-T02/checkpoints/best.pt`).

Both models were evaluated through `VehicleDamageDetector.detect_damage()` and the downstream service wrapper `process_claim_damage_detection()`. The evaluation confirms that Candidate `P9-T02` adheres with 100% fidelity to the existing ClaimSense AI Vision API contract.

---

## 2. Top-Level Response Schema Comparison

The table below contrasts each dictionary key returned by `detect_damage()` for both checkpoints:

| Response Field | Type | Production Baseline | Candidate P9-T02 | Parity Status |
| :--- | :--- | :--- | :--- | :--- |
| `conf_threshold` | `float` | `0.15` / `0.25` | `0.15` / `0.25` | **IDENTICAL** |
| `damage_categories`| `List[str]` | Unique sorted categories | Unique sorted categories | **IDENTICAL** |
| `detection_method` | `str` | `"yolov8_custom_cardd"` | `"yolov8_custom_cardd"` | **IDENTICAL** |
| `detections` | `List[Dict]` | Array of bounding boxes | Array of bounding boxes | **IDENTICAL** |
| `device` | `str` | `"cpu"` | `"cpu"` | **IDENTICAL** |
| `has_damage` | `bool` | `True` / `False` | `True` / `False` | **IDENTICAL** |
| `highest_confidence`| `float` | Max detection score | Max detection score | **IDENTICAL** |
| `image_dimensions` | `Dict[str, int]` | `{"width", "height", "channels"}` | `{"width", "height", "channels"}` | **IDENTICAL** |
| `model_available` | `bool` | `True` | `True` | **IDENTICAL** |
| `model_name` | `str` | `"ClaimSense-YOLOv8-DamageDetector"`| `"ClaimSense-YOLOv8-DamageDetector"`| **IDENTICAL** |
| `model_version` | `str` | `"cardd-yolov8n-v1.0"` | `"cardd-yolov8n-v1.0"` | **IDENTICAL** |
| `processing_time_ms`| `float` | Milliseconds elapsed | Milliseconds elapsed | **IDENTICAL** |
| `quality_assessment`| `Dict[str, Any]`| Quality metadata | Quality metadata | **IDENTICAL** |
| `total_detections` | `int` | Count of detected boxes | Count of detected boxes | **IDENTICAL** |

---

## 3. Individual Detection Object Schema Parity

Each object within the `detections` array is guaranteed to contain the following keys and data formats:

| Field Name | Type | Value Format / Constraints | Production Baseline | Candidate P9-T02 |
| :--- | :--- | :--- | :--- | :--- |
| `class_id` | `int` | Integer $\in [0, 5]$ | Supported | Supported |
| `label` | `str` | Class name string (e.g. `"dent"`, `"crack"`) | Supported | Supported |
| `category` | `str` | Normalized categorical string | Supported | Supported |
| `confidence` | `float` | Confidence score $\in [0.0, 1.0]$ | Supported | Supported |
| `bbox_normalized` | `List[float]` | $[y_{min}, x_{min}, y_{max}, x_{max}] \in [0.0, 1.0]$ | Supported | Supported |
| `bbox_pixels` | `List[int]` | $[y_{min}, x_{min}, y_{max}, x_{max}]$ integer pixels | Supported | Supported |
| `spatial_region` | `str` | Spatial quadrant (e.g. `"center"`, `"top-left"`) | Supported | Supported |
| `estimated_severity`| `str` | Severity tier (`"minor"`, `"moderate"`, `"severe"`)| Supported | Supported |

### JSON Schema Verification Example:

```json
{
  "class_id": 0,
  "label": "dent",
  "category": "dent",
  "confidence": 0.7423,
  "bbox_normalized": [0.412, 0.355, 0.684, 0.712],
  "bbox_pixels": [445, 681, 739, 1367],
  "spatial_region": "center",
  "estimated_severity": "moderate"
}
```

Both models produce JSON serializable outputs that validate completely against the strict ClaimSense AI database schema constraints.

---

## 4. Downstream Subsystem Impact Analysis

Because the candidate checkpoint matches the exact schema and interface contracts of the existing model, downstream components interact with it seamlessly:

1. **Database Persistence (`VehicleDamageAnalysis` & `VehicleDamageDetection`)**:
   - ORM models in `backend/database/models.py` insert detections via list iteration.
   - All columns (`category`, `confidence`, `bbox_normalized`, `severity`, etc.) map without null constraints or type errors.
2. **Cross-Modal Verification Engine (`backend/services/verification/engine.py`)**:
   - The field comparator and scoring engine match reported damage against incident descriptions using string labels (`"crack"`, `"scratch"`, `"dent"`).
   - Candidate `P9-T02` preserves all exact category strings, preventing misclassification in fraud detection logic.
3. **Visualization & Annotation Pipeline (`backend/services/vision/visualization.py`)**:
   - Bounding boxes are drawn onto OpenCV canvases using `bbox_pixels` and `label`.
   - Annotation rendering completed without distortion or out-of-bounds clipping.
4. **REST API Endpoints (`backend/routes/claims.py`)**:
   - API endpoints `/api/claims/<id>/damage-detection` and `/api/claims/submit` serialize detection payloads into JSON.
   - Full compatibility was confirmed.

---

## 5. Architectural Contract Verdict

Candidate `P9-T02` achieves **100% API contract compliance**. If model weights are ever approved for promotion in future phases, zero modifications to the application codebase, database schemas, or client-side contracts will be required.
