#!/usr/bin/env python3
"""Test different height percentages for Baleful Strix"""

from pathlib import Path
from PIL import Image
import numpy as np
from image_renamer import get_easyocr_reader

folder = Path(r"C:\Users\Brandon\Pictures\Proxies\Mood Swings\Need renamed")
files = list(folder.glob("*Baleful*"))

if not files:
    print("Baleful Strix not found")
    import sys
    sys.exit(1)

test_image = files[0]
img = Image.open(test_image)
width, height = img.size

reader = get_easyocr_reader()

for height_pct in [0.25, 0.30, 0.35, 0.40]:
    print("\n" + "=" * 60)
    print(f"Testing height: {height_pct*100}% (width: 70%)")
    print("=" * 60)
    
    crop_width = int(width * 0.70)
    crop_height = int(height * height_pct)
    region = img.crop((0, 0, crop_width, crop_height))
    
    print(f"Region: {crop_width}x{crop_height} pixels")
    
    results = reader.readtext(np.array(region), paragraph=False)
    
    print(f"\nAll detections:")
    for bbox, text, confidence in results:
        y_pos = bbox[0][1]
        print(f"  '{text}' (conf: {confidence:.3f}, y: {y_pos:.0f})")
    
    # Filter by confidence > 0.6
    filtered = [r for r in results if r[2] > 0.6]
    
    print(f"\nFiltered (conf > 0.6):")
    for bbox, text, confidence in filtered:
        print(f"  '{text}'")
    
    # Group by Y-position
    lines = []
    if filtered:
        filtered.sort(key=lambda x: x[0][0][1])
        current_line = [filtered[0]]
        for detection in filtered[1:]:
            y_current = detection[0][0][1]
            y_last = current_line[-1][0][0][1]
            if abs(y_current - y_last) < 20:
                current_line.append(detection)
            else:
                lines.append(current_line)
                current_line = [detection]
        lines.append(current_line)
    
    line_texts = []
    for line in lines:
        line.sort(key=lambda x: x[0][0][0])
        line_text = ' '.join([r[1] for r in line]).strip()
        line_texts.append(line_text)
    
    if len(line_texts) == 2:
        result = f"{line_texts[1]} ({line_texts[0]})"
    elif len(line_texts) > 0:
        result = ' '.join(line_texts)
    else:
        result = ""
    
    print(f"\n=> Final: '{result}'")
