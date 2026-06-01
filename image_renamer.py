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


def extract_text(image_path, width_percentage=0.75, height_percentage=0.4):
    """Extract text using EasyOCR"""
    try:
        img = Image.open(image_path)
        width, height = img.size
        
        # Crop to top-left region
        crop_width = int(width * width_percentage)
        crop_height = int(height * height_percentage)
        top_left_region = img.crop((0, 0, crop_width, crop_height))
        
        # Get EasyOCR reader
        reader = get_easyocr_reader()
        
        # Run detection
        results = reader.readtext(
            np.array(top_left_region),
            paragraph=False,
            contrast_ths=0.3,
            adjust_contrast=0.8,
            text_threshold=0.6,
            low_text=0.3
        )
        
        # Sort by position (top to bottom, left to right)
        results.sort(key=lambda x: (x[0][0][1], x[0][0][0]))
        
        # Extract text with confidence > 0.5
        text_parts = [r[1] for r in results if r[2] > 0.5]
        return ' '.join(text_parts).strip()
        
    except Exception as e:
        print(f"OCR error: {e}")
        return ""


def clean_text_for_filename(text, max_length=100):
    """
    Clean extracted text to create a valid filename.
    
    Args:
        text: Raw text from OCR
        max_length: Maximum length for the filename
    
    Returns:
        Cleaned text suitable for a filename
    """
    if not text:
        return None
    
    # Take the first non-empty line
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return None
    
    filename = lines[0]
    
    # Clean up common OCR errors for better readability
    # Remove leading/trailing special characters that are likely OCR errors
    filename = re.sub(r'^[^\w\s]+', '', filename)  # Remove leading special chars
    filename = re.sub(r'[^\w\s]+$', '', filename)  # Remove trailing special chars
    
    # Replace common OCR mistakes in the middle (but preserve hyphens and spaces)
    # Keep only alphanumeric, spaces, hyphens, apostrophes, and parentheses
    filename = re.sub(r'[^\w\s\-\'()]', ' ', filename)
    
    # Remove or replace invalid filename characters for Windows
    # Windows invalid chars: < > : " / \ | ? *
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Replace multiple spaces with single space
    filename = re.sub(r'\s+', ' ', filename)
    
    # Trim to max length
    filename = filename[:max_length].strip()
    
    # Remove trailing dots and spaces (Windows doesn't allow)
    filename = filename.rstrip('. ')
    
    # Apply title case for consistent formatting (First Letter Capitalized)
    filename = filename.title()
    
    # If it's too short or empty after cleaning, reject it
    if len(filename) < 2:
        return None
    
    return filename if filename else None


def rename_image(image_path, dry_run=False, width_percentage=0.75, height_percentage=0.4, verbose=False):
    """
    Rename an image file based on text in the top-left corner.
    
    Args:
        image_path: Path to the image file
        dry_run: If True, don't actually rename, just show what would happen
        width_percentage: Percentage of image width to scan for text
        height_percentage: Percentage of image height to scan for text
        verbose: If True, show detailed output
    
    Returns:
        True if renamed successfully, False otherwise
    """
    image_path = Path(image_path)
    
    if not image_path.exists():
        print(f"File not found: {image_path}")
        return False
    
    # Extract text from top-left
    if verbose:
        print(f"Processing: {image_path.name}")
    
    # Extract text using EasyOCR
    text = extract_text(image_path, width_percentage, height_percentage)
    
    if verbose and text:
        print(f"  Detected text: {text[:100]}...")
    
    # Clean text for filename
    new_name = clean_text_for_filename(text)
    
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


def process_directory(directory, dry_run=False, width_percentage=0.75, height_percentage=0.4, 
                     recursive=False, verbose=False, extensions=None):
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
        if rename_image(image_file, dry_run, width_percentage, height_percentage, verbose):
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
    parser.add_argument('--width', type=float, default=0.75, 
                       help='Percentage of image width to scan (0.0-1.0, default: 0.75)')
    parser.add_argument('--height', type=float, default=0.4, 
                       help='Percentage of image height to scan (0.0-1.0, default: 0.4)')
    parser.add_argument('-v', '--verbose', action='store_true', 
                       help='Show detailed output')
    parser.add_argument('--extensions', nargs='+', 
                       help='File extensions to process (default: .jpg .jpeg .png .bmp .tiff .gif .webp)')
    
    args = parser.parse_args()
    
    # Validate percentages
    if not 0.0 < args.width <= 1.0:
        print("Error: --width must be between 0.0 and 1.0")
        return 1
    if not 0.0 < args.height <= 1.0:
        print("Error: --height must be between 0.0 and 1.0")
        return 1
    
    # Process single image or directory
    if args.image:
        rename_image(args.image, args.dry_run, args.width, args.height, args.verbose)
    elif args.directory:
        process_directory(args.directory, args.dry_run, args.width, args.height, 
                         args.recursive, args.verbose, args.extensions)
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
