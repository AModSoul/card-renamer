#!/usr/bin/env python3
"""Debug Academy Ruins bottom-left detection"""

import sys
from pathlib import Path
from PIL import Image
import numpy as np
from image_renamer import get_easyocr_reader

folder = Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed")
files = list(folder.glob("*Academy*"))

if not files:
    print("Academy file not found")
    sys.exit(1)

test_image = files[0]

print("=" * 60)
print(f"Testing: {test_image.name}")
print("=" * 60)

img = Image.open(test_image)
width, height = img.size

# Bottom-left region: 18% width, 10% height from bottom
bottom_left_width = int(width * 0.18)
bottom_left_height = int(height * 0.10)
bottom_left_x = 0
bottom_left_y = height - bottom_left_height
bottom_left_region = img.crop((bottom_left_x, bottom_left_y, bottom_left_width, height))

print(f"\nBottom-left region: {bottom_left_width}x{bottom_left_height}")
print(f"Position: ({bottom_left_x}, {bottom_left_y}) to ({bottom_left_width}, {height})\n")

reader = get_easyocr_reader()

results = reader.readtext(
    np.array(bottom_left_region),
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

print("\n\nFiltered by confidence > 0.5:")
print("-" * 60)
import re
for bbox, text, confidence in results:
    if confidence > 0.5:
        print(f"'{text}' (conf: {confidence:.2f})")
        # Check if it's a collector number (3-4 digits)
        if re.search(r'\d{3,4}', text):
            print(f"  -> Matches collector number pattern")
        # Check if it's a set code (2-3 uppercase letters)
        if re.match(r'^[A-Z]{2,3}$', text.strip()):
            print(f"  -> Matches set code pattern")

print("=" * 60)
