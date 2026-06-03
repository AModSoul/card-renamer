#!/usr/bin/env python3
"""Test different bottom-left region sizes for any image (generic version)"""

import sys
from pathlib import Path
from PIL import Image
import numpy as np
import re
from image_renamer import get_easyocr_reader

if len(sys.argv) < 2:
    print("Usage: python test_region_sizes.py <image_path>")
    print("Example: python test_region_sizes.py \"C:\\Users\\Brandon\\Pictures\\Proxies\\Mood Swings\\mtg\\FIN\\Airship Crash_ [FIN].png\"")
    sys.exit(1)

test_image = Path(sys.argv[1])
if not test_image.exists():
    print(f"File not found: {test_image}")
    sys.exit(1)

print(f"Testing: {test_image.name}")
print("Expected collector example: 0171\n")

img = Image.open(test_image)
width, height = img.size
print(f"Image size: {width}x{height}\n")

reader = get_easyocr_reader()

# Test different region sizes (width, height percentages)
sizes = [(0.20, 0.10), (0.35, 0.15), (0.45, 0.20), (0.60, 0.25), (0.80, 0.30)]

for w_size, h_size in sizes:
    print("=" * 80)
    print(f"Region size: {w_size*100:.0f}% width × {h_size*100:.0f}% height from bottom-left")
    print(f"Actual pixels: {int(width*w_size)}w x {int(height*h_size)}h")
    print("-" * 80)
    
    bottom_left_width = int(width * w_size)
    bottom_left_height = int(height * h_size)
    bottom_left_region = img.crop((0, height - bottom_left_height, bottom_left_width, height))
    
    results = reader.readtext(
        np.array(bottom_left_region),
        paragraph=False,
        contrast_ths=0.5,
        adjust_contrast=1.0,
        text_threshold=0.3,
        low_text=0.1
    )
    
    results.sort(key=lambda x: (x[0][0][1], x[0][0][0]))
    
    print("Detections:")
    for i, (bbox, text, conf) in enumerate(results, 1):
        y_pos = int(bbox[0][1])
        print(f"  {i}. '{text}' (conf: {conf:.3f}) at y≈{y_pos}")
        if re.search(r'\d{3,4}', text):
            print("     -> MATCHES collector pattern!")
    print()