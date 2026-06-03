"""
Scryfall Set Image Downloader

Downloads all unique PNG images from a specified Magic: The Gathering set
using the Scryfall API.

Usage:
    python download_scryfall_set.py <set_code> [output_directory]

Example:
    python download_scryfall_set.py mid downloads/midnight_hunt
"""

import requests
import time
import os
import sys
from pathlib import Path
from typing import Set, Dict, List

if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class ScryfallSetDownloader:
    BASE_URL = "https://api.scryfall.com"
    HEADERS = {
        "User-Agent": "ScryfallSetDownloader/1.0",
        "Accept": "application/json"
    }
    # Scryfall rate limits: /cards/search requires 500ms, other endpoints 100ms
    # Image files at *.scryfall.io have NO rate limits
    SEARCH_DELAY = 0.5  # 500ms for /cards/search endpoint (2 requests/second)
    IMAGE_DELAY = 0.05  # Small delay for images (optional, just being polite)

    def __init__(self, set_code: str, output_dir: str = None):
        self.set_code = set_code.lower()
        self.output_dir = Path(output_dir or f"scryfall_{self.set_code}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.stats = {
            "total_cards": 0,
            "unique_images": 0,
            "skipped_duplicates": 0,
            "failed_downloads": 0
        }

    def search_cards(self) -> List[Dict]:
        """Search for all cards in the specified set."""
        all_cards = []
        url = f"{self.BASE_URL}/cards/search"
        params = {
            "q": f"set:{self.set_code}",
            "unique": "prints"  # Get all printings
        }

        print(f"Fetching cards from set '{self.set_code}'...")

        while url:
            response = self.session.get(url, params=params)
            
            if response.status_code != 200:
                print(f"Error: API returned status {response.status_code}")
                print(f"Message: {response.text}")
                sys.exit(1)

            data = response.json()
            cards = data.get("data", [])
            all_cards.extend(cards)
            
            print(f"  Fetched {len(cards)} cards... (Total: {len(all_cards)})")

            # Check if there are more pages
            if data.get("has_more", False):
                url = data.get("next_page")
                params = None  # Next page URL already includes params
                time.sleep(self.SEARCH_DELAY)  # /cards/search requires 500ms delay
            else:
                url = None

        self.stats["total_cards"] = len(all_cards)
        print(f"Found {len(all_cards)} total cards in set '{self.set_code}'")
        return all_cards

    def get_image_urls(self, card: Dict) -> List[Dict[str, str]]:
        """Extract PNG image URLs from a card object."""
        images = []

        # Check if card has image_uris (single-faced cards)
        if "image_uris" in card and card["image_uris"]:
            png_url = card["image_uris"].get("png")
            if png_url:
                illustration_id = card.get("illustration_id")
                images.append({
                    "url": png_url,
                    "illustration_id": illustration_id,
                    "name": card.get("name", "unknown"),
                    "face": None
                })

        # Check if card has multiple faces (double-faced cards, split cards, etc.)
        elif "card_faces" in card and card["card_faces"]:
            for idx, face in enumerate(card["card_faces"]):
                if "image_uris" in face and face["image_uris"]:
                    png_url = face["image_uris"].get("png")
                    if png_url:
                        illustration_id = face.get("illustration_id")
                        images.append({
                            "url": png_url,
                            "illustration_id": illustration_id,
                            "name": face.get("name", "unknown"),
                            "face": idx
                        })

        return images

    def sanitize_filename(self, name: str) -> str:
        """Remove characters that are invalid in filenames."""
        # Replace invalid characters with underscore
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        # Replace // with _ (for split cards)
        name = name.replace(' // ', '_')
        return name.strip()

    def download_image(self, image_info: Dict[str, str]) -> bool:
        """Download a single image."""
        url = image_info["url"]
        illustration_id = image_info["illustration_id"]
        name = image_info["name"]
        face = image_info["face"]

        # Generate base filename
        safe_name = self.sanitize_filename(name)
        if face is not None:
            base_filename = f"{safe_name}_face{face}.png"
        else:
            base_filename = f"{safe_name}.png"

        # Check if file exists and add (1), (2), etc. suffix if needed
        filename = base_filename
        filepath = self.output_dir / filename
        
        if filepath.exists():
            counter = 1
            name_part = base_filename.rsplit('.', 1)[0]
            extension = base_filename.rsplit('.', 1)[1]
            while filepath.exists():
                filename = f"{name_part} ({counter}).{extension}"
                filepath = self.output_dir / filename
                counter += 1
            self.stats["skipped_duplicates"] += 1

        # Download the image
        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.stats["unique_images"] += 1
            print(f"  ✓ Downloaded: {filename}")
            return True

        except Exception as e:
            print(f"  ✗ Failed to download {name}: {e}")
            self.stats["failed_downloads"] += 1
            return False

    def download_all(self):
        """Main function to download all unique images from the set."""
        print(f"\nStarting download to: {self.output_dir.absolute()}\n")

        # Get all cards from the set
        cards = self.search_cards()

        if not cards:
            print("No cards found!")
            return

        print(f"\nDownloading images...\n")

        for card in cards:
            images = self.get_image_urls(card)
            for image_info in images:
                self.download_image(image_info)
                time.sleep(self.IMAGE_DELAY)

        # Print summary
        print("\n" + "="*60)
        print("Download Summary:")
        print("="*60)
        print(f"Total cards in set:       {self.stats['total_cards']}")
        print(f"Images downloaded:        {self.stats['unique_images']}")
        print(f"Duplicates skipped:       {self.stats['skipped_duplicates']}")
        print(f"Failed downloads:         {self.stats['failed_downloads']}")
        print(f"Output directory:         {self.output_dir.absolute()}")
        print("="*60)


def main():
    if len(sys.argv) < 2:
        print("Usage: python download_scryfall_set.py <set_code> [output_directory]")
        print("\nExample:")
        print("  python download_scryfall_set.py mid")
        print("  python download_scryfall_set.py war downloads/war_of_the_spark")
        print("\nCommon set codes:")
        print("  mid - Innistrad: Midnight Hunt")
        print("  neo - Kamigawa: Neon Dynasty")
        print("  mkm - Murders at Karlov Manor")
        print("\nFind more set codes at: https://scryfall.com/sets")
        sys.exit(1)

    set_code = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    downloader = ScryfallSetDownloader(set_code, output_dir)
    downloader.download_all()


if __name__ == "__main__":
    main()
