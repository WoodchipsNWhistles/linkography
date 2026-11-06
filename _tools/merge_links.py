#!/usr/bin/env python3
"""
merge_links.py — Final Bulletproof 8-Category Taxonomy Normalizer
"""

import sys
import yaml
import shutil

CATEGORY_MAP = {
    "ai-agents": "ai-agents-and-development",
    "developer-tools": "developer-and-system-utilities",
    "audio-video-image-manipulation": "media-and-creative-production",
    "open-data-and-reference": "productivity-reference-and-play",
    "osint-open-access-research": "osint-and-reconnaissance",
    "search-engines": "osint-and-reconnaissance",
    "office-productivity-utilities": "productivity-reference-and-play",
    "text-and-writing": "productivity-reference-and-play",
    "games-and-play": "productivity-reference-and-play"
}

def normalize_item(item):
    old_cat = str(item.get("category", "")).strip()
    subcat = str(item.get("subcategory", "")).strip().lower()
    title = str(item.get("title", "")).strip().lower()

    # Explicitly handle the hybrid legacy category
    if old_cat == "open-access-learning-and-archives":
        learning_keywords = ["learning", "training", "course", "cert", "bootcamp", "school", "academy", "workforce", "education"]
        if any(k in subcat or k in title for k in learning_keywords):
            new_cat = "online-learning-and-workforce-training"
        else:
            new_cat = "open-access-archives-and-research"
    else:
        new_cat = CATEGORY_MAP.get(old_cat, "productivity-reference-and-play")

    # STRICT Historical/Combat override (Guaranteed no blockchain/vector editor drift)
    strict_historical_terms = ["sca ", "hema", "fencing manual", "combat treatise", "physical culture", "martial arts treatise", "historical fencing"]
    if any(term in subcat or term in title for term in strict_historical_terms):
        new_cat = "historical-research-and-combat-arts"

    item["category"] = new_cat
    return item

def process_dataset(input_file, output_file):
    shutil.copy("_data/linkographold.yaml", input_file)

    with open(input_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or []

    normalized_data = [normalize_item(item) for item in data]

    counts = {}
    for item in normalized_data:
        c = item["category"]
        counts[c] = counts.get(c, 0) + 1

    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(normalized_data, f, sort_keys=False, allow_unicode=True)

    print(f"[+] Processed {len(normalized_data)} records across all 8 categories:")
    for cat, count in sorted(counts.items()):
        print(f"    - {cat}: {count} items")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        process_dataset(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python merge_links.py <input.yaml> <output.yaml>")