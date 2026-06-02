#!/usr/bin/env python3
"""Test different top-left width percentages on Baleful Strix"""

import sys
from pathlib import Path
from image_renamer import extract_text, clean_text_for_filename

folder = Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed")
strix_files = list(folder.glob("*Strix*"))

if not strix_files:
    print("Baleful Strix file not found")
    sys.exit(1)

test_image = strix_files[0]

print("=" * 60)
print(f"Testing: {test_image.name}")
print("Expected card name: 'Baleful Strix' (no '2')")
print("=" * 60)

# Test different width percentages
widths = [0.75, 0.65, 0.55, 0.45, 0.35]

for width in widths:
    print(f"\nWidth: {width*100}% (height: 40%)")
    print("-" * 40)
    
    card_name, collector_number, set_code = extract_text(
        test_image, 
        width_percentage=width, 
        height_percentage=0.4,
        check_bottom_left=True
    )
    
    print(f"Card Name: '{card_name}'")
    
    if card_name:
        formatted = clean_text_for_filename(card_name, collector_number=collector_number, set_code=set_code)
        print(f"Full filename: {formatted}.png")

print("\n" + "=" * 60)
