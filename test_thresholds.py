#!/usr/bin/env python3
"""Test custom confidence thresholds"""

import sys
from pathlib import Path
from image_renamer import extract_text, clean_text_for_filename

test_image = Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed\Nostalgia [MSW] {0128}.webp")

if not test_image.exists():
    print(f"Error: Test image not found: {test_image}")
    sys.exit(1)

print("=" * 60)
print("Testing Custom Confidence Thresholds")
print("=" * 60)

thresholds = [None, 0.4, 0.3, 0.2]

for threshold in thresholds:
    print(f"\n{'No fallback' if threshold is None else f'Threshold: {threshold}'}")
    print("-" * 40)
    
    card_name, collector_number, set_code = extract_text(
        test_image, 
        check_bottom_left=True, 
        low_confidence_threshold=threshold
    )
    
    print(f"Card Name: '{card_name}'")
    if card_name:
        formatted = clean_text_for_filename(card_name, collector_number=collector_number, set_code=set_code)
        print(f"Formatted: {formatted}.webp")

print("\n" + "=" * 60)
