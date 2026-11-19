# ClaimSense AI — Phase 9.4: Experiment Reproducibility & Governance Protocol

**Document ID:** `REP-PH9-4-REPRO-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.4 — Training Strategy & Hyperparameter Optimization Planning  
**Governing Standard:** B.Tech Major Project Engineering Governance & Cryptographic Integrity  
**Status:** REPRODUCIBILITY FRAMEWORK SEALED  

---

## 1. Executive Summary

This protocol establishes the mandatory experiment governance, configuration recording, and artifact retention standard for all future Phase 9 model training experiments.

---

## 2. Mandatory Experiment Record Schema

Every experiment executed in future phases must generate a formal `experiment_record.json` containing the following cryptographic and execution attributes:

```json
{
  "experiment_id": "P9-T01",
  "timestamp_utc": "2026-11-XX...",
  "git_commit_sha": "<exact 40-char git commit>",
  "git_branch": "main",
  "dataset_manifest_sha256": "<sha256 of dataset manifest>",
  "dataset_config_yaml_sha256": "<sha256 of data.yaml>",
  "initialization_checkpoint": {
    "source_path": "yolov8n.pt",
    "sha256": "<recalculated sha256>"
  },
  "training_hyperparameters": {
    "imgsz": 832,
    "batch_size": 8,
    "epochs": 30,
    "lr0": 0.001,
    "lrf": 0.01,
    "optimizer": "AdamW",
    "weight_decay": 0.0005,
    "loss_weights": { "box": 7.5, "cls": 1.5, "dfl": 1.5 },
    "class_weights": { "crack": 2.8, "others": 1.0 },
    "augmentations": { "mosaic": 1.0, "copy_paste": 0.30, "fliplr": 0.5 }
  },
  "random_seed": 42,
  "environment": {
    "python_version": "3.14.6",
    "pytorch_version": "2.15.0+cpu",
    "ultralytics_version": "8.3.163",
    "os_version": "Windows 11 x86_64",
    "device": "cpu"
  },
  "final_checkpoint": {
    "saved_path": "runs/phase9/experiments/P9-T01/weights/best.pt",
    "file_size_bytes": 6472810,
    "sha256": "<cryptographic sha256>"
  },
  "validation_metrics": {
    "mAP50": 0.0,
    "mAP50-95": 0.0,
    "precision": 0.0,
    "recall": 0.0,
    "crack_recall": 0.0
  }
}
```

---

## 3. Checkpoint Naming & Artifact Retention Policy

1. **Isolation of Candidate Weights:**
   - All future candidate models must be written to isolated directories:
     `runs/phase9/experiments/<EXPERIMENT_ID>/weights/best.pt`
     `runs/phase9/experiments/<EXPERIMENT_ID>/weights/last.pt`
2. **Strict Prohibition on Production Overwrite:**
   - Under NO circumstance may any script write to, overwrite, or rename `models/phase5/best.pt`.
   - The production baseline must remain immutable.
3. **Preservation of Historical Benchmarks:**
   - Historical checkpoints (`EXP01`, `EXP02`, `EXP03`, `Session 1-4`) must remain quarantined and unaltered.
4. **Artifact Retention Minimums:**
   - Every completed run must retain: `args.yaml`, `results.csv`, `best.pt`, `confusion_matrix.png`, and `experiment_record.json`.
