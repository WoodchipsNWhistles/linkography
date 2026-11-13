import os
import yaml

# Define mapping rules for entries currently stuck in 'ai-dev-platforms'
# Key: item ID, Value: (new_category, new_subcategory)
MIGRATION_MAP = {
    "bottleship": ("productivity-reference-and-play", "games-and-play"),
	"circuitjs1": ("developer-and-system-utilities", "electronics-design"),
	"kicanvas": ("developer-and-system-utilities", "electronics-design"),
	"editorapdf": ("developer-and-system-utilities", "office-productivity-utilities"),
	"fit-stats": ("developer-and-system-utilities", "device-and-network-utilities"),
	"weaponize-it": ("osint-and-reconnaissance", "threat-intelligence")
}

def clean_ai_dev_platforms(file_path):
    if not os.path.exists(file_path):
        print(f"[-] Error: Could not find {file_path}")
        return

    print(f"[*] Loading linkography from {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        entries = yaml.safe_load(f) or []

    migrated_count = 0
    for entry in entries:
        item_id = entry.get("id")
        
        if item_id in MIGRATION_MAP:
            new_cat, new_sub = MIGRATION_MAP[item_id]
            old_cat = entry.get("category")
            old_sub = entry.get("subcategory")
            
            entry["category"] = new_cat
            entry["subcategory"] = new_sub
            
            print(f"[+] Migrated '{entry.get('title')} ({item_id})':")
            print(f"    Category:    {old_cat} -> {new_cat}")
            print(f"    Subcategory: {old_sub} -> {new_sub}")
            migrated_count += 1

    # Write back clean YAML
    print(f"\n[*] Saving updated linkography ({migrated_count} items re-homed)...")
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(entries, f, sort_keys=False, allow_unicode=True, width=100)

    print("[✔] Cleanup complete! Run your Eleventy build to verify.")

if __name__ == "__main__":
    # Automatically locate _data/linkography.yaml relative to _tools/fix_cats.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.normpath(os.path.join(script_dir, "../_data/linkography.yaml"))
    
    clean_ai_dev_platforms(target_path)