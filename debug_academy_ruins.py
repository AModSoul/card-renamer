#!/usr/bin/env python3
"""Debug Academy Ruins detection"""

import sys
from pathlib import Path
from PIL import Image
import numpy as np
from image_renamer import get_easyocr_reader

folder = Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed")
test_image = folder / "sld-1506-academy-ruins (1).png"

if not test_image.exists():
    print(f"File not found: {test_image}")
    sys.exit(1)

print("=" * 60)
print(f"Testing: {test_image.name}")
print("Expected: Academy Ruins")
print("=" * 60)

img = Image.open(test_image)
width, height = img.size
print(f"Image size: {width}x{height}\n")

# Top-left region: 55% width, 40% height
crop_width = int(width * 0.55)
crop_height = int(height * 0.40)
top_left_region = img.crop((0, 0, crop_width, crop_height))

print(f"Top-left region: {crop_width}x{crop_height}\n")

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
    print(f"{i}. Text: '{text}'")
    print(f"   Confidence: {confidence:.3f} ({confidence*100:.1f}%)")
    print(f"   Y-position: {bbox[0][1]}")
    print()

# Sort by position
results.sort(key=lambda x: (x[0][0][1], x[0][0][0]))
print("\nSorted by position (top to bottom):")
print("-" * 60)
text_parts = [r[1] for r in results if r[2] > 0.5]
print(f"Detected (confidence > 0.5): {text_parts}")
print(f"Joined: '{' '.join(text_parts)}'")

print("\n" + "=" * 60)
