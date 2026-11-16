import os
import sys
import time
import json
import csv
from pathlib import Path
from ultralytics import YOLO

def main():
    root_dir = Path(__file__).resolve().parent.parent
    data_yaml = root_dir / "data" / "cardd.yaml"
    weights_path = root_dir / "models" / "vehicle_damage" / "best.pt"
    reports_dir = root_dir / "reports" / "vehicle_damage"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Loading model from {weights_path}")
    model = YOLO(str(weights_path))
    
    print(f"Evaluating model on test split using {data_yaml}...")
    start_time = time.time()
    metrics = model.val(
        data=str(data_yaml),
        split="test",
        imgsz=640,
        batch=1,
        device="cpu",
        plots=True,
        save_json=False
    )
    total_eval_time = time.time() - start_time
    
    # metrics.results_dict contains metrics
    # metrics.box contains detailed box results:
    #   p (precision), r (recall), f1, all_ap (mAP50-95 for each class)
    #   map50, map75, map (mean mAP50-95)
    class_names = model.names
    print("Class names:", class_names)
    
    # Ultralytics metric extraction
    p_overall = float(metrics.box.mp)
    r_overall = float(metrics.box.mr)
    map50_overall = float(metrics.box.map50)
    map_overall = float(metrics.box.map)
    f1_overall = (2 * p_overall * r_overall / (p_overall + r_overall)) if (p_overall + r_overall) > 0 else 0.0
    
    # Per-class metrics
    per_class_results = []
    p_classes = metrics.box.p
    r_classes = metrics.box.r
    f1_classes = metrics.box.f1
    ap50_classes = metrics.box.ap50
    ap_classes = metrics.box.ap
    
    for cls_idx, cls_name in class_names.items():
        p_c = float(p_classes[cls_idx]) if cls_idx < len(p_classes) else 0.0
        r_c = float(r_classes[cls_idx]) if cls_idx < len(r_classes) else 0.0
        f1_c = float(f1_classes[cls_idx]) if cls_idx < len(f1_classes) else 0.0
        map50_c = float(ap50_classes[cls_idx]) if cls_idx < len(ap50_classes) else 0.0
        map_c = float(ap_classes[cls_idx]) if cls_idx < len(ap_classes) else 0.0
        
        per_class_results.append({
            "class_id": cls_idx,
            "class_name": cls_name,
            "precision": round(p_c, 4),
            "recall": round(r_c, 4),
            "f1_score": round(f1_c, 4),
            "map50": round(map50_c, 4),
            "map50_95": round(map_c, 4)
        })
    
    # Latency per image
    speed_dict = metrics.speed  # preprocess, inference, loss, postprocess in ms
    total_latency_ms = sum(speed_dict.values())
    
    evaluation_data = {
        "dataset": "CarDD_300",
        "split": "test",
        "num_test_images": 45,
        "evaluation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model_architecture": "YOLOv8n",
        "weights_path": str(weights_path),
        "device": "cpu",
        "overall_metrics": {
            "precision": round(p_overall, 4),
            "recall": round(r_overall, 4),
            "f1_score": round(f1_overall, 4),
            "map50": round(map50_overall, 4),
            "map50_95": round(map_overall, 4)
        },
        "per_class_metrics": per_class_results,
        "latency_metrics": {
            "preprocess_ms": round(speed_dict.get("preprocess", 0.0), 2),
            "inference_ms": round(speed_dict.get("inference", 0.0), 2),
            "postprocess_ms": round(speed_dict.get("postprocess", 0.0), 2),
            "total_latency_ms": round(total_latency_ms, 2)
        },
        "total_evaluation_time_seconds": round(total_eval_time, 2)
    }
    
    # Save JSON
    json_path = reports_dir / "evaluation_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(evaluation_data, f, indent=2)
    print(f"Saved evaluation JSON to {json_path}")
    
    # Save CSV
    csv_path = reports_dir / "evaluation_metrics.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric Level", "Class ID", "Class Name", "Precision", "Recall", "F1-Score", "mAP@50", "mAP@50-95"])
        writer.writerow(["Overall", "-", "All Classes", 
                         round(p_overall, 4), round(r_overall, 4), round(f1_overall, 4), 
                         round(map50_overall, 4), round(map_overall, 4)])
        for pc in per_class_results:
            writer.writerow(["Per-Class", pc["class_id"], pc["class_name"], 
                             pc["precision"], pc["recall"], pc["f1_score"], 
                             pc["map50"], pc["map50_95"]])
        writer.writerow([])
        writer.writerow(["Latency Stage", "Duration (ms)"])
        writer.writerow(["Preprocess", round(speed_dict.get("preprocess", 0.0), 2)])
        writer.writerow(["Inference", round(speed_dict.get("inference", 0.0), 2)])
        writer.writerow(["Postprocess", round(speed_dict.get("postprocess", 0.0), 2)])
        writer.writerow(["Total Latency Per Image", round(total_latency_ms, 2)])
    print(f"Saved evaluation CSV to {csv_path}")

if __name__ == "__main__":
    main()
