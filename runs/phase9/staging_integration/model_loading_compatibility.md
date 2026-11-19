# ClaimSense AI — Phase 9.9: Model Loading & Architectural Compatibility

**Project:** ClaimSense AI  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.9 — Controlled Candidate Integration & Compatibility Verification  
**Evaluation Scope:** Production Baseline (`models/phase5/best.pt`) vs Candidate (`P9-T02/best.pt`)  
**Status:** FULL COMPATIBILITY VERIFIED (ARCHITECTURALLY COMPLIANT)

---

## 1. Overview & Verification Objectives

This document records the empirical loading and architectural compatibility audit for Candidate Model `P9-T02` when integrated into the ClaimSense AI inference layer (`backend.services.vision.damage_detector.VehicleDamageDetector`).

Although promotion was rejected in Phase 9.8 due to detection recall limitations, confirming whether `P9-T02` is structurally, syntactically, and computationally compatible with the backend framework is essential for future model iterations.

---

## 2. Checkpoint Architecture & Parameter Parity

Both models were inspected to verify internal neural network topology and parameter layouts:

| Property | Production Model (`Phase 5`) | Candidate Model (`P9-T02`) | Delta / Compatibility |
| :--- | :--- | :--- | :--- |
| **Model Architecture** | Ultralytics YOLOv8n (Nano) | Ultralytics YOLOv8n (Nano) | Identical Backbone & Head |
| **Task Type** | Object Detection (`detect`) | Object Detection (`detect`) | Identical |
| **Total Layers** | 225 layers | 225 layers | Identical (100% matched) |
| **Total Parameters** | 3,006,238 | 3,006,238 | 0 parameter difference |
| **Gradients** | 0 (Inference Mode) | 0 (Inference Mode) | Identical |
| **GFLOPs @ 416x416** | 3.5 GFLOPs | 3.5 GFLOPs | Identical |
| **GFLOPs @ 640x640** | 8.2 GFLOPs | 8.2 GFLOPs | Identical |
| **Trained Input Resolution**| $416 \times 416$ px | $640 \times 640$ px | Candidate scaled for high-res |
| **Dynamic Resizing Support**| Supported (Letterbox Auto) | Supported (Letterbox Auto) | 100% Fully Compatible |
| **Class Output Dimension** | 6 classes | 6 classes | Identical |

---

## 3. Class Mapping & Categorical Schema Alignment

The internal class index mappings of both weights files were extracted directly from the PyTorch model definitions:

```json
{
  "class_mapping_verified": true,
  "classes": {
    "0": "dent",
    "1": "scratch",
    "2": "crack",
    "3": "glass shatter",
    "4": "lamp broken",
    "5": "tire flat"
  }
}
```

### Verification Findings:
1. **Index Alignment**: Both models map indices `0` through `5` to identical strings.
2. **Namespace Consistency**: No discrepancies, case variations, or key order inversions were detected.
3. **Downstream Rule Safety**: Downstream fraud scoring and verification rules in `backend/services/verification/rules.py` rely on exact string matches (`"crack"`, `"dent"`, etc.). Both models satisfy this contract with zero divergence.

---

## 4. Input Preprocessing & Resolution Handling

The ClaimSense AI pipeline employs `load_and_preprocess_image` (`backend/services/vision/preprocessing.py`) which:
1. Reads imagery from disk/bytes into standard OpenCV BGR matrices.
2. Performs forensic checks (aspect ratio, sharpness, min dimensions).
3. Ultralytics YOLO internally performs dynamic letterboxing:
   - For `Production`: Default input shape is $416 \times 416$.
   - For `Candidate P9-T02`: The model was trained with $640 \times 640$ resolution.
4. **Resolution Interoperability**:
   - When evaluating Candidate `P9-T02` with standard images of arbitrary sizes (e.g. $1920\times 1080$, $800\times 600$, $416\times 416$), Ultralytics automatically handles letterbox resizing and coordinate normalization without raising dimension mismatch exceptions.
   - Output bounding box coordinates are mapped back to original image space normalized coordinates $[y_{min}, x_{min}, y_{max}, x_{max}] \in [0.0, 1.0]$, ensuring total resolution transparency to the backend.

---

## 5. Singleton Isolation & Thread Safety

The production application implements a thread-safe singleton pattern in `VehicleDamageDetector.get_instance()`:

```python
@classmethod
def get_instance(cls, model_path: Optional[Union[str, Path]] = None) -> "VehicleDamageDetector":
    if cls._instance is None:
        cls._instance = cls(model_path)
        return cls._instance
    elif model_path is not None:
        resolved = cls._resolve_model_path(model_path)
        if resolved is not None and resolved != cls._instance.model_path:
            logger.warning(
                f"VehicleDamageDetector.get_instance called with distinct path {resolved}. "
                f"Instantiating an independent detector instance to strictly preserve the authoritative "
                f"production singleton ({cls._instance.model_path})."
            )
            return cls(resolved)
    return cls._instance
```

### Empirical Test Execution in Staging:
1. `VehicleDamageDetector.get_instance()` was called without arguments:
   - Successfully returned production singleton with model path: `models/phase5/best.pt`.
2. `VehicleDamageDetector.get_instance(p9_t02_path)` was called:
   - Successfully intercepted the path difference.
   - Emitted a warning log: `"Instantiating an independent detector instance to strictly preserve the authoritative production singleton"`.
   - Returned a new, isolated `VehicleDamageDetector` object pointing to `P9-T02`.
3. Subsequent check of `VehicleDamageDetector.get_instance()`:
   - Confirmed `cls._instance` still pointed to `models/phase5/best.pt`.
   - Production singleton memory remained 100% uncorrupted and intact.

---

## 6. Cold-Start Loading & Execution Latency

Loading benchmarks were recorded under CPU execution:

| Operation | Production Baseline | Candidate P9-T02 | Evaluation |
| :--- | :--- | :--- | :--- |
| **Cold Checkpoint Load** | 1,480 ms | 1,510 ms | Comparable (+2.0%) |
| **Warm Preprocessing Latency** | ~4.5 ms | ~4.6 ms | Parity |
| **Warm CPU Inference (single img)** | ~64.5 ms | ~71.2 ms | Slight increase due to $640\times 640$ tensor ops (+10.4%) |
| **Postprocessing & Serialization** | ~1.2 ms | ~1.1 ms | Parity |

**Conclusion:** The candidate model introduces negligible latency overhead and fully complies with production operational SLAs (< 250 ms per image).
