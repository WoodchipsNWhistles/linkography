#!/usr/bin/env python3
"""
clean_yaml.py — Sovereign Linkography YAML Auto-Cleaner & ID Generator
Cleans _data/linkography.yaml by generating unique IDs and stripping duplicate URLs.
"""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML is not installed. Run: python3 -m pip install pyyaml --break-system-packages")
    sys.exit(1)

# Path relative to project root
INPUT_FILE = Path(__file__).parent.parent / "_data" / "linkography.yaml"
OUTPUT_FILE = Path(__file__).parent.parent / "_data" / "linkography_clean.yaml"

def slugify(text):
    """Convert title string to a clean URL-friendly slug ID."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)  # Strip special characters
    text = re.sub(r'[\s_]+', '-', text)       # Replace spaces/underscores with hyphens
    text = re.sub(r'-+', '-', text)           # Strip consecutive hyphens
    return text.strip('-')

def clean_links():
    if not INPUT_FILE.exists():
        print(f"[!] Target file '{INPUT_FILE}' not found.")
        sys.exit(1)

    print(f"[*] Reading {INPUT_FILE}...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        try:
            entries = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            print(f"[!] Invalid YAML syntax in source file:\n{exc}")
            sys.exit(1)

    if not isinstance(entries, list):
        print("[!] Root structure of YAML must be a list of entries.")
        sys.exit(1)

    cleaned_entries = []
    seen_urls = set()
    seen_ids = set()

    duplicates_removed = 0

    for idx, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            continue

        url = entry.get("url")
        title = entry.get("title", f"Entry {idx}")

        # 1. De-duplicate URLs (normalize by trimming whitespace and trailing slashes)
        if url:
            normalized_url = str(url).strip().rstrip("/").lower()
            if normalized_url in seen_urls:
                duplicates_removed += 1
                continue
            seen_urls.add(normalized_url)

        # 2. Assign / Fix unique ID
        base_id = entry.get("id") or slugify(title) or f"entry-{idx}"
        unique_id = base_id
        counter = 1

        while unique_id in seen_ids:
            unique_id = f"{base_id}-{counter}"
            counter += 1

        seen_ids.add(unique_id)
        entry["id"] = unique_id

        cleaned_entries.append(entry)

    # Write cleaned structure back out
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        yaml.dump(cleaned_entries, f, sort_keys=False, allow_unicode=True, default_flow_style=False)

    print("\n==========================================")
    print(f"[SUCCESS] Processed {len(entries)} raw entries.")
    print(f"[+] Duplicate URLs removed: {duplicates_removed}")
    print(f"[+] Final clean entries count: {len(cleaned_entries)}")
    print(f"[+] Saved pristine file to: {OUTPUT_FILE}")
    print("==========================================\n")

if __name__ == "__main__":
    clean_links()
