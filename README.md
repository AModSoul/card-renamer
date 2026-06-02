# Image Renamer

A Python tool that automatically renames image files based on text detected in the images using OCR (Optical Character Recognition). Designed for card games, it extracts both card names and collector information.

## Features

- 🎯 99%+ accuracy with EasyOCR on colored backgrounds
- 🃏 Detects card names from top-left corner
- 📊 Extracts collector info (set code & number) from bottom-left corner
- 📝 Automatically formats filenames as: `Card Name [SET] {NUMBER}`
- 🗂️ Batch process entire directories
- 🔄 Recursive directory processing
- 🛡️ Dry-run mode to preview changes
- ✅ Handles duplicate filenames automatically with (n) numbering
- 📏 Adjustable detection region size
- 🅰️ Title case formatting for consistent naming
- 🎚️ Configurable confidence thresholds for difficult text
- ⏭️ Smart skip of already-renamed files

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
By default, the tool scans the top-left 75% width × 40% height. You can adjust this:
```bash
python image_renamer.py -d ./images --width 0.8 --height 0.5
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
  --width FLOAT         Percentage of image width to scan (0.0-1.0, default: 0.75)
  --height FLOAT        Percentage of image height to scan (0.0-1.0, default: 0.4)
  -v, --verbose         Show detailed output
  --extensions EXT      File extensions to process (default: .jpg .jpeg .png .bmp .tiff .gif .webp)
  --low-confidence [THRESHOLD]
                        Enable lower confidence threshold as fallback (default: 0.4, range: 0.0-1.0)
  --no-skip             Do not skip already-renamed files (only applies with --low-confidence)
```

## How It Works

1. **Image Loading**: Opens the image file using PIL (Pillow)
2. **Card Name Detection**: 
   - Crops the top-left portion of the image (default: 75% width × 40% height)
   - Uses EasyOCR deep learning model to extract card name
   - First pass: Uses strict confidence threshold (>0.5)
   - Second pass (if `--low-confidence`): Falls back to lower threshold if nothing found
3. **Collector Info Detection**:
   - Crops the bottom-left corner (14% from left and bottom edges)
   - Extracts collector number (first line) and set code (second line)
4. **Text Cleaning**: 
   - Takes detected text
   - Applies title case formatting (First Letter Capitalized)
   - Removes invalid filename characters
   - Removes extra whitespace
   - Truncates to reasonable length
5. **Filename Formatting**: Creates filename as `Card Name [SET_CODE] {COLLECTOR_NUMBER}`
6. **File Renaming**: Renames the file, handling duplicates with (n) numbering

## Examples

**Before:**
```
IMG_001.webp  (contains "ALTRUISM" in top-left, "0001" and "MSW" in bottom-left)
IMG_002.webp  (contains "NOSTALGIA" in top-left, "0128" and "MSW" in bottom-left)
```

**After:**
```
Altruism [MSW] {0001}.webp
Nostalgia [MSW] {0128}.webp
```

**Duplicate Handling:**
```
Before: LOVE.webp, LOVE_2.webp, LOVE_3.webp
After:  Love [MSW] {0050}.webp, Love [MSW] {0050} (1).webp, Love [MSW] {0050} (2).webp
```

## Troubleshooting

### No Text Detected
- Ensure the card name is in the **top-left** corner
- Ensure collector info (number and set code) is in the **bottom-left** corner
- Try using `--low-confidence` to enable fallback detection for difficult text
- Try increasing the region size: `--width 0.9 --height 0.6`
- Check that the image quality is good enough for OCR
- Make sure the text is clear and readable
- First run downloads the EasyOCR model (~90MB)

### Poor OCR Accuracy
- Use higher resolution images
- Ensure good contrast between text and background
- Adjust the `--width` and `--height` parameters to focus on the text area
- Try `--low-confidence 0.3` to use a more lenient threshold (may increase false positives)
- EasyOCR achieves 99% accuracy on white text with colored backgrounds

### Low Confidence Mode
- **Default behavior**: Skips files already renamed with `[SET] {NUMBER}` pattern
- **Use `--no-skip`**: To re-process already-renamed files
- **Custom thresholds**: Use `--low-confidence 0.2` to 0.4 depending on text difficulty
  - 0.4 (default): Balanced accuracy and detection rate
  - 0.3: More lenient, catches difficult text but may have false positives
  - 0.2: Very lenient, use only for extremely difficult text

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.
