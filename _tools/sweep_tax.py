import os
import yaml

# Define the new 9-Pillar Top-Level Categories
# 1. occupy-saas
# 2. office-productivity
# 3. research-and-reference
# 4. osint-and-reconnaissance
# 5. play
# 6. web-dev
# 7. ai-agents
# 8. av-creation
# 9. training-and-certs

# Specific ID overrides for tools moving to #OccupySaaS or Play
EXPLICIT_OVERRIDES = {
    # Heavy FOSS SaaS replacements -> Occupy SaaS
    "artcraft": {"category": "occupy-saas", "subcategory": "creative-suites"},
    "photopea": {"category": "occupy-saas", "subcategory": "creative-suites"},
    
    # Play / Cartography / Worldbuilding
    "watabous-procedural-generators-itch-page": {"category": "play", "subcategory": "tabletop-worldbuilding"},
    "mult-dev": {"category": "play", "subcategory": "cartography"},
    "bottleship": {"category": "play", "subcategory": "video-games"},
    "lo-pi-radio": {"category": "play", "subcategory": "play-goofy"},
}

def sweep_linkography(file_path):
    if not os.path.exists(file_path):
        print(f"[-] Error: Could not find {file_path}")
        return

    print(f"[*] Loading linkography from {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        entries = yaml.safe_load(f) or []

    updated_count = 0
    
    for entry in entries:
        item_id = entry.get("id")
        old_cat = entry.get("category", "")
        
        # 1. Check for explicit ID overrides first
        if item_id in EXPLICIT_OVERRIDES:
            override = EXPLICIT_OVERRIDES[item_id]
            entry["category"] = override["category"]
            if "subcategory" in override:
                entry["subcategory"] = override["subcategory"]
            print(f"[Override] '{entry.get('title')}': {old_cat} -> {override['category']}")
            updated_count += 1
            continue

        # 2. Bulk mapping of legacy top-level buckets to the new 9 pillars
        if old_cat in ["ai-agents-and-development", "ai-agents"]:
            entry["category"] = "ai-agents"
            updated_count += 1
            
        elif old_cat in ["developer-and-system-utilities", "developer-tools"]:
            entry["category"] = "web-dev"
            updated_count += 1
            
        elif old_cat in ["media-and-creative-production", "audio-video-image-manipulation"]:
            entry["category"] = "av-creation"
            updated_count += 1
            
        elif old_cat in ["open-access-archives-and-research", "open-data-and-reference"]:
            entry["category"] = "research-and-reference"
            updated_count += 1
            
        elif old_cat == "historical-research-and-combat-arts":
            entry["category"] = "research-and-reference"
            entry["subcategory"] = "historical-and-martial-arts"
            updated_count += 1
            
        elif old_cat in ["online-learning-and-workforce-training"]:
            entry["category"] = "training-and-certs"
            updated_count += 1
            
        elif old_cat in ["osint-and-reconnaissance", "osint-open-access-research", "search-engines"]:
            entry["category"] = "osint-and-reconnaissance"
            updated_count += 1
            
        elif old_cat in ["productivity-reference-and-play", "office-productivity-utilities", "text-and-writing"]:
            if "play" in entry.get("tags", []) or "game" in entry.get("tags", []):
                entry["category"] = "play"
            else:
                entry["category"] = "office-productivity"
            updated_count += 1

    # Save the updated YAML file
    print(f"\n[*] Saving updated linkography ({updated_count} entries re-mapped)...")
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(entries, f, sort_keys=False, allow_unicode=True, width=100)

    print("[✔] Category sweep complete! Run your Eleventy build to check permalinks.")

if __name__ == "__main__":
    # Pointing up one directory from _tools/ to find _data/linkography.yaml
    target_path = os.path.join(os.path.dirname(__file__), "../_data/linkography.yaml")
    sweep_linkography(target_path)