#!/usr/bin/env python3
"""Test 55% width on multiple cards"""

import sys
from pathlib import Path
from image_renamer import extract_text, clean_text_for_filename

folder = Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed")

# Test a few different cards
test_files = [
    "*Strix*",
    "*brade*",
    "*Time*",
    "*Zombify*",
    "*Stinging*"
]

print("=" * 60)
print("Testing 55% width on multiple cards")
print("=" * 60)

for pattern in test_files:
    files = list(folder.glob(pattern))
    if not files:
        continue
    
    test_image = files[0]
    print(f"\n{test_image.name}")
    print("-" * 40)
    
    card_name, collector_number, set_code = extract_text(
        test_image, 
        width_percentage=0.55, 
        height_percentage=0.4,
        check_bottom_left=True
    )
    
    print(f"Card Name: '{card_name}'")
    print(f"Collector: [{set_code}] {{{collector_number}}}")
    
    if card_name:
        formatted = clean_text_for_filename(card_name, collector_number=collector_number, set_code=set_code)
        print(f"Result: {formatted}.png")

print("\n" + "=" * 60)
