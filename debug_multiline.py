#!/usr/bin/env python3
"""Debug Academy Ruins multi-line detection"""

import sys
from pathlib import Path
from PIL import Image
import numpy as np
from image_renamer import get_easyocr_reader

folder = Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed")
files = list(folder.glob("*Kitezh*"))

if not files:
    print("Kitezh file not found")
    sys.exit(1)

test_image = files[0]

print("=" * 60)
print(f"Testing: {test_image.name}")
print("Expected: 'Academy Ruins' (multi-line card name)")
print("=" * 60)

img = Image.open(test_image)
width, height = img.size

# Top-left region: 70% width, 40% height
crop_width = int(width * 0.70)
crop_height = int(height * 0.40)
top_left_region = img.crop((0, 0, crop_width, crop_height))

print(f"\nTop-left region: {crop_width}x{crop_height}\n")

reader = get_easyocr_reader()

results = reader.readtext(
    np.array(top_left_region),
    paragraph=False,
    contrast_ths=0.3,
    adjust_contrast=0.8,
    text_threshold=0.6,
    low_text=0.3
)

print(f"Found {len(results)} text detections:")
print("-" * 60)

for i, (bbox, text, confidence) in enumerate(results, 1):
    y_pos = bbox[0][1]
    x_pos = bbox[0][0]
    print(f"{i}. '{text}' (conf: {confidence:.2f})")
    print(f"   Position: x={x_pos}, y={y_pos}")

# Sort by position (top to bottom, left to right)
results.sort(key=lambda x: (x[0][0][1], x[0][0][0]))

print("\n\nSorted by Y-position (top to bottom):")
print("-" * 60)
for i, (bbox, text, confidence) in enumerate(results, 1):
    if confidence > 0.5:
        y_pos = bbox[0][1]
        print(f"{i}. '{text}' (y={y_pos}, conf: {confidence:.2f})")

text_parts = [r[1] for r in results if r[2] > 0.5]
print(f"\n\nJoined result: '{' '.join(text_parts)}'")
print("=" * 60)
