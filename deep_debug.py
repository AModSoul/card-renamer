#!/usr/bin/env python3
"""Deep debug - trace through extract_text step by step"""
import sys
from PIL import Image
import numpy as np
import easyocr
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python deep_debug.py <image_path>")
    sys.exit(1)

image_path = Path(sys.argv[1])
print(f"Analyzing: {image_path}\n")

# Load and crop image
img = Image.open(image_path)
width, height = img.size
crop_width = int(width * 0.90)
crop_height = int(height * 0.25)
top_left_region = img.crop((0, 0, crop_width, crop_height))

# Initialize OCR
print("Initializing EasyOCR...")
reader = easyocr.Reader(['en'], gpu=False, verbose=False)

# Run OCR
print("Running OCR...\n")
results = reader.readtext(
    np.array(top_left_region),
    paragraph=False,
    contrast_ths=0.3,
    adjust_contrast=0.8,
    text_threshold=0.6,
    low_text=0.3
)

print(f"Step 1: Raw OCR results = {len(results)} detections")
for i, (bbox, text, conf) in enumerate(results):
    print(f"  [{i}] '{text}' (conf={conf:.3f})")

# Step 2: Filter by confidence (normal - 0.6)
confidence_threshold = 0.6
filtered_results = [r for r in results if r[2] > confidence_threshold]
print(f"\nStep 2:  After > {confidence_threshold} filter = {len(filtered_results)} detections")
for i, (bbox, text, conf) in enumerate(filtered_results):
    print(f"  [{i}] '{text}' (conf={conf:.3f})")

# Step 3: Try low confidence
low_confidence_threshold = 0.4
if not filtered_results and low_confidence_threshold is not None:
    print(f"\nStep 3: Trying low confidence mode ({low_confidence_threshold})...")
    confidence_threshold = low_confidence_threshold
    filtered_results = [r for r in results if r[2] > confidence_threshold]
    print(f"  After > {confidence_threshold} filter = {len(filtered_results)} detections")
    for i, (bbox, text, conf) in enumerate(filtered_results):
        print(f"  [{i}] '{text}' (conf={conf:.3f})")
else:
    print(f"\nStep 3: Skipping low confidence (filtered_results={len(filtered_results)})")

# Step 4: Filter by length
print(f"\nStep 4: Before length filter = {len(filtered_results)} detections")
filtered_results = [r for r in filtered_results if len(r[1].strip()) >= 2 or r[1].strip() in ['X']]
print(f" After length filter = {len(filtered_results)} detections")
for i, (bbox, text, conf) in enumerate(filtered_results):
    print(f"  [{i}] '{text}' (len={len(text.strip())})")

# Step 5: Group by lines
print(f"\nStep 5: Grouping into lines...")
lines = []
if filtered_results:
    filtered_results.sort(key=lambda x: x[0][0][1])
    current_line = [filtered_results[0]]
    for detection in filtered_results[1:]:
        y_current = detection[0][0][1]
        y_last = current_line[-1][0][0][1]
        if abs(y_current - y_last) < 20:
            current_line.append(detection)
        else:
            lines.append(current_line)
            current_line = [detection]
    lines.append(current_line)
    
print(f"  Found {len(lines)} line(s)")
for i, line in enumerate(lines):
    print(f"  Line {i}: {len(line)} detection(s)")
    for bbox, text, conf in line:
        print(f"    - '{text}'")

# Step 6: Join lines
line_texts = []
for line in lines:
    line.sort(key=lambda x: x[0][0][0])  # Sort by X
    line_text = ' '.join([r[1] for r in line]).strip()
    line_texts.append(line_text)

print(f"\nStep 6: Final line texts:")
for i, text in enumerate(line_texts):
    print(f"  Line {i}: '{text}'")

# Step 7: Format card name
if len(line_texts) == 2:
    card_name = f"{line_texts[1]} ({line_texts[0]})"
elif len(line_texts) > 0:
    card_name = ' '.join(line_texts)
else:
    card_name = ""

print(f"\nStep 7: Final card name: '{card_name}'")