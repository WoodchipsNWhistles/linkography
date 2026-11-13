import os
import yaml

# Define mapping rules for entries currently stuck in 'ai-dev-platforms'
# Key: item ID, Value: (new_category, new_subcategory)
MIGRATION_MAP = {
    # CAD / Modeling Tools -> Media & Creative Production
    "opencad-studio": ("media-and-creative-production", "cad-fabrication"),
    "beziermotion": ("media-and-creative-production", "cad-fabrication"),
    "chili3d":("media-and-creative-production", "cad-fabrication"),
    "cyclecad":("media-and-creative-production", "cad-fabrication"),
    
    # Diagramming, Docs, & Developer Utilities -> Developer or Productivity
    "mermify": ("developer-and-system-utilities", "developer-utilities"),
    "asciiflow": ("developer-and-system-utilities", "developer-utilities"),
    "quickref-me": ("developer-and-system-utilities", "frontend-dev-resources"),
    "algorithm-visualizer": ("developer-and-system-utilities", "developer-tools"),
    "python-tutor": ("online-learning-and-workforce-training", "programming-langauges"),
    "daily-stars-explorer":("developer-and-system-utilities", "developer-utilities"),
    "dsa-view-view":("developer-and-system-utilities", "developer-tools"),
    "codi-link":("developer-and-system-utilities", "developer-tools"),
    "frappe-playground":("developer-and-system-utilities", "developer-tools"),
    "forge":("developer-and-system-utilities", "developer-tools"),
    "pynote":("developer-and-system-utilities", "developer-tools"),
    "gitreverse":("developer-and-system-utilities", "developer-utilities"),
    "kroki":("developer-and-system-utilities", "developer-utilities"),
    "roadmaps-sh":("developer-and-system-utilities", "developer-tools"),
    "gitfut":("developer-and-system-utilities", "developer-utilities"),
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
    target_path = "_data/linkography.yaml"
    clean_ai_dev_platforms(target_path)