#!/usr/bin/env python3
"""
merge_subcategories.py — Merges subcategory map into _data/linkography.yaml
Handles smart quotes, Python dictionaries, JSON, single quotes, and trailing commas.
"""

import json
import ast
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed.")
    sys.exit(1)

YAML_PATH = Path(__file__).parent.parent / "_data" / "linkography.yaml"
JSON_PATH = Path(__file__).parent / "subcategories.json"

def merge():
    if not YAML_PATH.exists() or not JSON_PATH.exists():
        print(f"[!] Ensure both {YAML_PATH.name} and {JSON_PATH.name} exist.")
        sys.exit(1)

    with open(YAML_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    print(f"[*] Reading raw content from {JSON_PATH.name}...")
    raw_content = JSON_PATH.read_text(encoding="utf-8")

    # Isolate everything between the first opening brace and last closing brace
    match = re.search(r"\{.*\}", raw_content, re.DOTALL)
    if not match:
        print("[!] Error: Could not find a valid dictionary object ({...}) inside subcategories.json.")
        sys.exit(1)
    
    content_str = match.group(0)

    # Normalize smart/curly quotes to straight quotes
    content_str = content_str.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")

    mapping = None
    # Try 1: Standard JSON parsing
    try:
        mapping = json.loads(content_str)
    except json.JSONDecodeError:
        # Try 2: Python literal evaluation (handles single quotes and trailing commas)
        try:
            print("[*] Notice: Standard JSON parse failed, parsing as a Python dictionary literal...")
            mapping = ast.literal_eval(content_str)
        except Exception as exc:
            print(f"[!] Parsing error: {exc}")
            sys.exit(1)

    if not isinstance(mapping, dict):
        print("[!] Error: Parsed content is not a valid dictionary mapping.")
        sys.exit(1)

    updated_count = 0
    for entry in data:
        entry_id = entry.get("id")
        if entry_id in mapping:
            entry["subcategory"] = mapping[entry_id]
            updated_count += 1

    with open(YAML_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True, default_flow_style=False)

    print(f"[SUCCESS] Updated {updated_count} entries with subcategories in {YAML_PATH.name}.")

if __name__ == "__main__":
    merge()