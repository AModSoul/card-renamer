#!/usr/bin/env python3
"""Test two-pass confidence detection"""

import sys
from pathlib import Path
from image_renamer import extract_text, clean_text_for_filename

# Test images
test_images = [
    Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed\Altruism.webp"),
    Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed\NOSTALGIA.webp")
]

print("=" * 60)
print("Testing Two-Pass Confidence Detection")
print("=" * 60)
print("\nFirst pass: confidence > 0.5 (strict)")
print("Second pass: confidence > 0.4 (if first pass fails)")
print()

for test_image in test_images:
    if not test_image.exists():
        print(f"Skipping: {test_image.name} (not found)")
        continue
    
    print("=" * 60)
    print(f"Testing: {test_image.name}")
    print("-" * 60)
    
    # Extract with collector info
    card_name, collector_number, set_code = extract_text(test_image, check_bottom_left=True)
    
    print(f"Card Name: '{card_name}'")
    print(f"Collector Number: '{collector_number}'")
    print(f"Set Code: '{set_code}'")
    
    # Format filename
    formatted_name = clean_text_for_filename(card_name, collector_number=collector_number, set_code=set_code)
    print(f"\nFormatted: {formatted_name}.webp")

print("\n" + "=" * 60)
print("✓ Two-pass detection test complete")
print("=" * 60)
