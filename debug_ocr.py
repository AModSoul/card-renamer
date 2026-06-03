#!/usr/bin/env python3
"""Debug OCR results for a specific image"""
from PIL import Image
import numpy as np
import re
from image_renamer import get_easyocr_reader
import sys
from pathlib import Path

# Add current directory to path to import image_renamer functions
sys.path.insert(0, str(Path(__file__).parent))
from image_renamer import extract_text, clean_text_for_filename

if len(sys.argv) < 2:
    print("Usage: python debug_ocr.py <image_path>")
    sys.exit(1)

image_path = Path(sys.argv[1])

print(f"Analyzing: {image_path}\n")

# Test extract_text with different confidence thresholds
print("=" * 80)
print("Testing with normal confidence (0.6):")
print("=" * 80)
result = extract_text(image_path, check_bottom_left=True, low_confidence_threshold=None)
card_name, collector_number, set_code = result
print(f"Card Name: '{card_name}'")
print(f"Collector Number: {collector_number}")
print(f"Set Code: {set_code}")

if card_name:
    cleaned = clean_text_for_filename(card_name, collector_number=collector_number, set_code=set_code)
    print(f"Cleaned filename: '{cleaned}'")
else:
    print("No card name detected!")

print("\n" + "=" * 80)
print("Testing with low confidence (0.4):")
print("=" * 80)
result = extract_text(image_path, check_bottom_left=True, low_confidence_threshold=0.4)
card_name, collector_number, set_code = result
print(f"Card Name: '{card_name}'")
print(f"Collector Number: {collector_number}")
print(f"Set Code: {set_code}")

if card_name:
    cleaned = clean_text_for_filename(card_name, collector_number=collector_number, set_code=set_code)
    print(f"Cleaned filename: '{cleaned}'")
else:
    print("No card name detected!")

print("\n" + "=" * 80)
print("Testing with very low confidence (0.3")
print("=" * 80)
result = extract_text(image_path, check_bottom_left=True, low_confidence_threshold=0.3)
card_name, collector_number, set_code = result
print(f"Card Name: '{card_name}'")
print(f"Collector Number: {collector_number}")
print(f"Set Code: {set_code}")



if card_name:
    cleaned = clean_text_for_filename(card_name, collector_number=collector_number, set_code=set_code)
    print(f"Cleaned filename: '{cleaned}'")
else:
    print("No card name detected!")

print("\n" + "=" * 80)
print("RAW Bottom OCR Diagnostics (for collector debugging):")
print("=" * 80)
img = Image.open(image_path)
width, height = img.size
bottom_left_width = int(width * 0.35)
bottom_left_height = int(height * 0.15)
bottom_left_region = img.crop((0, height - bottom_left_height, bottom_left_width, height))

reader = get_easyocr_reader()
results = reader.readtext(
    np.array(bottom_left_region),
    paragraph=False,
    contrast_ths=0.5,
    adjust_contrast=1.0,
    text_threshold=0.3,
    low_text=0.1
)
print(f"Found {len(results)} bottom detections:")
for i, (bbox, text, conf) in enumerate(results, 1):
    print(f"  {i}. '{text}' (conf={conf:.3f}) at position y≈{int(bbox[0][1])}")
    if re.search(r'\d{3,4}', text):
        print("     -> MATCHES collector pattern!")
