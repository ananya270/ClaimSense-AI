"""Inspect CarDD_300 dataset structure, images, and annotations."""
import json
from pathlib import Path
from PIL import Image

def inspect_dataset():
    cardd_dir = Path("datasets/CarDD_300")
    print("=== CARDD DATASET INSPECTION ===")
    
    total_imgs = 0
    total_labels = 0
    corrupted_count = 0
    dimensions = set()
    formats = set()

    for split in ["train", "val", "test"]:
        img_dir = cardd_dir / split / "images"
        lbl_dir = cardd_dir / split / "labels"
        
        imgs = list(img_dir.glob("*.jpg")) + list(img_dir.glob("*.png")) + list(img_dir.glob("*.jpeg"))
        lbls = list(lbl_dir.glob("*.txt")) if lbl_dir.exists() else []
        
        total_imgs += len(imgs)
        total_labels += len(lbls)
        
        # Check corruptions and dimensions
        for img_p in imgs:
            try:
                with Image.open(img_p) as im:
                    im.verify()
                with Image.open(img_p) as im:
                    dimensions.add(im.size)
                    formats.add(im.format)
            except Exception as e:
                print(f"Corrupted image found: {img_p}: {e}")
                corrupted_count += 1
                
        print(f"Split '{split}': {len(imgs)} images, {len(lbls)} label files")

    print(f"Total usable images: {total_imgs}")
    print(f"Total label files: {total_labels}")
    print(f"Corrupted images: {corrupted_count}")
    print(f"Image formats: {formats}")
    print(f"Sample dimensions: {list(dimensions)[:8]} (total unique sizes: {len(dimensions)})")

    # Inspect COCO annotations
    anno_dir = cardd_dir / "annotations"
    print("\n=== COCO JSON ANNOTATIONS ===")
    for json_file in sorted(anno_dir.glob("*.json")):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        imgs = data.get("images", [])
        annos = data.get("annotations", [])
        cats = data.get("categories", [])
        print(f"File: {json_file.name}")
        print(f"  Images declared: {len(imgs)}")
        print(f"  Annotations: {len(annos)}")
        print(f"  Categories: {[c['name'] for c in cats]}")
        
        # Verify bounding box validity in COCO
        invalid_boxes = 0
        cat_counts = {}
        for a in annos:
            cid = a["category_id"]
            cat_counts[cid] = cat_counts.get(cid, 0) + 1
            bbox = a.get("bbox", [])
            if len(bbox) != 4 or bbox[2] <= 0 or bbox[3] <= 0:
                invalid_boxes += 1
        print(f"  Invalid boxes (w<=0 or h<=0): {invalid_boxes}")
        print(f"  Category counts: {cat_counts}")

    # Inspect YOLO labels
    print("\n=== YOLO TXT LABELS ===")
    class_counts = {}
    box_issues = 0
    total_yolo_boxes = 0
    for split in ["train", "val", "test"]:
        lbl_dir = cardd_dir / split / "labels"
        for lbl_p in lbl_dir.glob("*.txt"):
            with open(lbl_p, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 5:
                    cls_id = int(parts[0])
                    class_counts[cls_id] = class_counts.get(cls_id, 0) + 1
                    total_yolo_boxes += 1
                    coords = [float(x) for x in parts[1:5]]
                    for c in coords:
                        if c < 0.0 or c > 1.0:
                            box_issues += 1
    print(f"Total YOLO bounding boxes: {total_yolo_boxes}")
    print(f"YOLO Class distribution: {class_counts}")
    print(f"YOLO Coordinate out-of-bound issues (<0 or >1): {box_issues}")

if __name__ == "__main__":
    inspect_dataset()
