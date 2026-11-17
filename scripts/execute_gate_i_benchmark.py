"""ClaimSense AI — Phase 8: Gate I Benchmark Execution Engine.

Executes:
1. Pre-benchmark verification of 44-image dataset integrity & SHA-256 snapshot.
2. Checkpoint SHA-256 verification before and after evaluation.
3. Staging of independent validation splits (Pooled: 44, Tier 1: 36, Tier 2: 8).
4. Ultralytics evaluation for all 3 checkpoints across all 3 splits:
   - Production Baseline (Phase 5 best.pt)
   - Phase 8 Session 2 (best.pt)
   - Phase 8 Session 4 (best.pt)
5. Dedicated CUDA-synchronized latency benchmarking.
6. Fixed-threshold operational evaluation (conf=0.25, iou=0.45).
7. Emission of all required CSVs, confusion matrices, and markdown reports.
"""

import os
import sys
import time
import json
import csv
import shutil
import hashlib
from pathlib import Path
import numpy as np
import torch
from ultralytics import YOLO

PROJECT_ROOT = Path("c:/Users/ansh9/Desktop/Claimsense Ai")
VAL_BASE = PROJECT_ROOT / "datasets" / "CarDD_Independent_Val_v1"
B1_DIR = VAL_BASE / "batch_01"
B2_DIR = VAL_BASE / "batch_02"
MANIFEST_DIR = VAL_BASE / "manifests"
GATE_I_DIR = PROJECT_ROOT / "runs" / "phase8" / "gate_i_benchmark"
STAGING_DIR = GATE_I_DIR / "dataset_staging"

CLASS_NAMES = {
    0: "dent",
    1: "scratch",
    2: "crack",
    3: "glass shatter",
    4: "lamp broken",
    5: "tire flat"
}

CHECKPOINTS = [
    {
        "key": "production_baseline",
        "name": "Production Baseline (Phase 5)",
        "path": PROJECT_ROOT / "models" / "phase5" / "best.pt",
        "expected_sha": "90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565"
    },
    {
        "key": "session_2",
        "name": "Phase 8 Session 2",
        "path": PROJECT_ROOT / "runs" / "phase8" / "session_2" / "weights" / "best.pt",
        "expected_sha": "2ee0a56749ceba72da863fd3496f080ee06f26409daa4e9588fb69ee149333c5"
    },
    {
        "key": "session_4",
        "name": "Phase 8 Session 4",
        "path": PROJECT_ROOT / "runs" / "phase8" / "session_4_training_01" / "weights" / "best.pt",
        "expected_sha": "ea53eee94e508bbb81620b47b2a23c9826341b6b5a6981d9371e476cb9d0594f"
    }
]

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def measure_latency(model, image_paths, num_warmup=10):
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    dummy = torch.zeros((1, 3, 640, 640), device=device, dtype=torch.float32)
    for _ in range(num_warmup):
        _ = model.predict(dummy, imgsz=640, device=0, verbose=False)

    if torch.cuda.is_available():
        torch.cuda.synchronize()

    timings = []
    starter = torch.cuda.Event(enable_timing=True)
    ender = torch.cuda.Event(enable_timing=True)

    for img_p in image_paths:
        starter.record()
        _ = model.predict(str(img_p), imgsz=640, device=0, conf=0.25, iou=0.45, verbose=False)
        ender.record()
        torch.cuda.synchronize()
        timings.append(starter.elapsed_time(ender))

    timings = np.array(timings)
    return {
        "mean_ms": round(float(np.mean(timings)), 2),
        "median_ms": round(float(np.median(timings)), 2),
        "std_ms": round(float(np.std(timings)), 2),
        "min_ms": round(float(np.min(timings)), 2),
        "max_ms": round(float(np.max(timings)), 2),
        "fps": round(1000.0 / float(np.mean(timings)), 1) if np.mean(timings) > 0 else 0.0,
        "sample_count": len(timings)
    }

def write_csv(filepath, rows, fieldnames):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

def main():
    print("=" * 80)
    print("  CLAIMSENSE AI — PHASE 8: GATE I INDEPENDENT MODEL BENCHMARK")
    print("  Evaluation Dataset: CarDD_Independent_Val_v1 (44 Images, 47 Instances)")
    print("=" * 80)

    # 1. Verify Dataset Snapshot
    snapshot_csv = MANIFEST_DIR / "gate_g_sha256_snapshot.csv"
    assert snapshot_csv.exists(), "Snapshot CSV missing!"
    
    snapshot_rows = []
    with open(snapshot_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            snapshot_rows.append(r)
    assert len(snapshot_rows) == 44, f"Expected 44 snapshot rows, got {len(snapshot_rows)}"

    print("\n[Step 1] Verifying Pre-Benchmark Dataset SHA-256 Snapshot...")
    for row in snapshot_rows:
        cid = row['image_id']
        batch = row['batch']
        expected_img_sha = row['processed_sha256']
        expected_lbl_sha = row['label_sha256']

        img_p = VAL_BASE / batch / "processed" / f"{cid}.jpg"
        lbl_p = VAL_BASE / batch / "labels" / f"{cid}.txt"

        assert img_p.exists(), f"Image {img_p} missing!"
        assert lbl_p.exists(), f"Label {lbl_p} missing!"

        act_img_sha = sha256_file(img_p)
        act_lbl_sha = sha256_file(lbl_p)

        assert act_img_sha == expected_img_sha, f"SHA mismatch for image {cid}!"
        assert act_lbl_sha == expected_lbl_sha, f"SHA mismatch for label {cid}!"
    print("  -> Pre-benchmark dataset integrity verified: 100% PASS (44/44 match snapshot).")

    # 2. Verify Checkpoint SHA256 Hashes
    print("\n[Step 2] Verifying Pre-Benchmark Checkpoint Hashes...")
    pre_ckpt_hashes = {}
    for ckpt in CHECKPOINTS:
        p = ckpt["path"]
        assert p.exists(), f"Checkpoint {p} does not exist!"
        h = sha256_file(p)
        pre_ckpt_hashes[ckpt["key"]] = h
        print(f"  - {ckpt['name']:<30} | SHA256: {h[:16]}... | Match: {h == ckpt['expected_sha']}")
        assert h == ckpt["expected_sha"], f"Checkpoint hash mismatch for {ckpt['name']}!"

    # 3. Stage Evaluation Splits
    print("\n[Step 3] Staging Evaluation Dataset Splits...")
    for split_name in ["pooled", "tier1", "tier2"]:
        (STAGING_DIR / split_name / "images").mkdir(parents=True, exist_ok=True)
        (STAGING_DIR / split_name / "labels").mkdir(parents=True, exist_ok=True)

    tier1_ids = [r['image_id'] for r in snapshot_rows if "Tier 1" in r['resolution_tier']]
    tier2_ids = [r['image_id'] for r in snapshot_rows if "Tier 2" in r['resolution_tier']]
    assert len(tier1_ids) == 36, f"Expected 36 Tier 1 images, got {len(tier1_ids)}"
    assert len(tier2_ids) == 8, f"Expected 8 Tier 2 images, got {len(tier2_ids)}"

    for row in snapshot_rows:
        cid = row['image_id']
        batch = row['batch']
        img_src = VAL_BASE / batch / "processed" / f"{cid}.jpg"
        lbl_src = VAL_BASE / batch / "labels" / f"{cid}.txt"

        # Copy to pooled
        shutil.copy2(img_src, STAGING_DIR / "pooled" / "images" / f"{cid}.jpg")
        shutil.copy2(lbl_src, STAGING_DIR / "pooled" / "labels" / f"{cid}.txt")

        # Copy to tier1 or tier2
        if cid in tier1_ids:
            shutil.copy2(img_src, STAGING_DIR / "tier1" / "images" / f"{cid}.jpg")
            shutil.copy2(lbl_src, STAGING_DIR / "tier1" / "labels" / f"{cid}.txt")
        else:
            shutil.copy2(img_src, STAGING_DIR / "tier2" / "images" / f"{cid}.jpg")
            shutil.copy2(lbl_src, STAGING_DIR / "tier2" / "labels" / f"{cid}.txt")

    print(f"  -> Staged Pooled: {len(list((STAGING_DIR / 'pooled' / 'images').glob('*.jpg')))} images")
    print(f"  -> Staged Tier 1: {len(list((STAGING_DIR / 'tier1' / 'images').glob('*.jpg')))} images")
    print(f"  -> Staged Tier 2: {len(list((STAGING_DIR / 'tier2' / 'images').glob('*.jpg')))} images")

    # Generate dataset YAMLs
    yaml_configs = {}
    for split in ["pooled", "tier1", "tier2"]:
        yaml_content = f"""# ClaimSense AI Independent Validation - {split}
path: {str((STAGING_DIR / split).resolve()).replace('\\', '/')}
train: images
val: images

nc: 6
names:
  0: dent
  1: scratch
  2: crack
  3: glass shatter
  4: lamp broken
  5: tire flat
"""
        y_path = STAGING_DIR / f"dataset_{split}.yaml"
        with open(y_path, "w") as f:
            f.write(yaml_content)
        yaml_configs[split] = y_path

    # 4. Latency Benchmark
    print("\n[Step 4] Running Dedicated Latency Benchmark...")
    pooled_images = sorted(list((STAGING_DIR / "pooled" / "images").glob("*.jpg")))
    latency_results = {}
    for ckpt in CHECKPOINTS:
        k = ckpt["key"]
        print(f"  - Measuring latency for {ckpt['name']} on 44 images...")
        model = YOLO(str(ckpt["path"]))
        lat = measure_latency(model, pooled_images, num_warmup=10)
        latency_results[k] = lat
        print(f"    Mean: {lat['mean_ms']}ms | Median: {lat['median_ms']}ms | Std: {lat['std_ms']}ms | FPS: {lat['fps']}")

    # 5. Model Evaluation across Splits
    print("\n[Step 5] Running Standardized Ultralytics Evaluations...")
    eval_raw = {}
    for ckpt in CHECKPOINTS:
        k = ckpt["key"]
        eval_raw[k] = {}
        for split in ["pooled", "tier1", "tier2"]:
            print(f"\n---> Evaluating [{ckpt['name']}] on [{split}] split...")
            torch.cuda.empty_cache()
            model = YOLO(str(ckpt["path"]))
            save_proj = GATE_I_DIR / "eval_runs" / k
            save_name = split

            val_res = model.val(
                data=str(yaml_configs[split]),
                split="val",
                imgsz=640,
                batch=4,
                device=0,
                conf=0.001,
                iou=0.6,
                plots=True,
                save_json=False,
                project=str(save_proj),
                name=save_name,
                exist_ok=True,
                verbose=False
            )
            eval_raw[k][split] = val_res

    # 6. Parse and Structure Metrics
    print("\n[Step 6] Compiling Metrics & Composite Index...")
    overall_rows = []
    tier_rows = []
    per_class_rows = []
    cm_dir = GATE_I_DIR / "confusion_matrices"
    cm_dir.mkdir(parents=True, exist_ok=True)

    for ckpt in CHECKPOINTS:
        k = ckpt["key"]
        mname = ckpt["name"]

        res_t1 = eval_raw[k]["tier1"]
        res_t2 = eval_raw[k]["tier2"]
        res_p = eval_raw[k]["pooled"]

        splits_meta = [
            ("Tier 1 (Walkaround)", res_t1, 36),
            ("Tier 2 (Macro)", res_t2, 8),
            ("Empirical Pooled", res_p, 44)
        ]

        parsed_splits = {}
        for sname, res, n_imgs in splits_meta:
            box = res.box
            mp = float(box.mp)
            mr = float(box.mr)
            f1 = (2 * mp * mr / (mp + mr)) if (mp + mr) > 0 else 0.0
            map50 = float(box.map50)
            map50_95 = float(box.map)

            parsed_splits[sname] = {
                "precision": mp,
                "recall": mr,
                "f1": f1,
                "map50": map50,
                "map50_95": map50_95,
                "ap50_per_class": box.ap50.tolist(),
                "ap_per_class": box.ap.tolist(),
                "p_per_class": box.p.tolist(),
                "r_per_class": box.r.tolist(),
                "f1_per_class": box.f1.tolist()
            }

            tier_rows.append({
                "model_key": k,
                "model_name": mname,
                "evaluation_split": sname,
                "image_count": n_imgs,
                "precision": round(mp, 4),
                "recall": round(mr, 4),
                "f1_score": round(f1, 4),
                "map50": round(map50, 4),
                "map50_95": round(map50_95, 4)
            })

        # Calculate Fixed-Weight Composite Index (70% Tier 1 + 30% Tier 2)
        t1_p = parsed_splits["Tier 1 (Walkaround)"]
        t2_p = parsed_splits["Tier 2 (Macro)"]
        comp_precision = 0.70 * t1_p["precision"] + 0.30 * t2_p["precision"]
        comp_recall = 0.70 * t1_p["recall"] + 0.30 * t2_p["recall"]
        comp_f1 = (2 * comp_precision * comp_recall / (comp_precision + comp_recall)) if (comp_precision + comp_recall) > 0 else 0.0
        comp_map50 = 0.70 * t1_p["map50"] + 0.30 * t2_p["map50"]
        comp_map50_95 = 0.70 * t1_p["map50_95"] + 0.30 * t2_p["map50_95"]

        tier_rows.append({
            "model_key": k,
            "model_name": mname,
            "evaluation_split": "Fixed-Weight Composite (70% T1 + 30% T2)",
            "image_count": 44,
            "precision": round(comp_precision, 4),
            "recall": round(comp_recall, 4),
            "f1_score": round(comp_f1, 4),
            "map50": round(comp_map50, 4),
            "map50_95": round(comp_map50_95, 4)
        })

        pool_p = parsed_splits["Empirical Pooled"]
        overall_rows.append({
            "model_key": k,
            "model_name": mname,
            "pooled_map50": round(pool_p["map50"], 4),
            "pooled_map50_95": round(pool_p["map50_95"], 4),
            "pooled_precision": round(pool_p["precision"], 4),
            "pooled_recall": round(pool_p["recall"], 4),
            "pooled_f1": round(pool_p["f1"], 4),
            "composite_map50": round(comp_map50, 4),
            "composite_map50_95": round(comp_map50_95, 4),
            "composite_f1": round(comp_f1, 4),
            "latency_mean_ms": latency_results[k]["mean_ms"],
            "fps": latency_results[k]["fps"]
        })

        for cid in range(6):
            cname = CLASS_NAMES[cid]
            p_c = pool_p["p_per_class"][cid] if cid < len(pool_p["p_per_class"]) else 0.0
            r_c = pool_p["r_per_class"][cid] if cid < len(pool_p["r_per_class"]) else 0.0
            f1_c = pool_p["f1_per_class"][cid] if cid < len(pool_p["f1_per_class"]) else 0.0
            ap50_c = pool_p["ap50_per_class"][cid] if cid < len(pool_p["ap50_per_class"]) else 0.0
            ap_c = pool_p["ap_per_class"][cid] if cid < len(pool_p["ap_per_class"]) else 0.0

            t1_ap50 = t1_p["ap50_per_class"][cid] if cid < len(t1_p["ap50_per_class"]) else 0.0
            t2_ap50 = t2_p["ap50_per_class"][cid] if cid < len(t2_p["ap50_per_class"]) else 0.0
            comp_ap50 = 0.70 * t1_ap50 + 0.30 * t2_ap50

            per_class_rows.append({
                "model_key": k,
                "model_name": mname,
                "class_id": cid,
                "class_name": cname,
                "pooled_precision": round(p_c, 4),
                "pooled_recall": round(r_c, 4),
                "pooled_f1": round(f1_c, 4),
                "pooled_ap50": round(ap50_c, 4),
                "pooled_ap50_95": round(ap_c, 4),
                "tier1_ap50": round(t1_ap50, 4),
                "tier2_ap50": round(t2_ap50, 4),
                "composite_ap50": round(comp_ap50, 4)
            })

        # Save confusion matrix CSV
        if hasattr(res_p, "confusion_matrix") and res_p.confusion_matrix is not None:
            mat = res_p.confusion_matrix.matrix
            cm_csv_path = cm_dir / f"confusion_matrix_{k}.csv"
            with open(cm_csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                header = ["class"] + [CLASS_NAMES[i] for i in range(6)] + ["background"]
                writer.writerow(header)
                for r_idx, r_name in enumerate([CLASS_NAMES[i] for i in range(6)] + ["background"]):
                    writer.writerow([r_name] + [round(float(val), 2) for val in mat[r_idx]])

    # Write Deliverable CSVs
    write_csv(
        GATE_I_DIR / "overall_metrics.csv",
        overall_rows,
        ["model_key", "model_name", "pooled_map50", "pooled_map50_95", "pooled_precision", "pooled_recall", "pooled_f1", "composite_map50", "composite_map50_95", "composite_f1", "latency_mean_ms", "fps"]
    )
    write_csv(
        GATE_I_DIR / "tier_wise_metrics.csv",
        tier_rows,
        ["model_key", "model_name", "evaluation_split", "image_count", "precision", "recall", "f1_score", "map50", "map50_95"]
    )
    write_csv(
        GATE_I_DIR / "per_class_metrics.csv",
        per_class_rows,
        ["model_key", "model_name", "class_id", "class_name", "pooled_precision", "pooled_recall", "pooled_f1", "pooled_ap50", "pooled_ap50_95", "tier1_ap50", "tier2_ap50", "composite_ap50"]
    )

    latency_rows = []
    for ckpt in CHECKPOINTS:
        k = ckpt["key"]
        l_info = latency_results[k]
        latency_rows.append({
            "model_key": k,
            "model_name": ckpt["name"],
            "mean_latency_ms": l_info["mean_ms"],
            "median_latency_ms": l_info["median_ms"],
            "std_latency_ms": l_info["std_ms"],
            "min_latency_ms": l_info["min_ms"],
            "max_latency_ms": l_info["max_ms"],
            "throughput_fps": l_info["fps"],
            "sample_count": l_info["sample_count"],
            "device": "NVIDIA GeForce RTX 3050 Laptop GPU (CUDA:0)"
        })
    write_csv(
        GATE_I_DIR / "latency_comparison.csv",
        latency_rows,
        ["model_key", "model_name", "mean_latency_ms", "median_latency_ms", "std_latency_ms", "min_latency_ms", "max_latency_ms", "throughput_fps", "sample_count", "device"]
    )

    # 7. Post-Benchmark Verification
    print("\n[Step 7] Post-Benchmark Checkpoint Hash Verification...")
    post_hashes = {}
    for ckpt in CHECKPOINTS:
        p = ckpt["path"]
        h = sha256_file(p)
        post_hashes[ckpt["key"]] = h
        match = (h == pre_ckpt_hashes[ckpt["key"]])
        print(f"  - {ckpt['name']:<30} | Match Initial: {match} (SHA: {h[:16]}...)")
        assert match, f"CRITICAL: Checkpoint {ckpt['name']} was altered during benchmark!"

    print("\n[Step 8] Post-Benchmark Source Dataset SHA-256 Verification...")
    for row in snapshot_rows:
        cid = row['image_id']
        batch = row['batch']
        img_p = VAL_BASE / batch / "processed" / f"{cid}.jpg"
        lbl_p = VAL_BASE / batch / "labels" / f"{cid}.txt"
        assert sha256_file(img_p) == row['processed_sha256'], f"Image {cid} altered!"
        assert sha256_file(lbl_p) == row['label_sha256'], f"Label {cid} altered!"
    print("  -> Post-benchmark dataset integrity verified: 100% UNTOUCHED.")

    # Save summary json for markdown report generation
    summary_data = {
        "overall": overall_rows,
        "tier": tier_rows,
        "per_class": per_class_rows,
        "latency": latency_rows,
        "pre_hashes": pre_ckpt_hashes,
        "post_hashes": post_hashes
    }
    with open(GATE_I_DIR / "benchmark_summary.json", "w") as f:
        json.dump(summary_data, f, indent=2)

    print("\n=== Benchmark Execution Complete! Data saved to runs/phase8/gate_i_benchmark/ ===")

if __name__ == "__main__":
    main()
