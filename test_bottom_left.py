#!/usr/bin/env python3
"""Test script for bottom-left text detection"""

from image_renamer import extract_text
from pathlib import Path

# Test image path
test_image = Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed\Altruism.webp")

if not test_image.exists():
    print(f"Error: Test image not found at {test_image}")
    exit(1)

print("="*60)
print("Testing Bottom-Left Text Detection")
print("="*60)
print(f"\nTest image: {test_image.name}\n")

# Test 1: Top-left only (original behavior)
print("Test 1: Top-left region only")
print("-" * 40)
text_top_only = extract_text(test_image, check_bottom_left=False)
print(f"Result: '{text_top_only}'")
print()

# Test 2: With bottom-left region
print("Test 2: Top-left + Bottom-left regions")
print("-" * 40)
text_both = extract_text(test_image, check_bottom_left=True)
print(f"Result:\n{text_both}")
print()

# Show the difference
print("="*60)
if text_top_only != text_both:
    print("✓ Bottom-left text detected!")
    print(f"\nAdditional text found:")
    additional = text_both.replace(text_top_only, '').strip()
    print(f"'{additional}'")
else:
    print("✗ No additional text found in bottom-left")
print("="*60)
