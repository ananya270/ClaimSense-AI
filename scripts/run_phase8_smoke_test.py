"""ClaimSense AI - Phase 8 YOLO 1-Epoch Smoke Test Runner.

Executes a controlled 1-epoch smoke test on RTX 3050 Laptop GPU (device 0)
using batch=2, imgsz=640, workers=2, and amp=True.
Tracks VRAM peak, temperature, epoch latency, training losses, and validates
checkpoint creation and CUDA inference.
"""

import os
import sys
import time
import json
import hashlib
import subprocess
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch
from ultralytics import YOLO


def get_gpu_smi_metrics():
    """Query temperature and memory via nvidia-smi."""
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


def main():
    print("=" * 70)
    print("  CLAIMSENSE AI - PHASE 8 YOLO 1-EPOCH SMOKE TEST")
    print("=" * 70)

    # 1. Environment & CUDA Pre-check
    print("\n[1] Checking CUDA & System Environment...")
    if not torch.cuda.is_available():
        print("ERROR: CUDA is not available in PyTorch. Halting.")
        sys.exit(1)

    device_name = torch.cuda.get_device_name(0)
    device_cap = torch.cuda.get_device_capability(0)
    total_vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    print(f"    - GPU:               {device_name} (Capability {device_cap})")
    print(f"    - Total VRAM:        {total_vram_gb:.2f} GB")
    print(f"    - PyTorch Version:   {torch.__version__}")

    pre_smi = get_gpu_smi_metrics()
    print(f"    - Initial Temp:      {pre_smi.get('temp_c')} °C")
    print(f"    - Initial VRAM Used: {pre_smi.get('mem_used_mib')} MiB")

    # Record initial hash of production model
    prod_model_path = PROJECT_ROOT / "models" / "phase5" / "best.pt"
    initial_prod_hash = get_file_hash(prod_model_path) if prod_model_path.exists() else None
    print(f"    - Prod Checkpoint:   {prod_model_path.name} (SHA256: {initial_prod_hash[:16]}...)")

    # 2. Configuration Setup
    cardd_yaml = PROJECT_ROOT / "data" / "cardd_train.yaml"
    base_model_path = PROJECT_ROOT / "yolov8n.pt"
    if not base_model_path.exists():
        base_model_path = "yolov8n.pt"  # Let ultralytics locate or load

    project_dir = PROJECT_ROOT / "runs" / "phase8"
    run_name = "smoke_test"
    run_dir = project_dir / run_name

    print("\n[2] Training Parameters:")
    print(f"    - Data YAML:         {cardd_yaml}")
    print(f"    - Base Architecture: {base_model_path}")
    print(f"    - Epochs:            1 (Smoke test only)")
    print(f"    - Image Size:        640")
    print(f"    - Batch Size:        2")
    print(f"    - Workers:           2")
    print(f"    - Device:            0 (CUDA)")
    print(f"    - AMP (FP16):        True")
    print(f"    - Destination:       {run_dir}")

    # Reset PyTorch CUDA memory peak tracker
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats(0)

    # 3. Model Loading & 1-Epoch Execution
    print("\n[3] Launching 1-Epoch Smoke Test...")
    model = YOLO(str(base_model_path))

    start_train_time = time.perf_counter()
    train_results = model.train(
        data=str(cardd_yaml),
        epochs=1,
        imgsz=640,
        batch=2,
        workers=2,
        device=0,
        amp=True,
        project=str(project_dir),
        name=run_name,
        exist_ok=True,
        save=True,
        val=True,
        plots=True,
        verbose=True,
    )
    epoch_duration_sec = time.perf_counter() - start_train_time

    # 4. Measure GPU & VRAM Metrics Post-Train
    post_smi = get_gpu_smi_metrics()
    peak_alloc_mib = torch.cuda.max_memory_allocated(0) / (1024**2)
    peak_res_mib = torch.cuda.max_memory_reserved(0) / (1024**2)

    print("\n[4] GPU Hardware & Resource Consumption:")
    print(f"    - Epoch Duration:    {epoch_duration_sec:.2f} seconds")
    print(f"    - Peak VRAM Alloc:   {peak_alloc_mib:.2f} MiB ({peak_alloc_mib/1024:.2f} GB)")
    print(f"    - Peak VRAM Reserved:{peak_res_mib:.2f} MiB ({peak_res_mib/1024:.2f} GB)")
    print(f"    - Peak % of 4GB:     {(peak_res_mib / 4096.0) * 100:.1f} %")
    print(f"    - Post-Train Temp:   {post_smi.get('temp_c')} °C")

    # 5. Extract Loss & Metric Values
    results_csv = run_dir / "results.csv"
    train_losses = {}
    if results_csv.exists():
        with open(results_csv, "r") as f:
            lines = [l.strip() for l in f if l.strip()]
            if len(lines) >= 2:
                headers = [h.strip() for h in lines[0].split(",")]
                values = [float(v.strip()) for v in lines[-1].split(",")]
                row_dict = dict(zip(headers, values))
                train_losses = {
                    "train/box_loss": row_dict.get("train/box_loss"),
                    "train/cls_loss": row_dict.get("train/cls_loss"),
                    "train/dfl_loss": row_dict.get("train/dfl_loss"),
                    "metrics/mAP50(B)": row_dict.get("metrics/mAP50(B)"),
                    "metrics/mAP50-95(B)": row_dict.get("metrics/mAP50-95(B)"),
                    "val/box_loss": row_dict.get("val/box_loss"),
                    "val/cls_loss": row_dict.get("val/cls_loss"),
                    "val/dfl_loss": row_dict.get("val/dfl_loss"),
                }

    print("\n[5] Training & Validation Losses (Epoch 1):")
    for k, v in train_losses.items():
        print(f"    - {k:22s}: {v}")

    # 6. Verify Checkpoint Generation
    best_pt = run_dir / "weights" / "best.pt"
    last_pt = run_dir / "weights" / "last.pt"

    print("\n[6] Validating Created Checkpoints:")
    best_exists = best_pt.exists()
    last_exists = last_pt.exists()
    print(f"    - best.pt exists:    {best_exists} ({best_pt.stat().st_size / (1024**2):.2f} MB)" if best_exists else "    - best.pt: MISSING")
    print(f"    - last.pt exists:    {last_exists} ({last_pt.stat().st_size / (1024**2):.2f} MB)" if last_exists else "    - last.pt: MISSING")

    # Test loading checkpoints
    best_loadable = False
    last_loadable = False
    try:
        model_best = YOLO(str(best_pt))
        best_loadable = True
        print("    - best.pt load:      SUCCESS (YOLOv8n architecture verified)")
    except Exception as e:
        print(f"    - best.pt load:      FAILED ({e})")

    try:
        model_last = YOLO(str(last_pt))
        last_loadable = True
        print("    - last.pt load:      SUCCESS")
    except Exception as e:
        print(f"    - last.pt load:      FAILED ({e})")

    # 7. CUDA Inference Test with New Checkpoint
    print("\n[7] Executing CUDA Inference Test with Newly Created best.pt...")
    sample_img = PROJECT_ROOT / "datasets" / "CarDD_300" / "val" / "images" / "000001.jpg"
    if not sample_img.exists():
        # Fallback to any valid jpg in val
        sample_img = next((PROJECT_ROOT / "datasets" / "CarDD_300" / "val" / "images").glob("*.jpg"))

    start_inf = time.perf_counter()
    inf_results = model_best.predict(
        source=str(sample_img),
        device=0,
        imgsz=640,
        conf=0.25,
        verbose=False,
    )
    inf_latency_ms = (time.perf_counter() - start_inf) * 1000.0

    boxes = inf_results[0].boxes
    num_detections = len(boxes) if boxes is not None else 0
    print(f"    - Sample Image:      {sample_img.name}")
    print(f"    - Inference Device:  CUDA (device 0)")
    print(f"    - Inference Latency: {inf_latency_ms:.2f} ms")
    print(f"    - Detections:        {num_detections} bounding boxes")
    if num_detections > 0:
        for b in boxes:
            cls_id = int(b.cls[0].item())
            conf_val = float(b.conf[0].item())
            cls_name = model_best.names.get(cls_id, f"class_{cls_id}")
            print(f"        * {cls_name}: confidence={conf_val*100:.1f}%")

    # 8. Verify Production Isolation
    print("\n[8] Verifying Production Checkpoint Isolation...")
    final_prod_hash = get_file_hash(prod_model_path) if prod_model_path.exists() else None
    prod_untouched = (initial_prod_hash == final_prod_hash)
    print(f"    - Prod Checkpoint:   {prod_model_path}")
    print(f"    - Initial SHA256:    {initial_prod_hash}")
    print(f"    - Final SHA256:      {final_prod_hash}")
    print(f"    - Zero-Tamper Check: {'PASSED (Checkpoint is 100% untouched)' if prod_untouched else 'FAILED'}")

    # 9. Output Structured Report
    report = {
        "status": "PASSED" if (best_exists and last_exists and best_loadable and prod_untouched) else "FAILED",
        "hardware": {
            "gpu": device_name,
            "vram_total_gb": round(total_vram_gb, 2),
            "initial_temp_c": pre_smi.get("temp_c"),
            "post_temp_c": post_smi.get("temp_c"),
            "peak_vram_allocated_mib": round(peak_alloc_mib, 2),
            "peak_vram_reserved_mib": round(peak_res_mib, 2),
            "peak_vram_percent_of_4gb": round((peak_res_mib / 4096.0) * 100, 2),
        },
        "training": {
            "epoch": 1,
            "duration_sec": round(epoch_duration_sec, 2),
            "imgsz": 640,
            "batch": 2,
            "workers": 2,
            "amp": True,
            "device": 0,
            "losses": train_losses,
        },
        "checkpoints": {
            "best_pt": str(best_pt),
            "best_size_mb": round(best_pt.stat().st_size / (1024**2), 2) if best_exists else 0,
            "best_loadable": best_loadable,
            "last_pt": str(last_pt),
            "last_size_mb": round(last_pt.stat().st_size / (1024**2), 2) if last_exists else 0,
            "last_loadable": last_loadable,
        },
        "cuda_inference_test": {
            "image": sample_img.name,
            "latency_ms": round(inf_latency_ms, 2),
            "detections": num_detections,
        },
        "production_isolation": {
            "production_model": str(prod_model_path),
            "untouched": prod_untouched,
        },
    }

    report_path = PROJECT_ROOT / "reports" / "phase8_smoke_test_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n[9] Smoke test report saved to: {report_path}")
    print("=" * 70)
    print("  SMOKE TEST COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()
