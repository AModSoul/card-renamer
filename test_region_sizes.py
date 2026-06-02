#!/usr/bin/env python3
"""Test different bottom-left region sizes"""

import sys
from pathlib import Path
from PIL import Image
import numpy as np
from image_renamer import get_easyocr_reader

folder = Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed")
abrade_files = list(folder.glob("*brade*"))

if not abrade_files:
    print("Abrade file not found")
    sys.exit(1)

test_image = abrade_files[0]
print(f"Testing: {test_image.name}")
print("Expected: [SLD] {2390}\n")

img = Image.open(test_image)
width, height = img.size

reader = get_easyocr_reader()

# Test different region sizes
sizes = [0.14, 0.18, 0.22, 0.25]

for size in sizes:
    print("=" * 60)
    print(f"Region size: {size*100}% from left and bottom")
    print("-" * 60)
    
    bottom_left_width = int(width * size)
    bottom_left_height = int(height * size)
    bottom_left_region = img.crop((0, height - bottom_left_height, bottom_left_width, height))
    
    results = reader.readtext(
        np.array(bottom_left_region),
        paragraph=False,
        contrast_ths=0.3,
        adjust_contrast=0.8,
        text_threshold=0.6,
        low_text=0.3
    )
    
    # Sort by position
    results.sort(key=lambda x: (x[0][0][1], x[0][0][0]))
    
    print(f"Detections:")
    for i, (bbox, text, conf) in enumerate(results, 1):
        print(f"  {i}. '{text}' (conf: {conf:.2f})")
    print()
