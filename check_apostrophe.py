#!/usr/bin/env python3
"""Check what OCR detects for Abrade variant"""

from pathlib import Path
from PIL import Image
import numpy as np
from image_renamer import get_easyocr_reader

folder = Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed")
files = list(folder.glob("*Abrade*Youre*"))

if not files:
    print("Abrade variant not found")
    import sys
    sys.exit(1)

test_image = files[0]
img = Image.open(test_image)
width, height = img.size

crop_width = int(width * 0.90)
crop_height = int(height * 0.2)
region = img.crop((0, 0, crop_width, crop_height))

print(f"Testing: {test_image.name}\n")

reader = get_easyocr_reader()
results = reader.readtext(np.array(region), paragraph=False)

print("All detections:")
for bbox, text, confidence in results:
    if confidence > 0.6:
        print(f"  '{text}' (conf: {confidence:.3f})")
        print(f"    Characters: {[c for c in text]}")
        print(f"    Has apostrophe: {\"'\" in text}")
