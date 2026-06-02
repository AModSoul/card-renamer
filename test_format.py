#!/usr/bin/env python3
"""Test collector info detection and filename formatting"""

import sys
from pathlib import Path
from image_renamer import extract_text, clean_text_for_filename

# Test image path
test_image = Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed\Altruism.webp")

if not test_image.exists():
    print(f"Error: Test image not found: {test_image}")
    sys.exit(1)

print("=" * 60)
print("Testing Collector Info Detection & Formatting")
print("=" * 60)
print(f"\nTest image: {test_image.name}\n")

# Test with collector info detection
print("Extracting card name and collector info...")
print("-" * 40)
print("Initializing EasyOCR (first time may download model ~90MB)...")
card_name, collector_number, set_code = extract_text(test_image, check_bottom_left=True)

print(f"\nCard Name: '{card_name}'")
print(f"Collector Number: '{collector_number}'")
print(f"Set Code: '{set_code}'\n")

# Test filename formatting
print("=" * 60)
print("Formatted Filename:")
print("-" * 40)
formatted_name = clean_text_for_filename(card_name, collector_number=collector_number, set_code=set_code)
print(f"{formatted_name}.webp")
print("=" * 60)
