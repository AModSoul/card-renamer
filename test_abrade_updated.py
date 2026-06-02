#!/usr/bin/env python3
"""Test updated collector info detection on Abrade"""

import sys
from pathlib import Path
from image_renamer import extract_text, clean_text_for_filename

folder = Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed")
abrade_files = list(folder.glob("*brade*"))

if not abrade_files:
    print("Abrade file not found")
    sys.exit(1)

test_image = abrade_files[0]

print("=" * 60)
print(f"Testing: {test_image.name}")
print("Expected: [SLD] {2390}")
print("=" * 60)

card_name, collector_number, set_code = extract_text(test_image, check_bottom_left=True)

print(f"\nCard Name: '{card_name}'")
print(f"Collector Number: '{collector_number}'")
print(f"Set Code: '{set_code}'")

formatted = clean_text_for_filename(card_name, collector_number=collector_number, set_code=set_code)
print(f"\nFormatted: {formatted}.png")
print("=" * 60)
