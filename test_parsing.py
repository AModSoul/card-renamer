#!/usr/bin/env python3
"""Test parsing logic for Abrade variant"""

import re

# Simulating what the code detects
bottom_text_parts = ['R 2179', 'SLD']

collector_number = None
set_code = None

print("Processing bottom-left detections:")
for text in bottom_text_parts:
    print(f"\nProcessing: '{text}'")
    
    # Look for collector number
    if re.search(r'\d{3,4}', text) and not collector_number:
        print(f"  -> Matches collector number pattern")
        match = re.search(r'[A-Z]?\s*(\d{3,4})', text)
        if match:
            collector_number = match.group(1)
            print(f"  -> Extracted: {collector_number}")
    
    # Look for set code
    elif not re.search(r'\d', text) and not set_code:
        print(f"  -> No digits, checking for set code")
        match = re.search(r'[A-Z]{2,3}', text)
        if match:
            set_code = match.group(0)
            print(f"  -> Extracted set code: {set_code}")
    else:
        if re.search(r'\d', text):
            print(f"  -> Has digits, skipping (collector_number={collector_number})")
        if set_code:
            print(f"  -> set_code already set: {set_code}")

print(f"\n\nFinal Results:")
print(f"Collector Number: {collector_number}")
print(f"Set Code: {set_code}")
