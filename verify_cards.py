#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path
from collections import defaultdict
import difflib

def parse_filename(filename):
    stem = filename.stem
    match = re.search(r'^(.*?)(?:\s*\((.*?)\))?\s*\[([A-Z0-9]+)\]\s*\{(\d+)\}', stem)
    if match:
        main_name = re.sub(r'[_ ]+$', '', match.group(1).strip())
        nickname = match.group(2).strip() if match.group(2) else None
        set_code = match.group(3)
        collector = match.group(4)
        return {
            'name': main_name,
            'nickname': nickname,
            'set': set_code,
            'collector': collector,
            'original': str(filename)
        }
    # Fallback for bad filenames (numbers only, missing brackets, etc)
    cleaned = re.sub(r'\s*\[.*?\]\s*\{.*?\}', '', stem)
    cleaned = re.sub(r'[_ ]+$', '', cleaned)
    if cleaned.isdigit() or len(cleaned) < 3:  # avoid pure numbers like '1311'
        cleaned = "Unknown"
    return {
        'name': cleaned.strip(),
        'nickname': None,
        'set': None,
        'collector': None,
        'original': str(filename)
    }

def main():
    parser = argparse.ArgumentParser(description="Verify images against grouped JSON (name + flavor_name as nickname)")
    parser.add_argument('--folder', type=Path, required=True, help='Folder with renamed images')
    parser.add_argument('--json', type=Path, default=Path('filtered_cards.json'), help='Path to grouped JSON (defaults to root)')
    parser.add_argument('--fix', action='store_true', help='Auto-fix obvious filename errors using JSON')
    args = parser.parse_args()

    if not args.folder.exists():
        print(f"Folder not found: {args.folder}")
        return
    if not args.json.exists():
        print(f"JSON not found: {args.json}. Run filter_cards.py first.")
        return

    # Load grouped JSON (name -> list of prints with flavor_name)
    with open(args.json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    card_db = {}
    for item in data:
        if isinstance(item, dict) and 'name' in item and 'prints' in item:
            card_db[item['name'].lower()] = item['prints']
            if '//' in item['name']:
                parts = [p.strip().lower() for p in item['name'].split('//')]
                for p in parts:
                    card_db[p] = item['prints']

    collector_map = defaultdict(list)
    for name, prints in card_db.items():
        for p in prints:
            collector = str(p.get('collector_number', '')).lstrip('0') or '0'
            collector_map[collector].append(name)

    image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    images = [f for f in args.folder.glob('*') if f.is_file() and f.suffix.lower() in image_extensions]

    unmatched = []
    fixed_count = 0

    print(f"Checking {len(images)} images against {len(card_db)} unique cards (using flavor_name as nickname)...\n")

    for img in sorted(images):
        info = parse_filename(img)
        name_lower = re.sub(r'[_ ]+$', '', info['name'].lower())
        
        # Skip if already correct (skip numeric names like "1385" so they get fixed by collector lookup)
        if info['set'] and info['collector'] and not info['name'].isdigit() and name_lower in card_db:
            expected_stem = f"{info['name']} [{info['set']}] {{{info['collector']}}}"
            if expected_stem.lower() in img.stem.lower() or info['name'].lower() in img.stem.lower():
                continue
        
        # First pass: card name with better cleaning and collector-aware matching
        if name_lower not in card_db:
            close_matches = difflib.get_close_matches(name_lower, card_db.keys(), n=3, cutoff=0.85)
            matched = False
            for close_name in close_matches:
                prints = card_db.get(close_name, [])
                for p in prints:
                    if str(p.get('collector_number', '')) == info['collector']:  # match name + collector, ignore current set to fix set code
                        correct_name = close_name.title().replace("'", "'")
                        if '//' in correct_name:
                            parts = [p.strip() for p in correct_name.split('//')]
                            correct_name = next((p for p in parts if p.lower() in info['name'].lower() or info['name'].lower() in p.lower()), parts[0])
                        new_stem = f"{correct_name}{f' ({info['nickname']})' if info['nickname'] else ''}"
                        new_stem = re.sub(r'[:/\\|?*<>""]', '-', new_stem)
                        new_stem = new_stem.replace(' // ', ' - ').replace('//', ' - ')
                        new_path = img.with_name(f"{new_stem} [{p.get('set', info['set']).upper()}] {{{info['collector']}}}{img.suffix}")
                        if new_path == img:
                            continue
                        if new_path.exists():
                            counter = 1
                            name_part = new_path.stem
                            extension = new_path.suffix
                            while new_path.exists():
                                new_path = new_path.with_name(f"{name_part} ({counter}){extension}")
                                counter += 1
                        try:
                            img.rename(new_path)
                            print(f"FIXED: {img.name} → {new_path.name} (matched collector {info['collector']})")
                            matched = True
                            break
                        except Exception as e:
                            print(f"Failed to rename {img.name}: {e}")
                if matched:
                    break
            if not matched:
                unmatched.append(f"{img.name} - NO NAME MATCH (closest: {close_matches[0] if close_matches else 'none'})")
                continue
        
        # Second pass: check prints for matching nickname (flavor_name), set, and collector
        prints = card_db.get(name_lower, [])
        match_found = False
        for p in prints:
            json_flavor = p.get("flavor_name")
            name_match = (not json_flavor or not info['nickname'] or
                         json_flavor.lower() in info['nickname'].lower() or
                         info['nickname'].lower() in json_flavor.lower())
            if name_match and str(p.get('collector_number', '')) == info['collector']:
                match_found = True
                break
        
        if not match_found:
            unmatched.append(f"{img.name} - NAME MATCHED but NO matching flavor_name/set/collector in JSON prints")
            continue

        
        # First pass: card name with better cleaning and collector-aware matching
        if name_lower not in card_db:
            close_matches = difflib.get_close_matches(name_lower, card_db.keys(), n=3, cutoff=0.6)
            matched = False
            for close_name in close_matches:
                prints = card_db.get(close_name, [])
                for p in prints:
                    if str(p.get('collector_number', '')) == info['collector']:  # match name + collector, ignore current set to fix set code
                        correct_name = close_name.title().replace("'", "'")
                        if '//' in correct_name:
                            parts = [p.strip() for p in correct_name.split('//')]
                            correct_name = next((p for p in parts if p.lower() in info['name'].lower() or info['name'].lower() in p.lower()), parts[0])
                        new_stem = f"{correct_name}{f' ({info['nickname']})' if info['nickname'] else ''}"
                        new_stem = re.sub(r'[:/\\|?*<>""]', '-', new_stem)
                        new_stem = new_stem.replace(' // ', ' - ').replace('//', ' - ')
                        new_path = img.with_name(f"{new_stem} [{p.get('set', info['set']).upper()}] {{{info['collector']}}}{img.suffix}")
                        if new_path == img:
                            continue
                        if new_path.exists():
                            counter = 1
                            name_part = new_path.stem
                            extension = new_path.suffix
                            while new_path.exists():
                                new_path = new_path.with_name(f"{name_part} ({counter}){extension}")
                                counter += 1
                        try:
                            img.rename(new_path)
                            print(f"FIXED: {img.name} → {new_path.name} (matched collector {info['collector']})")
                            matched = True
                            break
                        except Exception as e:
                            print(f"Failed to rename {img.name}: {e}")
                if matched:
                    break
            if not matched:
                unmatched.append(f"{img.name} - NO NAME MATCH (closest: {close_matches[0] if close_matches else 'none'})")
                continue

                if new_path.exists():
                            counter = 1
                            name_part = new_path.stem
                            extension = new_path.suffix
                            while new_path.exists():
                                new_path = new_path.with_name(f"{name_part} ({counter}){extension}")
                                counter += 1
                try:
                    img.rename(new_path)
                    print(f"FIXED: {img.name} → {new_path.name} (matched collector {info['collector']})")
                    matched = True
                    break
                except Exception as e:
                    print(f"Failed to rename {img.name}: {e}")
                if matched:
                    break
            if not matched:
                unmatched.append(f"{img.name} - NO NAME MATCH (closest: {close_matches[0] if close_matches else 'none'})")
                continue
        
        # Second pass: check prints for matching nickname (flavor_name), set, and collector
        prints = card_db.get(name_lower, [])
        match_found = False
        for p in prints:
            json_flavor = p.get("flavor_name")
            name_match = (not json_flavor or not info['nickname'] or
                         json_flavor.lower() in info['nickname'].lower() or
                         info['nickname'].lower() in json_flavor.lower())
            if name_match and str(p.get('collector_number', '')) == info['collector']:
                match_found = True
                break
        
        if not match_found:
            unmatched.append(f"{img.name} - NAME MATCHED but NO matching flavor_name/set/collector in JSON prints")
            continue

        
        # Collector-first search (fixes numeric/garbled names like "1385", "1311", "Joshua Phoenix S Dominant", "Opera Love Song_", "Crystal Fragments")
        key = str(info['collector']).lstrip('0') or '0' if info['collector'] else ''
        if key in collector_map:
            correct_name = collector_map[key][0]
            if '//' in correct_name:
                parts = [p.strip() for p in correct_name.split('//')]
                best_part = parts[0]
                best_ratio = 0
                for p in parts:
                    ratio = difflib.SequenceMatcher(None, p.lower(), info['name'].lower()).ratio()
                    if ratio > best_ratio:
                        best_ratio = ratio
                        best_part = p
                correct_name = best_part
            new_stem = f"{correct_name.title()}{f' ({info['nickname']})' if info['nickname'] else ''}"
            new_stem = re.sub(r'[:/\\|?*<>""]', '-', new_stem)
            new_stem = new_stem.replace(' // ', ' - ').replace('//', ' - ')
            new_path = img.with_name(f"{new_stem} [{info['set']}] {{{info['collector']}}}{img.suffix}")
            if new_path == img:  # skip if already correct (prevents "already exists" error)
                continue
            if new_path.exists():
                counter = 1
                name_part = new_path.stem
                extension = new_path.suffix
                while new_path.exists():
                    new_path = new_path.with_name(f"{name_part} ({counter}){extension}")
                    counter += 1
            try:
                img.rename(new_path)
                print(f"FIXED: {img.name} → {new_path.name} (matched collector {info['collector']})")
                fixed_count += 1
                continue
            except Exception as e:
                print(f"Failed to rename {img.name}: {e}")
        
        unmatched.append(f"{img.name} - NO MATCH for collector/set in JSON")
        continue

    if unmatched:
        unmatched_file = args.folder / "unmatched.txt"
        with open(unmatched_file, 'w', encoding='utf-8') as f:
            f.write("Unmatched images (name, flavor_name/nickname, set, or collector mismatch):\n\n")
            f.write('\n'.join(unmatched))
        print(f"\nFound {len(unmatched)} unmatched images. List written to {unmatched_file}")
    else:
        print("\nAll images matched successfully!")

    if args.fix and fixed_count > 0:
        print(f"Fixed {fixed_count} filenames.")

if __name__ == "__main__":
    main()