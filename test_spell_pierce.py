#!/usr/bin/env python3
"""Test Spell Pierce with corrected bottom-left height"""

import sys
from pathlib import Path
from image_renamer import extract_text, clean_text_for_filename

folder = Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed")
spell_files = list(folder.glob("*Spell*"))

if not spell_files:
    print("Spell Pierce file not found")
    sys.exit(1)

test_image = spell_files[0]

print("=" * 60)
print(f"Testing: {test_image.name}")
print("Bottom-left region: 18% width, 10% height (fixed)")
print("=" * 60)

card_name, collector_number, set_code = extract_text(test_image, check_bottom_left=True)

print(f"\nCard Name: '{card_name}'")
print(f"Collector Number: '{collector_number}'")
print(f"Set Code: '{set_code}'")

formatted = clean_text_for_filename(card_name, collector_number=collector_number, set_code=set_code)
print(f"\nFormatted: {formatted}.png")
print("=" * 60)
