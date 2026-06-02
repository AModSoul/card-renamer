#!/usr/bin/env python3
"""Debug NOSTALGIA.webp - show all OCR results"""

import sys
from pathlib import Path
from PIL import Image
import numpy as np
from image_renamer import get_easyocr_reader

# Test image path
test_image = Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed\NOSTALGIA.webp")

if not test_image.exists():
    print(f"Error: Test image not found: {test_image}")
    sys.exit(1)

print("=" * 60)
print("NOSTALGIA.webp - Full OCR Debug")
print("=" * 60)

img = Image.open(test_image)
width, height = img.size
print(f"\nImage size: {width}x{height}")

# Crop to top-left region (75% width, 40% height)
crop_width = int(width * 0.75)
crop_height = int(height * 0.40)
top_left_region = img.crop((0, 0, crop_width, crop_height))
print(f"Top-left region: {crop_width}x{crop_height}")

print("\nInitializing EasyOCR...")
reader = get_easyocr_reader()

# Run detection
results = reader.readtext(
    np.array(top_left_region),
    paragraph=False,
    contrast_ths=0.3,
    adjust_contrast=0.8,
    text_threshold=0.6,
    low_text=0.3
)

print(f"\nFound {len(results)} text detections:")
print("-" * 60)

if len(results) == 0:
    print("NO TEXT DETECTED!")
    print("\nTrying with lower thresholds...")
    results = reader.readtext(
        np.array(top_left_region),
        paragraph=False,
        contrast_ths=0.1,
        adjust_contrast=0.5,
        text_threshold=0.3,
        low_text=0.1
    )
    print(f"\nWith lower thresholds, found {len(results)} text detections:")
    print("-" * 60)

for i, (bbox, text, confidence) in enumerate(results, 1):
    print(f"{i}. Text: '{text}'")
    print(f"   Confidence: {confidence:.3f} ({confidence*100:.1f}%)")
    print(f"   Position: {bbox[0]}")
    print()

print("=" * 60)
