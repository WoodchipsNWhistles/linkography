import os
import yaml

# Define mapping rules for items that need category corrections
# Key: item ID, Value: new category (and optional subcategory override)
TAXONOMY_FIXES = {
    "mxtoolbox": {
        "category": "osint-and-reconnaissance",
        "subcategory": "email-diagnostics"
    },
    "mail-tester": {
        "category": "osint-and-reconnaissance",
        "subcategory": "email-diagnostics"
    },
    "revealer": {
        "category": "osint-and-reconnaissance",
        "subcategory": "osint-frameworks"
    },
    "fingerprint-to": {
        "category": "osint-and-reconnaissance",
        "subcategory": "privacy-auditing"
    },
    "bluehood": {
        "category": "osint-and-reconnaissance",
        "subcategory": "surveillance-awareness"
    },
    "rosint-plus": {
        "category": "osint-and-reconnaissance",
        "subcategory": "osint-frameworks"
    }
}

def fix_linkography(file_path):
    if not os.path.exists(file_path):
        print(f"[-] Error: Could not find {file_path}")
        return

    print(f"[*] Loading linkography from {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        entries = yaml.safe_load(f) or []

    fixed_count = 0
    for entry in entries:
        item_id = entry.get("id")
        
        # Apply specific ID-based fixes
        if item_id in TAXONOMY_FIXES:
            fix = TAXONOMY_FIXES[item_id]
            old_cat = entry.get("category")
            entry["category"] = fix["category"]
            if "subcategory" in fix:
                entry["subcategory"] = fix["subcategory"]
            print(f"[+] Fixed '{entry.get('title')} ({item_id})': {old_cat} -> {fix['category']}")
            fixed_count += 1

        # Fallback check: catch any stray items with osint tags in developer tools
        elif entry.get("category") == "developer-and-system-utilities":
            tags = entry.get("tags", [])
            if any(t in tags for t in ["osint", "reconnaissance", "email-intelligence", "bluetooth-recon"]):
                old_cat = entry.get("category")
                entry["category"] = "osint-and-reconnaissance"
                print(f"[+] Heuristic Fix '{entry.get('title')}': {old_cat} -> osint-and-reconnaissance")
                fixed_count += 1

    # Write back clean YAML with nice formatting
    print(f"[*] Saving updated linkography ({fixed_count} entries modified)...")
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(entries, f, sort_keys=False, allow_unicode=True, width=100)

    print("[✔] Taxonomy fix complete! Run your Eleventy build to verify.")

if __name__ == "__main__":
    target_path = "_data/linkography.yaml"
    fix_linkography(target_path)