#!/usr/bin/env python3
"""Debug NOSTALGIA.webp detection"""

import sys
from pathlib import Path
from image_renamer import extract_text, clean_text_for_filename

# Test image path
test_image = Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed\NOSTALGIA.webp")

if not test_image.exists():
    print(f"Error: Test image not found: {test_image}")
    sys.exit(1)

print("=" * 60)
print("Testing NOSTALGIA.webp")
print("=" * 60)

# Test with collector info detection
print("\nInitializing EasyOCR...")
card_name, collector_number, set_code = extract_text(test_image, check_bottom_left=True)

print(f"\nCard Name: '{card_name}'")
print(f"Collector Number: '{collector_number}'")
print(f"Set Code: '{set_code}'")

# Test filename formatting
formatted_name = clean_text_for_filename(card_name, collector_number=collector_number, set_code=set_code)
print(f"\nFormatted Filename: {formatted_name}")
print("=" * 60)
