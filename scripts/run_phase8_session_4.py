"""ClaimSense AI - Phase 8 Session 4 Training Runner.

Executes controlled fine-tuning on datasets/CarDD_Expanded_v1 (310 images).
Starting Checkpoint: runs/phase8/session_2/weights/best.pt
Output Directory: runs/phase8/session_4_training_01/
Resolution: 640px, Batch: 4 (fallback: 2), AMP: True, Workers: 2 (fallback: 0), Max Epochs: 20
Optimizer: AdamW (lr0: 0.001, lrf: 0.01), Mosaic: 0.5, Close Mosaic: 5, Erasing: 0.0
"""

import os
import sys
import time
import json
import hashlib
import threading
import subprocess
import multiprocessing
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch
from ultralytics import YOLO


def get_gpu_smi_metrics():
    """Query temperature, VRAM usage, and power via nvidia-smi."""
    try:
        res = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=temperature.gpu,memory.used,memory.total,power.draw",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        line = res.stdout.strip()
        parts = [p.strip() for p in line.split(",")]
        return {
            "temp_c": int(parts[0]),
            "mem_used_mib": float(parts[1]),
            "mem_total_mib": float(parts[2]),
            "power_draw_w": parts[3],
        }
    except Exception as e:
        return {"error": str(e)}


def get_file_hash(path: Path) -> str:
    """Compute SHA256 of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


class GpuMonitor(threading.Thread):
    """Background monitor for peak GPU temperature and system metrics."""

    def __init__(self, interval_sec: float = 1.0):
        super().__init__()
        self.interval_sec = interval_sec
        self.stop_requested = threading.Event()
        self.max_temp = 0
        self.max_vram_used_smi = 0.0
        self.thermal_warning_triggered = False
        self.history = []

    def run(self):
        while not self.stop_requested.is_set():
            metrics = get_gpu_smi_metrics()
            if "temp_c" in metrics:
                temp = metrics["temp_c"]
                mem = metrics["mem_used_mib"]
                if temp > self.max_temp:
                    self.max_temp = temp
                if temp >= 82:
                    self.thermal_warning_triggered = True
                if mem > self.max_vram_used_smi:
                    self.max_vram_used_smi = mem
                self.history.append({"time": time.time(), "temp": temp, "mem": mem})
            time.sleep(self.interval_sec)

    def stop(self):
        self.stop_requested.set()


def main():
    print("=" * 80, flush=True)
    print("  CLAIMSENSE AI - PHASE 8 YOLO SESSION 4 TRAINING EXECUTION", flush=True)
    print("  Dataset: CarDD_Expanded_v1 (310 Train Images / 829 Instances)", flush=True)
    print("  Initialization: Session 2 Best Checkpoint (runs/phase8/session_2/weights/best.pt)", flush=True)
    print("  Target Destination: runs/phase8/session_4_training_01/", flush=True)
    print("=" * 80, flush=True)

    # 1. Environment & CUDA Pre-check
    print("\n[1] Environment & Hardware Verification...", flush=True)
    if not torch.cuda.is_available():
        print("ERROR: CUDA is not available. Halting.", flush=True)
        sys.exit(1)

    device_name = torch.cuda.get_device_name(0)
    total_vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    pre_smi = get_gpu_smi_metrics()
    print(f"    - GPU Device:        {device_name}", flush=True)
    print(f"    - Total VRAM:        {total_vram_gb:.2f} GB", flush=True)
    print(f"    - Current Temp:      {pre_smi.get('temp_c')} °C", flush=True)
    print(f"    - Initial VRAM Used: {pre_smi.get('mem_used_mib')} MiB", flush=True)

    # Pre-training safeguard: Check production model hash
    prod_model_path = PROJECT_ROOT / "models" / "phase5" / "best.pt"
    initial_prod_hash = get_file_hash(prod_model_path)
    assert initial_prod_hash == "90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565", "Production hash mismatch!"
    print(f"    - Production Model:  {prod_model_path.name} (SHA256: {initial_prod_hash[:16]}... VERIFIED)", flush=True)

    # Source checkpoint verification
    source_ckpt = PROJECT_ROOT / "runs" / "phase8" / "session_2" / "weights" / "best.pt"
    if not source_ckpt.exists():
        print(f"ERROR: Session 2 best checkpoint not found at: {source_ckpt}", flush=True)
        sys.exit(1)
    s2_hash = get_file_hash(source_ckpt)
    assert s2_hash == "2ee0a56749ceba72da863fd3496f080ee06f26409daa4e9588fb69ee149333c5", "Session 2 best hash mismatch!"
    print(f"    - Source Checkpoint: {source_ckpt.name} (SHA256: {s2_hash[:16]}... VERIFIED)", flush=True)

    # Dataset verification
    cardd_yaml = PROJECT_ROOT / "datasets" / "CarDD_Expanded_v1" / "dataset.yaml"
    if not cardd_yaml.exists():
        print(f"ERROR: Dataset YAML not found at: {cardd_yaml}", flush=True)
        sys.exit(1)

    train_imgs_count = len(list((PROJECT_ROOT / "datasets" / "CarDD_Expanded_v1" / "train" / "images").glob("*.*")))
    train_lbls_count = len(list((PROJECT_ROOT / "datasets" / "CarDD_Expanded_v1" / "train" / "labels").glob("*.txt")))
    val_imgs_count = len(list((PROJECT_ROOT / "datasets" / "CarDD_Expanded_v1" / "val" / "images").glob("*.*")))
    test_imgs_count = len(list((PROJECT_ROOT / "datasets" / "CarDD_300" / "test" / "images").glob("*.*")))

    assert train_imgs_count == 310 and train_lbls_count == 310, f"Train count mismatch: {train_imgs_count}/{train_lbls_count}"
    assert val_imgs_count == 45, f"Val count mismatch: {val_imgs_count}"
    assert test_imgs_count == 45, f"Test count mismatch: {test_imgs_count}"
    print(f"    - Dataset Verified:  Train={train_imgs_count}, Val={val_imgs_count}, Test={test_imgs_count} (FROZEN)", flush=True)

    # Destination directory protection
    project_dir = PROJECT_ROOT / "runs" / "phase8"
    run_name = "session_4_training_01"
    run_dir = project_dir / run_name

    if run_dir.exists():
        print(f"ERROR: Destination directory already exists: {run_dir}. Aborting to prevent overwrite.", flush=True)
        sys.exit(1)
    print(f"    - Target Dir:        {run_dir} (CONFIRMED NEW & AVAILABLE)", flush=True)

    # 2. Hyperparameters
    initial_batch_size = 4
    batch_size = initial_batch_size
    imgsz = 640
    workers = 2
    epochs = 20
    patience = 7

    print("\n[2] Session 4 Training Hyperparameters:", flush=True)
    print(f"    - Source Weights:    {source_ckpt}", flush=True)
    print(f"    - Dataset Config:    {cardd_yaml}", flush=True)
    print(f"    - Epochs:            {epochs} (patience={patience})", flush=True)
    print(f"    - Image Size:        {imgsz}", flush=True)
    print(f"    - Initial Batch:     {batch_size}", flush=True)
    print(f"    - Workers:           {workers}", flush=True)
    print(f"    - Optimizer:         AdamW (lr0=0.001, lrf=0.01, weight_decay=0.0005, cos_lr=True)", flush=True)
    print(f"    - Warmup:            2.0 epochs (warmup_momentum=0.8, warmup_bias_lr=0.1)", flush=True)
    print(f"    - Augmentations:     mosaic=0.5, close_mosaic=5, erasing=0.0, fliplr=0.5, flipud=0.0", flush=True)
    print(f"    - Loss Gains:        box=7.5, cls=0.5, dfl=1.5", flush=True)
    print(f"    - Device:            CUDA 0 (AMP=True)", flush=True)

    # Start GPU monitor
    monitor = GpuMonitor(interval_sec=1.0)
    monitor.start()

    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats(0)

    # 3. Model Training Execution with OOM & Worker Fallbacks
    print(f"\n[3] Launching Model Training Session 4...", flush=True)
    start_train_time = time.perf_counter()
    oom_encountered = False
    worker_fallback_triggered = False

    def execute_train(b_size, w_count):
        m = YOLO(str(source_ckpt))
        res = m.train(
            data=str(cardd_yaml),
            epochs=epochs,
            patience=patience,
            imgsz=imgsz,
            batch=b_size,
            workers=w_count,
            device=0,
            amp=True,
            optimizer="AdamW",
            lr0=0.001,
            lrf=0.01,
            momentum=0.937,
            weight_decay=0.0005,
            cos_lr=True,
            warmup_epochs=2.0,
            warmup_momentum=0.8,
            warmup_bias_lr=0.1,
            box=7.5,
            cls=0.5,
            dfl=1.5,
            mosaic=0.5,
            close_mosaic=5,
            erasing=0.0,
            hsv_h=0.015,
            hsv_s=0.7,
            hsv_v=0.4,
            degrees=0.0,
            translate=0.1,
            scale=0.5,
            shear=0.0,
            perspective=0.0,
            flipud=0.0,
            fliplr=0.5,
            seed=42,
            project=str(project_dir),
            name=run_name,
            exist_ok=False,
            save=True,
            save_period=-1,
            val=True,
            plots=True,
            verbose=True,
        )
        return res

    try:
        train_results = execute_train(batch_size, workers)
    except torch.cuda.OutOfMemoryError as oom_err:
        oom_encountered = True
        print(f"\n[WARNING] CUDA Out of Memory with batch={batch_size}: {oom_err}", flush=True)
        print("          Executing safety fallback: Reducing batch size to 2...", flush=True)
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats(0)
        batch_size = 2
        # Clean incomplete directory if created
        if run_dir.exists():
            shutil.rmtree(run_dir)
        train_results = execute_train(batch_size, workers)
    except Exception as exc:
        if "multiprocessing" in str(exc).lower() or "freeze_support" in str(exc).lower() or "bootstrap" in str(exc).lower():
            worker_fallback_triggered = True
            print(f"\n[WARNING] Worker spawn error: {exc}", flush=True)
            print("          Executing safety fallback: Setting workers=0...", flush=True)
            torch.cuda.empty_cache()
            workers = 0
            if run_dir.exists():
                shutil.rmtree(run_dir)
            train_results = execute_train(batch_size, workers)
        else:
            monitor.stop()
            monitor.join(timeout=2.0)
            raise exc

    training_duration_sec = time.perf_counter() - start_train_time
    monitor.stop()
    monitor.join(timeout=2.0)

    # 4. Measure GPU & Performance Metrics
    peak_alloc_mib = torch.cuda.max_memory_allocated(0) / (1024**2)
    peak_res_mib = torch.cuda.max_memory_reserved(0) / (1024**2)
    post_smi = get_gpu_smi_metrics()

    print("\n[4] Training Execution Performance:", flush=True)
    print(f"    - Duration:          {training_duration_sec:.2f} seconds ({training_duration_sec/60:.2f} minutes)", flush=True)
    print(f"    - Final Batch Size:  {batch_size} (OOM fallback: {oom_encountered})", flush=True)
    print(f"    - Final Workers:     {workers} (Worker fallback: {worker_fallback_triggered})", flush=True)
    print(f"    - Peak VRAM Alloc:   {peak_alloc_mib:.2f} MiB ({peak_alloc_mib/1024:.2f} GB)", flush=True)
    print(f"    - Peak VRAM Reserved:{peak_res_mib:.2f} MiB ({peak_res_mib/1024:.2f} GB)", flush=True)
    print(f"    - Max GPU Temp:      {monitor.max_temp} °C", flush=True)
    print(f"    - Thermal Warning:   {monitor.thermal_warning_triggered}", flush=True)

    # 5. Checkpoint Verification
    weights_dir = run_dir / "weights"
    best_pt = weights_dir / "best.pt"
    last_pt = weights_dir / "last.pt"

    assert best_pt.exists(), f"best.pt not found at {best_pt}"
    assert last_pt.exists(), f"last.pt not found at {last_pt}"

    best_sha = get_file_hash(best_pt)
    last_sha = get_file_hash(last_pt)
    best_size = best_pt.stat().st_size
    last_size = last_pt.stat().st_size

    print("\n[5] Checkpoint Verification:", flush=True)
    print(f"    - best.pt Path:      {best_pt}", flush=True)
    print(f"    - best.pt Size:      {best_size:,} bytes ({best_size/(1024**2):.2f} MB)", flush=True)
    print(f"    - best.pt SHA256:    {best_sha}", flush=True)
    print(f"    - last.pt SHA256:    {last_sha}", flush=True)

    # Re-verify production model remains untouched
    post_prod_hash = get_file_hash(prod_model_path)
    assert post_prod_hash == initial_prod_hash, "CRITICAL: Production model hash changed during training!"
    print(f"    - Production Model:  {prod_model_path.name} (SHA256: {post_prod_hash[:16]}... 100% UNTOUCHED)", flush=True)

    # 6. Parse Epoch-wise Metrics from results.csv
    results_csv = run_dir / "results.csv"
    epoch_records = []
    if results_csv.exists():
        with open(results_csv, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
            if len(lines) >= 2:
                headers = [h.strip() for h in lines[0].split(",")]
                for line in lines[1:]:
                    vals = [float(v.strip()) for v in line.split(",")]
                    epoch_records.append(dict(zip(headers, vals)))

    print(f"\n[6] Epoch Progression Summary ({len(epoch_records)} Epochs Completed):", flush=True)
    print(f"{'Epoch':<6} | {'Train Box':<10} | {'Train Cls':<10} | {'Val Box':<10} | {'Val Cls':<10} | {'mAP50':<8} | {'mAP50-95':<8}", flush=True)
    print("-" * 80, flush=True)
    for rec in epoch_records:
        ep = int(rec.get("epoch", 0))
        tb = rec.get("train/box_loss", 0.0)
        tc = rec.get("train/cls_loss", 0.0)
        vb = rec.get("val/box_loss", 0.0)
        vc = rec.get("val/cls_loss", 0.0)
        map50 = rec.get("metrics/mAP50(B)", 0.0)
        map95 = rec.get("metrics/mAP50-95(B)", 0.0)
        print(f"{ep:<6} | {tb:<10.4f} | {tc:<10.4f} | {vb:<10.4f} | {vc:<10.4f} | {map50:<8.4f} | {map95:<8.4f}", flush=True)

    # 7. Independent Validation Split Evaluation on best.pt (strictly on val, NOT test)
    print("\n[7] Evaluating Best Checkpoint on Validation Split (CarDD_Expanded_v1/val)...", flush=True)
    val_model = YOLO(str(best_pt))
    val_metrics = val_model.val(
        data=str(cardd_yaml),
        split="val",
        imgsz=640,
        batch=1,
        device=0,
        half=True,
        workers=0,
        plots=False,
        verbose=False,
    )

    class_names = val_model.names
    print("\n=== Validation Split Per-Class Performance ===", flush=True)
    val_class_summary = {}
    for i, c_name in class_names.items():
        p = float(val_metrics.box.p[i]) if i < len(val_metrics.box.p) else 0.0
        r = float(val_metrics.box.r[i]) if i < len(val_metrics.box.r) else 0.0
        f1 = float(val_metrics.box.f1[i]) if i < len(val_metrics.box.f1) else 0.0
        m50 = float(val_metrics.box.ap50[i]) if i < len(val_metrics.box.ap50) else 0.0
        m95 = float(val_metrics.box.ap[i]) if i < len(val_metrics.box.ap) else 0.0
        val_class_summary[c_name] = {
            "precision": round(p, 4),
            "recall": round(r, 4),
            "f1": round(f1, 4),
            "mAP50": round(m50, 4),
            "mAP50_95": round(m95, 4),
        }
        print(f"  {i}: {c_name:<15s} | P: {p:.4f} | R: {r:.4f} | F1: {f1:.4f} | mAP50: {m50:.4f} | mAP50-95: {m95:.4f}", flush=True)

    all_p = float(val_metrics.box.mp)
    all_r = float(val_metrics.box.mr)
    all_map50 = float(val_metrics.box.map50)
    all_map95 = float(val_metrics.box.map)
    print("-" * 75, flush=True)
    print(f"  Overall Validation: | P: {all_p:.4f} | R: {all_r:.4f} | mAP50: {all_map50:.4f} | mAP50-95: {all_map95:.4f}", flush=True)

    # 8. Save Machine-Readable Training Summary
    summary_payload = {
        "run_id": "session_4_training_01",
        "output_dir": str(run_dir),
        "execution_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "training_duration_seconds": round(training_duration_sec, 2),
        "epochs_completed": len(epoch_records),
        "batch_size_used": batch_size,
        "workers_used": workers,
        "oom_fallback_triggered": oom_encountered,
        "worker_fallback_triggered": worker_fallback_triggered,
        "hardware_metrics": {
            "device": device_name,
            "peak_vram_allocated_mb": round(peak_alloc_mib, 2),
            "peak_vram_reserved_mb": round(peak_res_mib, 2),
            "max_gpu_temp_c": monitor.max_temp,
            "final_gpu_temp_c": post_smi.get("temp_c"),
            "thermal_warning": monitor.thermal_warning_triggered,
        },
        "checkpoints": {
            "best_pt": {
                "path": str(best_pt),
                "sha256": best_sha,
                "size_bytes": best_size,
            },
            "last_pt": {
                "path": str(last_pt),
                "sha256": last_sha,
                "size_bytes": last_size,
            },
            "production_model_untouched": True,
            "production_sha256": post_prod_hash,
        },
        "validation_metrics": {
            "overall": {
                "precision": round(all_p, 4),
                "recall": round(all_r, 4),
                "mAP50": round(all_map50, 4),
                "mAP50_95": round(all_map95, 4),
            },
            "per_class": val_class_summary,
        },
    }

    summary_json_path = run_dir / "training_summary.json"
    with open(summary_json_path, "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2)

    print(f"\n[8] Training summary saved to: {summary_json_path}", flush=True)
    print("=" * 80, flush=True)
    print("  PHASE 8 SESSION 4 TRAINING COMPLETE. READY FOR BENCHMARK REVIEW.", flush=True)
    print("=" * 80, flush=True)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
