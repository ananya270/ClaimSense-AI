import io
import urllib.request
import json
from PIL import Image

USER_AGENT = "ClaimSenseAuditBot/2.0 (claimsense-ai-research; contact@claimsense.ai)"

# Check meta.json or annotations in DrBimmer
url = "https://huggingface.co/api/datasets/DrBimmer/car-parts-and-damage-dataset/tree/main/Car%20damages%20dataset/File1/ann"
req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print(f"Annotation files in Car damages File1: {len(data)}")
        # inspect first 5 annotations
        for item in data[:5]:
            ann_path = item["path"]
            ann_url = f"https://huggingface.co/datasets/DrBimmer/car-parts-and-damage-dataset/resolve/main/{urllib.parse.quote(ann_path)}"
            with urllib.request.urlopen(urllib.request.Request(ann_url, headers={"User-Agent": USER_AGENT})) as aresp:
                ann_data = json.loads(aresp.read().decode("utf-8"))
                size = ann_data.get("size", {})
                print(f"{item['path']}: {size}")
except Exception as e:
    print(f"Error: {e}")
