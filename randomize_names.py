import random
from pathlib import Path

def randomize_filenames(directory):
    """Rename all image files in a directory to random numbers between 10 and 10000."""
    directory = Path(directory)
    
    # Image extensions to process
    extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp'}
    
    # Get all image files
    image_files = [f for f in directory.glob('*') 
                   if f.is_file() and f.suffix.lower() in extensions]
    
    if not image_files:
        print(f"No image files found in {directory}")
        return
    
    print(f"Found {len(image_files)} image(s) to rename\n")
    
    # Generate unique random numbers
    random_numbers = random.sample(range(10, 10001), len(image_files))
    
    # Rename each file
    renamed_count = 0
    for image_file, rand_num in zip(image_files, random_numbers):
        new_name = f"{rand_num}{image_file.suffix}"
        new_path = image_file.parent / new_name
        
        # Handle collision (very unlikely but just in case)
        counter = 1
        while new_path.exists():
            new_name = f"{rand_num}_{counter}{image_file.suffix}"
            new_path = image_file.parent / new_name
            counter += 1
        
        try:
            image_file.rename(new_path)
            print(f"[OK] {image_file.name} → {new_name}")
            renamed_count += 1
        except Exception as e:
            print(f"[!] Failed to rename {image_file.name}: {e}")
    
    print(f"\nRenamed {renamed_count} of {len(image_files)} files")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python randomize_names.py <directory>")
        sys.exit(1)
    
    randomize_filenames(sys.argv[1])
