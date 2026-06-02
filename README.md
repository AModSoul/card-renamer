# Image Renamer

A Python tool that automatically renames image files based on text detected in the images using OCR (Optical Character Recognition). Designed for card games (especially Magic: The Gathering), it extracts card names, including multi-line nicknames, and collector information (set codes and numbers).

Perfect for organizing card image collections with consistent naming: `Card Name [SET] {NUMBER}` or `Main Name (Nickname) [SET] {NUMBER}` for alternate art cards.

## Features

- 🎯 99%+ accuracy with EasyOCR on colored backgrounds
- 🃏 Detects card names from top-left corner (90% width × 20% height)
- 📊 Extracts collector info (set code & number) from bottom-left corner (20% width × 10% height)
- 📝 Automatically formats filenames as: `Card Name [SET] {NUMBER}`
- 🎭 **Multi-line card name support** - detects nicknames/alternate titles and formats as `Main Name (Nickname) [SET] {NUMBER}`
- ✍️ **Automatic contraction fixing** - corrects common OCR mistakes like "Youre" → "You're"
- 🔤 Preserves special characters (apostrophes, commas, parentheses)
- 🗂️ Batch process entire directories
- 🔄 Recursive directory processing
- 🛡️ Dry-run mode to preview changes
- ✅ Handles duplicate filenames automatically with (n) numbering
- 📏 Adjustable detection region size
- 🅰️ Smart title case formatting for consistent naming
- 🎚️ Configurable confidence thresholds for difficult text
- 🔍 Low-confidence fallback for set codes (detects even at 0.15 confidence)
- ⏭️ Smart skip of already-renamed files

## Key Features Explained

### Multi-line Card Name Detection
The tool automatically detects when card names span 2 lines (common with alternate art/nickname variants):
- Analyzes vertical positioning of detected text
- Groups text lines that are within 20 pixels of each other
- Formats as `Main Name (Nickname)` when 2 lines detected
- Example: `Academy Ruins (Kitezh, Sunken City) [SLD] {1506}`

### Automatic Contraction Fixing
OCR often fails to detect apostrophes in contractions. The tool automatically fixes 30+ common contractions:
- You're, Don't, Can't, Won't, Isn't, Wasn't, Weren't, Aren't
- Didn't, Doesn't, Hasn't, Haven't, Wouldn't, Shouldn't, Couldn't
- I'm, I've, I'd, I'll, He's, She's, It's
- That's, What's, Who's, There's, Here's, Let's, Where's
- We've, They're, They've, We'll, They'll

### Smart Character Preservation
Unlike basic filename cleaners, this tool preserves meaningful characters:
- **Apostrophes**: "You're" not "Youre"
- **Commas**: "Kitezh, Sunken City" not "Kitezh Sunken City"
- **Parentheses**: "(Nickname)" format for multi-line cards
- **Custom title case**: Properly capitalizes words starting with special characters

### Intelligent Set Code Detection
Set codes are often small and low-confidence. The tool uses a two-tier approach:
- First: Searches high-confidence detections (>0.5)
- Fallback: If not found, searches all detections with confidence >0.15
- Extracts 2-3 letter codes even from noisy text like "SLD . EN"

## Prerequisites

### 1. Install Python
Make sure you have Python 3.7 or higher installed.

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

**Note:** EasyOCR will download a ~90MB model on first use.

## Usage

### Basic Usage

#### Rename a Single Image
```bash
python image_renamer.py path/to/image.jpg
```

#### Process All Images in a Directory
```bash
python image_renamer.py --directory ./images
```

#### Dry Run (Preview Changes)
```bash
python image_renamer.py --directory ./images --dry-run
```

### Advanced Options

#### Process Subdirectories Recursively
```bash
python image_renamer.py -d ./images --recursive
```

#### Adjust Detection Region Size
By default, the tool scans the top-left 90% width × 20% height for card names. You can adjust this:
```bash
python image_renamer.py -d ./images --width 0.8 --height 0.3
```

#### Verbose Output
```bash
python image_renamer.py -d ./images --verbose
```

#### Specify File Extensions
```bash
python image_renamer.py -d ./images --extensions .jpg .png .webp
```

#### Enable Low Confidence Detection
For cards with difficult-to-read text, enable fallback to lower confidence threshold:
```bash
# Use default 0.4 threshold
python image_renamer.py -d ./images --low-confidence

# Use custom threshold (e.g., 0.3 or 0.2)
python image_renamer.py -d ./images --low-confidence 0.3
```

**Note:** Low confidence mode automatically skips already-renamed files (those with `[SET] {NUMBER}` format).

#### Process Already-Renamed Files
To re-process files that are already renamed:
```bash
python image_renamer.py -d ./images --low-confidence --no-skip
```

## Command Line Options

```
positional arguments:
  image                 Path to image file to rename

optional arguments:
  -h, --help            Show help message
  -d, --directory DIR   Process all images in this directory
  -r, --recursive       Process subdirectories recursively
  --dry-run             Show what would be renamed without actually renaming
  --width FLOAT         Percentage of image width to scan (0.0-1.0, default: 0.90)
  --height FLOAT        Percentage of image height to scan (0.0-1.0, default: 0.2)
  -v, --verbose         Show detailed output
  --extensions EXT      File extensions to process (default: .jpg .jpeg .png .bmp .tiff .gif .webp)
  --low-confidence [THRESHOLD]
                        Enable lower confidence threshold as fallback (default: 0.4, range: 0.0-1.0)
  --no-skip             Do not skip already-renamed files (only applies with --low-confidence)
```

## How It Works

1. **Image Loading**: Opens the image file using PIL (Pillow)
2. **Card Name Detection**: 
   - Crops the top-left portion of the image (default: 90% width × 20% height)
   - Uses EasyOCR deep learning model to extract card name
   - First pass: Uses strict confidence threshold (>0.6)
   - Second pass (if `--low-confidence`): Falls back to lower threshold if nothing found
   - **Multi-line detection**: Automatically detects when card names span 2 lines (e.g., nicknames)
   - Groups lines by vertical position and formats as `Main Name (Nickname)`
3. **Collector Info Detection**:
   - Crops the bottom-left corner (20% width × 10% height)
   - Extracts collector number (3-4 digit pattern) and set code (2-3 letter pattern)
   - Uses regex patterns to find numbers and set codes
   - **Set code fallback**: If not found initially, searches all detections with confidence >0.15
   - Cleans collector numbers by removing leading letters (e.g., "R 2390" → "2390")
4. **Text Cleaning**: 
   - Fixes common contractions that OCR often misses apostrophes on:
     - "Youre" → "You're", "Dont" → "Don't", "Cant" → "Can't", etc.
   - Preserves special characters: apostrophes, commas, parentheses
   - Applies custom title case formatting (handles words starting with special chars)
   - Removes invalid filename characters
   - Removes extra whitespace
   - Truncates to reasonable length
5. **Filename Formatting**: Creates filename as `Card Name [SET_CODE] {COLLECTOR_NUMBER}`
   - Multi-line cards: `Main Name (Nickname) [SET] {NUMBER}`
   - Single-line cards: `Card Name [SET] {NUMBER}`
6. **File Renaming**: Renames the file, handling duplicates with (n) numbering

## Examples

**Basic Card Names:**
```
Before: IMG_001.png
After:  Abrade [SLD] {2390}.png

Before: photo_123.png
After:  Invisible Woman [MSC] {0001}.png
```

**Multi-line Card Names with Nicknames:**
```
Before: card_scan.png (has "ABRADE" on top line, "YOU'RE GONNA NEED A BIGGER BOAT" on second line)
After:  Abrade (You're Gonna Need A Bigger Boat) [SLD] {2179}.png

Before: ruins.png (has "ACADEMY RUINS" on top line, "KITEZH, SUNKEN CITY" on second line)
After:  Academy Ruins (Kitezh, Sunken City) [SLD] {1506}.png
```

**Contraction Fixing:**
```
OCR detects: "Youre Gonna Need A Bigger Boat"
Result:      "You're Gonna Need A Bigger Boat"

OCR detects: "Dont Worry"
Result:      "Don't Worry"
```

**Duplicate Handling:**
```
Before: card1.png, card2.png, card3.png (all same card)
After:  Spell Pierce [SLD] {2388}.png
        Spell Pierce [SLD] {2388} (1).png
        Spell Pierce [SLD] {2388} (2).png
```

## Troubleshooting

### No Text Detected
- Ensure the card name is in the **top-left** corner
- Ensure collector info (number and set code) is in the **bottom-left** corner
- Try using `--low-confidence` to enable fallback detection for difficult text
- Try adjusting the region size: `--width 0.95 --height 0.25`
- Check that the image quality is good enough for OCR
- Make sure the text is clear and readable
- First run downloads the EasyOCR model (~90MB)

### Multi-line Card Names
- The tool automatically detects when a card name spans 2 lines
- It formats them as `Main Name (Nickname) [SET] {NUMBER}`
- If detection fails, try increasing `--width` to 0.95 or higher to capture full text
- Reduce `--height` to 0.15-0.20 to avoid capturing card text below the name

### Set Code Not Detected
- Set codes use a fallback confidence threshold of 0.15 to catch small/blurry text
- If still not detected, the set code may be too blurry or positioned differently
- Check that the set code is in the **bottom-left corner** of the card

### Poor OCR Accuracy
- Use higher resolution images
- Ensure good contrast between text and background
- Adjust the `--width` and `--height` parameters to focus on the text area
- Try `--low-confidence 0.3` to use a more lenient threshold (may increase false positives)
- EasyOCR achieves 99% accuracy on white text with colored backgrounds

### Contraction Issues
- The tool automatically fixes 30+ common contractions
- If a specific contraction isn't being fixed, it may need to be added to the contraction list
- Supported: You're, Don't, Can't, Won't, I'm, It's, That's, and many more

### Low Confidence Mode
- **Default behavior**: Skips files already renamed with `[SET] {NUMBER}` pattern
- **Use `--no-skip`**: To re-process already-renamed files
- **Custom thresholds**: Use `--low-confidence 0.2` to 0.4 depending on text difficulty
  - 0.4 (default): Balanced accuracy and detection rate
  - 0.3: More lenient, catches difficult text but may have false positives
  - 0.2: Very lenient, use only for extremely difficult text
- **Card name threshold**: 0.6 (strict to avoid symbols and card text)
- **Set code fallback**: 0.15 (very lenient to catch small text)

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.
