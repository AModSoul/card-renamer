import json
import sys
from pathlib import Path

if len(sys.argv) < 3:
    print("Usage: python filter_cards.py <input.json> <output.json>")
    sys.exit(1)

input_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])

with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

from collections import defaultdict

cards = data if isinstance(data, list) else data.get('data', [])

grouped = defaultdict(list)
for card in cards:
    if card.get("set_type") in ("alchemy","archenemy","funny", "memorabilia", "minigame", "planechase", "vanguard") or card.get("lang") != "en":
        continue  # Skip funny/joke sets (Unglued, Unhinged, etc.)
    
    image_uris = card.get('image_uris') or (card.get('card_faces', [{}])[0].get('image_uris') if card.get('card_faces') else {})
    png = image_uris.get('png') if isinstance(image_uris, dict) else None
    
    print_obj = {
        "png": png,
        "set": card.get("set"),
        "collector_number": card.get("collector_number"),
        "rarity": card.get("rarity"),
        "artist": card.get("artist")
    }

    flavor_name = card.get("flavor_name")
    if flavor_name:  # only add if it exists and is not null/empty
        print_obj["flavor_name"] = flavor_name

    grouped[card.get("name")].append(print_obj)

result = [
    {
        "name": name,
        "prints": prints
    }
    for name, prints in sorted(grouped.items())
]

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"Grouped {len(result)} unique names ({sum(len(p['prints']) for p in result)} prints) → {output_path}")