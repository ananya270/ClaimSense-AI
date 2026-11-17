import os
from PIL import Image
import numpy as np

WORKSPACE = r"C:\Users\ansh9\Desktop\Claimsense Ai"
RAW_DIR = os.path.join(WORKSPACE, "datasets", "CarDD_Independent_Val_v1", "batch_01", "raw_restricted")

images_to_check = [
    ("CS_VAL_016", "CS_VAL_016_raw.jpg", "Dent"),
    ("CS_VAL_017", "CS_VAL_017_raw.jpg", "Dent"),
    ("CS_VAL_020", "CS_VAL_020_raw.png", "Crack"),
    ("CS_VAL_021", "CS_VAL_021_raw.png", "Crack"),
    ("CS_VAL_022", "CS_VAL_022_raw.jpg", "Lamp Broken"),
    ("CS_VAL_023", "CS_VAL_023_raw.png", "Lamp Broken"),
    ("CS_VAL_024", "CS_VAL_024_raw.png", "Scratch"),
    ("CS_VAL_025", "CS_VAL_025_raw.png", "Dent")
]

print("="*70)
print("INSPECTING SUB-800x600 CANDIDATES")
print("="*70)

for cid, fname, cat in images_to_check:
    fpath = os.path.join(RAW_DIR, fname)
    if not os.path.exists(fpath):
        print(f"Missing {fname}")
        continue
    img = Image.open(fpath)
    w, h = img.size
    total_area = w * h
    
    # Calculate aspect ratio
    aspect = w / h
    
    # Check orientation
    orient = "Landscape" if w >= h else "Portrait"
    
    # Check 800x600, 640x400, 600x400 thresholds
    pass_800x600 = (w >= 800 and h >= 600)
    pass_640x400 = (w >= 640 and h >= 400)
    pass_600x400 = (w >= 600 and h >= 400)
    
    # Orientation-agnostic check min/max
    pass_minmax_600x400 = (min(w, h) >= 400 and max(w, h) >= 600)
    pass_minmax_640x400 = (min(w, h) >= 400 and max(w, h) >= 640)
    
    print(f"\n{cid} ({cat}): {w}x{h} ({orient}, aspect {aspect:.2f})")
    print(f"  800x600 (Strict): {pass_800x600}")
    print(f"  640x400 (Fixed WxH): {pass_640x400} | (MinMax): {pass_minmax_640x400}")
    print(f"  600x400 (Fixed WxH): {pass_600x400} | (MinMax): {pass_minmax_600x400}")
