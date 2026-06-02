#!/usr/bin/env python3
"""Debug Baleful Strix detection to find optimal width"""

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

for width_pct in [0.55, 0.60, 0.65, 0.70]:
    print("\n" + "=" * 60)
    print(f"Testing width: {width_pct*100}%")
    print("=" * 60)
    
    crop_width = int(width * width_pct)
    crop_height = int(height * 0.4)
    region = img.crop((0, 0, crop_width, crop_height))
    
    results = reader.readtext(np.array(region), paragraph=False)
    
    # Filter by confidence > 0.5
    filtered = [r for r in results if r[2] > 0.5]
    
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
    
    # Sort each line by X and join
    line_texts = []
    for line in lines:
        line.sort(key=lambda x: x[0][0][0])
        line_text = ' '.join([r[1] for r in line]).strip()
        line_texts.append(line_text)
    
    print(f"Detected {len(line_texts)} line(s):")
    for i, text in enumerate(line_texts, 1):
        print(f"  Line {i}: '{text}'")
    
    if len(line_texts) == 2:
        result = f"{line_texts[1]} ({line_texts[0]})"
    elif len(line_texts) > 0:
        result = ' '.join(line_texts)
    else:
        result = ""
    
    print(f"Final: '{result}'")
