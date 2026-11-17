import urllib.request
import json

url = "https://huggingface.co/api/datasets/DrBimmer/car-parts-and-damage-dataset/tree/main/Car%20damages%20dataset/File1/img"
req = urllib.request.Request(url, headers={"User-Agent": "ClaimSenseAuditBot/2.0"})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print(f"Car damages dataset sub-items: {len(data)}")
        for item in data[:15]:
            print(f"- {item.get('type')}: {item.get('path')}")
except Exception as e:
    print(f"Error: {e}")

