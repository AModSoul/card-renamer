#!/usr/bin/env python3
"""Debug Baleful Strix to see all detections with confidence"""

from pathlib import Path
from PIL import Image
import numpy as np
from image_renamer import get_easyocr_reader

folder = Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed")
files = list(folder.glob("*Baleful*"))

if not files:
    print("Baleful Strix not found")
    import sys
    sys.exit(1)

test_image = files[0]
img = Image.open(test_image)
width, height = img.size

crop_width = int(width * 0.70)
crop_height = int(height * 0.4)
region = img.crop((0, 0, crop_width, crop_height))

print("=" * 60)
print(f"Testing: {test_image.name}")
print(f"Top-left region: {crop_width}x{crop_height}")
print("=" * 60)

reader = get_easyocr_reader()
results = reader.readtext(np.array(region), paragraph=False)

print(f"\nAll {len(results)} detections:")
print("-" * 60)
for i, (bbox, text, confidence) in enumerate(results, 1):
    y_pos = bbox[0][1]
    x_pos = bbox[0][0]
    print(f"{i}. '{text}' (conf: {confidence:.3f}, x: {x_pos:.0f}, y: {y_pos:.0f})")

print("\n\nFiltered by confidence > 0.6:")
print("-" * 60)
filtered = [r for r in results if r[2] > 0.6]
for bbox, text, confidence in filtered:
    print(f"'{text}' (conf: {confidence:.3f})")

print(f"\n{len(filtered)} detection(s) above 0.6 confidence")
print("=" * 60)
