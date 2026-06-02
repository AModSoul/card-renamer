#!/usr/bin/env python3
"""Debug Abrade variant detection"""

from pathlib import Path
from PIL import Image
import numpy as np
from image_renamer import get_easyocr_reader

folder = Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed")
files = list(folder.glob("*Abrade (Youre*"))

if not files:
    print("Abrade variant not found")
    import sys
    sys.exit(1)

test_image = files[0]
img = Image.open(test_image)
width, height = img.size

print("=" * 60)
print(f"Testing: {test_image.name}")
print("=" * 60)

reader = get_easyocr_reader()

# Top-left region
crop_width = int(width * 0.70)
crop_height = int(height * 0.2)
top_region = img.crop((0, 0, crop_width, crop_height))

print(f"\nTop-left region: {crop_width}x{crop_height}")
results = reader.readtext(np.array(top_region), paragraph=False)

print("\nTop-left detections:")
for bbox, text, confidence in results:
    y_pos = bbox[0][1]
    print(f"  '{text}' (conf: {confidence:.3f}, y: {y_pos:.0f})")

# Bottom-left region
bottom_left_width = int(width * 0.20)
bottom_left_height = int(height * 0.10)
bottom_region = img.crop((0, height - bottom_left_height, bottom_left_width, height))

print(f"\nBottom-left region: {bottom_left_width}x{bottom_left_height}")
bottom_results = reader.readtext(np.array(bottom_region), paragraph=False)

print("\nBottom-left detections:")
for bbox, text, confidence in bottom_results:
    print(f"  '{text}' (conf: {confidence:.3f})")

print("=" * 60)
