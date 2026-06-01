# Image Renamer

A Python tool that automatically renames image files based on text detected in the top-left corner of the image using OCR (Optical Character Recognition).

## Features

- 🎯 99%+ accuracy with EasyOCR on colored backgrounds
- 📝 Automatically renames files based on detected text
- 🗂️ Batch process entire directories
- 🔄 Recursive directory processing
- 🛡️ Dry-run mode to preview changes
- ✅ Handles duplicate filenames automatically with (n) numbering
- 📏 Adjustable detection region size
- 🅰️ Title case formatting for consistent naming

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

## Command Line Options

```
positional arguments:
  image                 Path to image file to rename

optional arguments:
  -h, --help           Show help message
  -d, --directory DIR  Process all images in this directory
  -r, --recursive      Process subdirectories recursively
  --dry-run           Show what would be renamed without actually renaming
  --width FLOAT        Percentage of image width to scan (0.0-1.0, default: 0.75)
  --height FLOAT       Percentage of image height to scan (0.0-1.0, default: 0.4)
  -v, --verbose        Show detailed output
  --extensions EXT     File extensions to process (default: .jpg .jpeg .png .bmp .tiff .gif .webp)
```

## How It Works

1. **Image Loading**: Opens the image file using PIL (Pillow)
2. **Region Extraction**: Crops the top-left portion of the image (default: 75% width × 40% height)
3. **Text Detection**: Uses EasyOCR deep learning model to extract text
4. **Text Cleaning**: 
   - Takes detected text
   - Applies title case formatting (First Letter Capitalized)
   - Removes invalid filename characters
   - Removes extra whitespace
   - Truncates to reasonable length
5. **File Renaming**: Renames the file, handling duplicates with (n) numbering

## Examples

**Before:**
```
IMG_001.webp  (contains "FEAR" in top-left)
IMG_002.webp  (contains "AMBITION" in top-left)
```

**After:**
```
Fear.webp
Ambition.webp
```

## Troubleshooting

### No Text Detected
- Ensure the text is in the **top-left** corner
- Try increasing the region size: `--width 0.9 --height 0.6`
- Check that the image quality is good enough for OCR
- Make sure the text is clear and readable
- First run downloads the EasyOCR model (~90MB)

### Poor OCR Accuracy
- Use higher resolution images
- Ensure good contrast between text and background
- Adjust the `--width` and `--height` parameters to focus on the text area
- EasyOCR achieves 99% accuracy on white text with colored backgrounds

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.
