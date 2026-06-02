#!/usr/bin/env python3
"""Debug Abrade.png bottom-left detection"""

import sys
from pathlib import Path
from PIL import Image
import numpy as np
from image_renamer import get_easyocr_reader

# Find Abrade file
folder = Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed")
abrade_files = list(folder.glob("*brade*"))

if not abrade_files:
    print("Abrade file not found")
    sys.exit(1)

test_image = abrade_files[0]
print(f"Testing: {test_image.name}")
print("=" * 60)

img = Image.open(test_image)
width, height = img.size
print(f"Image size: {width}x{height}\n")

# Bottom-left region: 14% from left and bottom edges
bottom_left_width = int(width * 0.14)
bottom_left_height = int(height * 0.14)
bottom_left_x = 0
bottom_left_y = height - bottom_left_height
bottom_left_region = img.crop((bottom_left_x, bottom_left_y, bottom_left_width, height))

print(f"Bottom-left region: {bottom_left_width}x{bottom_left_height}")
print(f"Position: ({bottom_left_x}, {bottom_left_y}) to ({bottom_left_width}, {height})\n")

print("Initializing EasyOCR...")
reader = get_easyocr_reader()

# Run detection
results = reader.readtext(
    np.array(bottom_left_region),
    paragraph=False,
    contrast_ths=0.3,
    adjust_contrast=0.8,
    text_threshold=0.6,
    low_text=0.3
)

print(f"\nFound {len(results)} text detections:")
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
for i, (bbox, text, confidence) in enumerate(results, 1):
    print(f"{i}. '{text}' (confidence: {confidence:.3f})")

print("\n" + "=" * 60)
print("Expected: [SLD] {2390}")
print("=" * 60)
