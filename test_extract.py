#!/usr/bin/env python3
"""Direct test of extract_text on Abrade variant"""

from pathlib import Path
from image_renamer import extract_text

test_image = Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed\Abrade (Youre Gonna Need A Bigger) {2179}.png")

print(f"Testing: {test_image.name}\n")

result = extract_text(test_image, check_bottom_left=True)

print(f"Return type: {type(result)}")
if isinstance(result, tuple):
    card_name, collector_number, set_code = result
    print(f"Card Name: '{card_name}'")
    print(f"Collector Number: '{collector_number}'")
    print(f"Set Code: {repr(set_code)}")
    print(f"Set Code is None: {set_code is None}")
    print(f"Set Code type: {type(set_code)}")
else:
    print(f"Result: '{result}'")
