#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Renamer Tool
Renames image files based on text detected in the top-left corner of the image.
"""

import os
import re
import sys
import argparse
from pathlib import Path
from PIL import Image
import numpy as np

# Lazy load EasyOCR (only when needed)
_easyocr_reader = None

def get_easyocr_reader():
    """Lazy load EasyOCR reader (downloads model on first use)"""
    global _easyocr_reader
    if _easyocr_reader is None:
        import easyocr
        print("Initializing EasyOCR (first time may download model ~90MB)...")
        _easyocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    return _easyocr_reader

# Force UTF-8 encoding for console output
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def clean_collector_number(text):
    """
    Clean collector number by removing leading letters and spaces.
    Examples:
        'R 238' -> '238'
        'M 248' -> '248'
        'R 20E' -> '20E'
        'mc' -> 'mc' (keep if all letters)
        '0001' -> '0001'
    """
    if not text:
        return None
    
    # Remove leading letters and spaces (e.g., "R 238" -> "238")
    cleaned = re.sub(r'^[A-Za-z]+\s*', '', text)
    
    # If nothing left after removing leading letters, return original
    # (handles cases like "mc", "We", "nec" which are all letters)
    if not cleaned:
        return text
    
    return cleaned


def extract_text(image_path, width_percentage=0.90, height_percentage=0.2, check_bottom_left=False, low_confidence_threshold=None):
    """Extract text using EasyOCR
    
    Args:
        image_path: Path to the image file
        width_percentage: Percentage of image width to scan for card name (default: 0.90)
        height_percentage: Percentage of image height to scan for card name (default: 0.2)
        check_bottom_left: If True, also detect collector info from bottom-left corner
        low_confidence_threshold: If set, use this confidence threshold as fallback (e.g., 0.4, 0.3, 0.2)
    
    Returns:
        If check_bottom_left is False: string with card name
        If check_bottom_left is True: tuple of (card_name, collector_number, set_code)
    """
    try:
        img = Image.open(image_path)
        width, height = img.size
        
        # Crop to top-left region (Card Name detection)
        crop_width = int(width * width_percentage)
        crop_height = int(height * height_percentage)
        top_left_region = img.crop((0, 0, crop_width, crop_height))
        
        # Get EasyOCR reader
        reader = get_easyocr_reader()
        
        # Run detection on top-left
        results = reader.readtext(
            np.array(top_left_region),
            paragraph=False,
            contrast_ths=0.3,
            adjust_contrast=0.8,
            text_threshold=0.6,
            low_text=0.3
        )
        
        # Filter by confidence (strict first)
        confidence_threshold = 0.6
        filtered_results = [r for r in results if r[2] > confidence_threshold]
        
        # Second pass: if nothing detected and low confidence threshold set, try lower threshold
        if not filtered_results and low_confidence_threshold is not None:
            confidence_threshold = low_confidence_threshold
            filtered_results = [r for r in results if r[2] > confidence_threshold]
        
        # Filter out single-character or very short detections (likely symbols/card text, not card names)
        # Keep only detections with 2+ characters or common single letters in card names (like "X")
        filtered_results = [r for r in filtered_results if len(r[1].strip()) >= 2 or r[1].strip() in ['X']]
        
        # Group detections by Y-position (multi-line card names)
        # Group texts that are within 20 pixels vertically
        lines = []
        if filtered_results:
            # Sort by Y position first
            filtered_results.sort(key=lambda x: x[0][0][1])
            
            current_line = [filtered_results[0]]
            for detection in filtered_results[1:]:
                y_current = detection[0][0][1]
                y_last = current_line[-1][0][0][1]
                
                # If within 20 pixels vertically, same line
                if abs(y_current - y_last) < 20:
                    current_line.append(detection)
                else:
                    # New line - save current and start new
                    lines.append(current_line)
                    current_line = [detection]
            
            # Add the last line
            lines.append(current_line)
        
        # Sort each line by X-position (left to right) and join
        line_texts = []
        for line in lines:
            line.sort(key=lambda x: x[0][0][0])  # Sort by X
            line_text = ' '.join([r[1] for r in line]).strip()
            line_texts.append(line_text)
        
        # Format card name based on number of lines
        if len(line_texts) == 2:
            # Two-line card: bottom line (main name) + top line (nickname in parentheses)
            card_name = f"{line_texts[1]} ({line_texts[0]})"
        elif len(line_texts) > 0:
            # Single line or multiple lines: join all
            card_name = ' '.join(line_texts)
        else:
            card_name = ""
        
        # Optionally check bottom-left corner (Collector Info detection)
        if check_bottom_left:
            # Bottom left region: 20% from left, 10% from bottom edges
            bottom_left_width = int(width * 0.20)
            bottom_left_height = int(height * 0.10)
            bottom_left_x = 0
            bottom_left_y = height - bottom_left_height
            bottom_left_region = img.crop((bottom_left_x, bottom_left_y, bottom_left_width, height))
            
            # Run detection on bottom-left
            bottom_results = reader.readtext(
                np.array(bottom_left_region),
                paragraph=False,
                contrast_ths=0.3,
                adjust_contrast=0.8,
                text_threshold=0.6,
                low_text=0.3
            )
            
             # Sort by position (top to bottom)
            bottom_results.sort(key=lambda x: (x[0][0][1], x[0][0][0]))
            
            # Extract text with confidence > 0.5 (strict) for collector numbers
            bottom_text_parts = [r[1] for r in bottom_results if r[2] > 0.5]
            
            # Second pass: if nothing detected and low confidence threshold set, try lower threshold
            if not bottom_text_parts and low_confidence_threshold is not None:
                bottom_text_parts = [r[1] for r in bottom_results if r[2] > low_confidence_threshold]
            
            # Parse collector info from multiple detections
            # Look for: collector number (contains digits, e.g., "R 2390", "M 248", "2070")
            #           set code (2-3 letters, e.g., "SLD", "SLD . EN", "EN")
            collector_number = None
            set_code = None
            
            # Process high confidence detections first
            for text in bottom_text_parts:
                # Look for collector number (has 3-4 consecutive digits, possibly with leading letter)
                if re.search(r'\d{3,4}', text) and not collector_number:
                    # Extract the number part
                    match = re.search(r'[A-Z]?\s*(\d{3,4})', text)
                    if match:
                        collector_number = match.group(1)
                # Look for set code (2-3 uppercase letters, may have dots/spaces)
                # Must not contain digits (to avoid matching collector numbers like "R 1506")
                elif not re.search(r'\d', text) and not set_code:
                    # Extract first occurrence of 2-3 consecutive uppercase letters
                    match = re.search(r'[A-Z]{2,3}', text)
                    if match:
                        set_code = match.group(0)
            
            # If no set code found in high confidence detections, try ALL detections with lower threshold
            if not set_code:
                for bbox, text, conf in bottom_results:
                    if conf > 0.15 and not re.search(r'\d', text):  # Lower threshold for set codes
                        match = re.search(r'[A-Z]{2,3}', text)
                        if match:
                            set_code = match.group(0)
                            break
            
            return (card_name, collector_number, set_code)
        
        return card_name
        
    except Exception as e:
        print(f"OCR error: {e}")
        if check_bottom_left:
            return ("", None, None)
        return ""

def fix_contractions(text):
    """
    Fix common contractions that OCR often detects without apostrophes.
    
    Args:
        text: Text with missing apostrophes in contractions
    
    Returns:
        Text with common contractions fixed
    """
    # Dictionary of common contractions (case-insensitive patterns)
    contractions = {
        r'\bYoure\b': "You're",
        r'\bDont\b': "Don't",
        r'\bCant\b': "Can't",
        r'\bWont\b': "Won't",
        r'\bIsnt\b': "Isn't",
        r'\bWasnt\b': "Wasn't",
        r'\bWerent\b': "Weren't",
        r'\bArent\b': "Aren't",
        r'\bDidnt\b': "Didn't",
        r'\bDoesnt\b': "Doesn't",
        r'\bHasnt\b': "Hasn't",
        r'\bHavent\b': "Haven't",
        r'\bWouldnt\b': "Wouldn't",
        r'\bShouldnt\b': "Shouldn't",
        r'\bCouldnt\b': "Couldn't",
        r'\bIm\b': "I'm",
        r'\bIve\b': "I've",
        r'\bId\b': "I'd",
        r'\bIll\b': "I'll",
        r'\bHes\b': "He's",
        r'\bShes\b': "She's",
        r'\bIts\b': "It's",
        r'\bThats\b': "That's",
        r'\bWhats\b': "What's",
        r'\bWhos\b': "Who's",
        r'\bTheres\b': "There's",
        r'\bHeres\b': "Here's",
        r'\bLets\b': "Let's",
        r'\bWheres\b': "Where's",
        r'\bWeve\b': "We've",
        r'\bTheyre\b': "They're",
        r'\bTheyve\b': "They've",
        r'\bWell\b': "We'll",
        r'\bTheyll\b': "They'll",
    }
    
    # Apply each contraction fix
    for pattern, replacement in contractions.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def clean_text_for_filename(text, max_length=100, collector_number=None, set_code=None):
    """
    Clean extracted text to create a valid filename.
    
    Args:
        text: Raw card name text from OCR
        max_length: Maximum length for the filename
        collector_number: Optional collector number to include in {}
        set_code: Optional set code to include in []
    
    Returns:
        Cleaned text suitable for a filename in format: "Card Name {number} [code]"
    """
    if not text:
        return None
    
    # Take the first non-empty line for card name
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return None
    
    filename = lines[0]
    
    # Fix common contractions that OCR often misses apostrophes on
    filename = fix_contractions(filename)
    
    # Clean up common OCR errors for better readability
    # Remove leading/trailing special characters that are likely OCR errors
    # (but preserve parentheses and commas which may be part of card names)
    filename = re.sub(r'^[^\w\s(,]+', '', filename)  # Remove leading special chars (except parentheses/commas)
    filename = re.sub(r'[^\w\s),]+$', '', filename)  # Remove trailing special chars (except parentheses/commas)
    
    # Replace common OCR mistakes in the middle (but preserve hyphens and spaces)
    # Keep only alphanumeric, spaces, hyphens, apostrophes, parentheses, and commas
    filename = re.sub(r'[^\w\s\-\'(),]', ' ', filename)
    
    # Remove or replace invalid filename characters for Windows
    # Windows invalid chars: < > : " / \ | ? *
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Replace multiple spaces with single space
    filename = re.sub(r'\s+', ' ', filename)
    
    # Trim to max length
    filename = filename[:max_length].strip()
    
    # Remove trailing dots and spaces (Windows doesn't allow)
    filename = filename.rstrip('. ')
    
    # Apply title case for consistent formatting
    # Handle words that may start with special characters (e.g., parentheses)
    def title_word(word):
        # Find first letter and capitalize it
        for i, char in enumerate(word):
            if char.isalpha():
                return word[:i] + word[i].upper() + word[i+1:].lower()
        return word  # No letters found, return as-is
    
    words = filename.split()
    filename = ' '.join(title_word(word) for word in words)
    
    # If it's too short or empty after cleaning, reject it
    if len(filename) < 2:
        return None
    
    # Add collector info if provided
    # Format: "Card Name [set_code] {collector_number}"
    if set_code:
        filename = f"{filename} [{set_code}]"
    if collector_number:
        filename = f"{filename} {{{collector_number}}}"
    
    return filename if filename else None


def rename_image(image_path, dry_run=False, width_percentage=0.90, height_percentage=0.2, verbose=False, low_confidence_threshold=None, skip_renamed=True):
    """
    Rename an image file based on text in the top-left corner.
    
    Args:
        image_path: Path to the image file
        dry_run: If True, don't actually rename, just show what would happen
        width_percentage: Percentage of image width to scan for text
        height_percentage: Percentage of image height to scan for text
        verbose: If True, show detailed output
        low_confidence_threshold: If set, use this confidence threshold as fallback (e.g., 0.4)
        skip_renamed: If True, skip files that already have collector info in filename
    
    Returns:
        True if renamed successfully, False otherwise
    """
    image_path = Path(image_path)
    
    if not image_path.exists():
        print(f"File not found: {image_path}")
        return False
    
    # Check if file is already renamed (has collector info pattern like [CODE] {NUMBER})
    if skip_renamed and low_confidence_threshold is not None:
        filename_no_ext = image_path.stem
        # Check for pattern: [XXX] {NNNN}
        if re.search(r'\[\w+\]\s*\{\d+\}', filename_no_ext):
            if verbose:
                print(f"  [SKIP] Already renamed: {image_path.name}", flush=True)
            else:
                print(f"  [SKIP] {image_path.name}", flush=True)
            return False
    
    # Extract text from top-left
    if verbose:
        print(f"Processing: {image_path.name}")
    
    # Extract text using EasyOCR with collector info detection
    result = extract_text(image_path, width_percentage, height_percentage, check_bottom_left=True, low_confidence_threshold=low_confidence_threshold)
    
    # Handle tuple return (card_name, collector_number, set_code)
    if isinstance(result, tuple):
        card_name, collector_number, set_code = result
        if verbose and card_name:
            print(f"  Card Name: {card_name}")
            if collector_number:
                print(f"  Collector Number: {collector_number}")
            if set_code:
                print(f"  Set Code: {set_code}")
        # Clean text for filename with collector info
        new_name = clean_text_for_filename(card_name, collector_number=collector_number, set_code=set_code)
    else:
        # Backwards compatibility if check_bottom_left was False
        if verbose and result:
            print(f"  Detected text: {result[:100]}...")
        new_name = clean_text_for_filename(result)
    
    if not new_name:
        print(f"  [!] No text detected in {image_path.name}", flush=True)
        return False
    
    # Create new filename with original extension
    new_filename = new_name + image_path.suffix
    new_path = image_path.parent / new_filename
    
    # Check if target already exists
    if new_path.exists() and new_path != image_path:
        print(f"  [!] Target already exists: {new_filename}")
        
        # Add number suffix in parentheses
        counter = 1
        while new_path.exists():
            new_filename = f"{new_name} ({counter}){image_path.suffix}"
            new_path = image_path.parent / new_filename
            counter += 1
        
        print(f"  Using: {new_filename}")
    
    # Check if names are identical (case-sensitive comparison)
    # On Windows, we can still rename to fix casing even though paths are equal
    if image_path.name == new_path.name:
        print(f"  [i] Already named correctly: {image_path.name}", flush=True)
        return False
    
    # Rename the file (this will work even on Windows to change case)
    if dry_run:
        print(f"  [DRY RUN] Would rename to: {new_filename}")
    else:
        try:
            # On Windows, renaming to same path with different case requires temp rename
            if image_path.resolve() == new_path.resolve():
                temp_path = image_path.parent / f"_temp_{new_filename}"
                image_path.rename(temp_path)
                temp_path.rename(new_path)
            else:
                image_path.rename(new_path)
            print(f"  [OK] Renamed to: {new_filename}", flush=True)
            return True
        except Exception as e:
            print(f"  [ERROR] Error renaming: {e}", flush=True)
            return False
    
    return True


def process_directory(directory, dry_run=False, width_percentage=0.90, height_percentage=0.2, 
                     recursive=False, verbose=False, extensions=None, low_confidence_threshold=None, skip_renamed=True):
    """
    Process all images in a directory.
    
    Args:
        directory: Path to directory containing images
        dry_run: If True, don't actually rename files
        width_percentage: Percentage of image width to scan for text
        height_percentage: Percentage of image height to scan for text
        recursive: If True, process subdirectories
        verbose: If True, show detailed output
        extensions: List of file extensions to process (e.g., ['.jpg', '.png'])
        low_confidence_threshold: If set, use this confidence threshold as fallback (e.g., 0.4)
        skip_renamed: If True, skip files that already have collector info in filename
    
    Returns:
        Number of files successfully renamed
    """
    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp']
    
    extensions = [ext.lower() for ext in extensions]
    directory = Path(directory)
    
    if not directory.exists():
        print(f"Directory not found: {directory}")
        return 0
    
    # Find image files
    if recursive:
        image_files = [f for f in directory.rglob('*') 
                      if f.is_file() and f.suffix.lower() in extensions]
    else:
        image_files = [f for f in directory.glob('*') 
                      if f.is_file() and f.suffix.lower() in extensions]
    
    if not image_files:
        print(f"No image files found in {directory}")
        return 0
    
    print(f"Found {len(image_files)} image(s) to process\n")
    
    renamed_count = 0
    for idx, image_file in enumerate(image_files, 1):
        # Print progress to keep terminal responsive
        print(f"[{idx}/{len(image_files)}] ", end='', flush=True)
        if rename_image(image_file, dry_run, width_percentage, height_percentage, verbose, low_confidence_threshold, skip_renamed):
            renamed_count += 1
        sys.stdout.flush()  # Force output to appear immediately
    
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Renamed {renamed_count} of {len(image_files)} files")
    return renamed_count


def main():
    parser = argparse.ArgumentParser(
        description="Rename image files based on text detected in the top-left corner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single image
  python image_renamer.py image.jpg
  
  # Process all images in a directory (dry run)
  python image_renamer.py --directory ./images --dry-run
  
  # Process directory recursively
  python image_renamer.py -d ./images --recursive
  
  # Adjust the region size
  python image_renamer.py -d ./images --width 0.8 --height 0.5
        """
    )
    
    parser.add_argument('image', nargs='?', help='Path to image file to rename')
    parser.add_argument('-d', '--directory', help='Process all images in this directory')
    parser.add_argument('-r', '--recursive', action='store_true', 
                       help='Process subdirectories recursively')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be renamed without actually renaming')
    parser.add_argument('--width', type=float, default=0.90, 
                       help='Percentage of image width to scan (0.0-1.0, default: 0.70)')
    parser.add_argument('--height', type=float, default=0.2, 
                       help='Percentage of image height to scan (0.0-1.0, default: 0.4)')
    parser.add_argument('-v', '--verbose', action='store_true', 
                       help='Show detailed output')
    parser.add_argument('--extensions', nargs='+', 
                       help='File extensions to process (default: .jpg .jpeg .png .bmp .tiff .gif .webp)')
    parser.add_argument('--low-confidence', type=float, nargs='?', const=0.4, metavar='THRESHOLD',
                       help='Enable lower confidence threshold as fallback (default: 0.4, range: 0.0-1.0)')
    parser.add_argument('--no-skip', action='store_true',
                       help='Do not skip already-renamed files (only applies with --low-confidence)')
    
    args = parser.parse_args()
    
    # Validate percentages
    if not 0.0 < args.width <= 1.0:
        print("Error: --width must be between 0.0 and 1.0")
        return 1
    if not 0.0 < args.height <= 1.0:
        print("Error: --height must be between 0.0 and 1.0")
        return 1
    
    # Validate low confidence threshold if provided
    if args.low_confidence is not None and not 0.0 < args.low_confidence <= 1.0:
        print("Error: --low-confidence must be between 0.0 and 1.0")
        return 1
    
    # Process single image or directory
    skip_renamed = not args.no_skip  # Invert the flag: --no-skip means skip_renamed=False
    if args.image:
        # Check if the provided path is a directory
        image_path = Path(args.image)
        if image_path.is_dir():
            # Automatically process as directory
            process_directory(args.image, args.dry_run, args.width, args.height, 
                             args.recursive, args.verbose, args.extensions, args.low_confidence, skip_renamed)
        else:
            rename_image(args.image, args.dry_run, args.width, args.height, args.verbose, args.low_confidence, skip_renamed)
    elif args.directory:
        process_directory(args.directory, args.dry_run, args.width, args.height, 
                         args.recursive, args.verbose, args.extensions, args.low_confidence, skip_renamed)
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
