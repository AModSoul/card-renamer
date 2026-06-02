#!/usr/bin/env python3
"""Test different heights to capture 'Boat' in Abrade variant"""

from pathlib import Path
from PIL import Image
import numpy as np
from image_renamer import get_easyocr_reader

folder = Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed")
files = list(folder.glob("*Abrade*Youre*"))

if not files:
    print("Abrade variant not found")
    import sys
    sys.exit(1)

test_image = files[0]
img = Image.open(test_image)
width, height = img.size

reader = get_easyocr_reader()

for height_pct in [0.20, 0.22, 0.25, 0.28, 0.30]:
    print("\n" + "=" * 60)
    print(f"Height: {height_pct*100}% (width: 70%)")
    print("=" * 60)
    
    crop_width = int(width * 0.70)
    crop_height = int(height * height_pct)
    region = img.crop((0, 0, crop_width, crop_height))
    
    results = reader.readtext(np.array(region), paragraph=False)
    
    print(f"\nDetections (conf > 0.6):")
    for bbox, text, confidence in results:
        if confidence > 0.6:
            y_pos = bbox[0][1]
            print(f"  '{text}' (conf: {confidence:.3f}, y: {y_pos:.0f})")
