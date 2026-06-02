#!/usr/bin/env python3
"""Debug Invisible Woman bottom-left detection"""

import sys
from pathlib import Path
from PIL import Image
import numpy as np
from image_renamer import get_easyocr_reader
import re

folder = Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed")
files = list(folder.glob("*Invisible*"))

if not files:
    print("Invisible Woman file not found")
    sys.exit(1)

test_image = files[0]

print("=" * 60)
print(f"Testing: {test_image.name}")
print("=" * 60)

img = Image.open(test_image)
width, height = img.size

# Bottom-left region: 20% width, 10% height from bottom
bottom_left_width = int(width * 0.20)
bottom_left_height = int(height * 0.10)
bottom_left_x = 0
bottom_left_y = height - bottom_left_height
bottom_left_region = img.crop((bottom_left_x, bottom_left_y, bottom_left_width, height))

print(f"\nBottom-left region: {bottom_left_width}x{bottom_left_height}\n")

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
    print(f"{i}. '{text}' (conf: {confidence:.2f})")

print("\n\nFiltered by confidence > 0.5:")
print("-" * 60)
bottom_text_parts = [r[1] for r in results if r[2] > 0.5]

collector_number = None
set_code = None

for text in bottom_text_parts:
    print(f"Processing: '{text}'")
    # Look for collector number (has 3-4 consecutive digits, possibly with leading letter)
    if re.search(r'\d{3,4}', text) and not collector_number:
        print(f"  -> Has digits")
        # Extract the number part
        match = re.search(r'[A-Z]?\s*(\d{3,4})', text)
        if match:
            collector_number = match.group(1)
            print(f"  -> Extracted collector number: '{collector_number}'")
    # Look for set code (2-3 uppercase letters, may have dots/spaces)
    # Must not contain digits (to avoid matching collector numbers like "R 1506")
    elif not re.search(r'\d', text) and not set_code:
        print(f"  -> No digits, looking for set code")
        # Extract first occurrence of 2-3 consecutive uppercase letters
        match = re.search(r'[A-Z]{2,3}', text)
        if match:
            set_code = match.group(0)
            print(f"  -> Extracted set code: '{set_code}'")

print(f"\n\nFinal Results:")
print(f"Collector Number: {collector_number}")
print(f"Set Code: {set_code}")
print("=" * 60)
