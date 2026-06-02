#!/usr/bin/env python3
"""Debug NOSTALGIA.webp - test different scan regions"""

import sys
from pathlib import Path
from image_renamer import extract_text

# Test image path
test_image = Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed\NOSTALGIA.webp")

if not test_image.exists():
    print(f"Error: Test image not found: {test_image}")
    sys.exit(1)

print("=" * 60)
print("Testing NOSTALGIA.webp - Different Scan Regions")
print("=" * 60)

print("\nInitializing EasyOCR...")

# Test 1: Default 75% width, 40% height
print("\nTest 1: 75% width, 40% height (default)")
print("-" * 40)
result = extract_text(test_image, width_percentage=0.75, height_percentage=0.4, check_bottom_left=False)
print(f"Card Name: '{result}'")

# Test 2: Larger area - 100% width, 50% height
print("\nTest 2: 100% width, 50% height (larger area)")
print("-" * 40)
result = extract_text(test_image, width_percentage=1.0, height_percentage=0.5, check_bottom_left=False)
print(f"Card Name: '{result}'")

# Test 3: Even larger - 100% width, 75% height
print("\nTest 3: 100% width, 75% height (even larger)")
print("-" * 40)
result = extract_text(test_image, width_percentage=1.0, height_percentage=0.75, check_bottom_left=False)
print(f"Card Name: '{result}'")

print("\n" + "=" * 60)
