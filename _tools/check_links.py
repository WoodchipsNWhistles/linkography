#!/usr/bin/env python3
"""
check_links.py — Sovereign Linkography Duplicate & Schema Validator
Run this script before running 11ty to catch duplicate URLs or IDs.
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML is not installed. Install it with: pip install pyyaml")
    sys.exit(1)

# Inside _tools/check_links.py
# Point up one level from _tools/ to root, then into _data/links.yaml
DATA_FILE = Path(__file__).parent.parent / "_data" / "linkography.yaml"

def validate_links():
    if not DATA_FILE.exists():
        print(f"[!] Data file '{DATA_FILE}' not found.")
        sys.exit(1)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            entries = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            print(f"[!] Invalid YAML syntax:\n{exc}")
            sys.exit(1)

    if not isinstance(entries, list):
        print("[!] YAML root must be a list of link entries.")
        sys.exit(1)

    seen_ids = set()
    seen_urls = set()
    errors = []

    for index, entry in enumerate(entries, start=1):
        # 1. Required Field Checks
        entry_id = entry.get("id")
        title = entry.get("title", f"Entry #{index}")
        url = entry.get("url")
        category = entry.get("category")

        if not entry_id:
            errors.append(f"Entry #{index} ({title}): Missing required 'id' field.")
        if not url:
            errors.append(f"Entry #{index} ({title}): Missing required 'url' field.")
        if not category:
            errors.append(f"Entry #{index} ({title}): Missing required 'category' field.")

        # 2. Check for Duplicate IDs
        if entry_id:
            if entry_id in seen_ids:
                errors.append(f"DUPLICATE ID: '{entry_id}' found multiple times.")
            seen_ids.add(entry_id)

        # 3. Check for Duplicate URLs (normalized)
        if url:
            normalized_url = url.strip().rstrip("/").lower()
            if normalized_url in seen_urls:
                errors.append(f"DUPLICATE URL: '{url}' used in multiple entries.")
            seen_urls.add(normalized_url)

    # Output Validation Results
    if errors:
        print(f"\n[FAIL] Found {len(errors)} validation error(s):\n")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print(f"[OK] {len(entries)} entries validated successfully with zero duplicates.")

if __name__ == "__main__":
    validate_links()