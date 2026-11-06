import json
import yaml
import os

def rebalance_linkography():
    # Define paths relative to the project root
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    yaml_path = os.path.join(root_dir, "_data", "linkography.yaml")
    json_path = os.path.join(root_dir, "_data", "category_mapping.json")
    output_path = os.path.join(root_dir, "_data", "linkography_clean.yaml")

    # Load original YAML from _data/
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Load Claude's JSON mapping
    with open(json_path, "r", encoding="utf-8") as f:
        mappings = json.load(f)

    updated_count = 0

    # Apply updates and normalize category slugs on the fly
    for entry in data:
        entry_id = entry.get("id")
        if entry_id in mappings:
            category = mappings[entry_id]["category"]
            
            # Catch the old AI slug and map it cleanly to the new one
            if category == "local-self-hosted-ai-agents":
                category = "ai-agents"
                
            entry["category"] = category
            entry["subcategory"] = mappings[entry_id]["subcategory"]
            updated_count += 1

    # Write cleaned YAML back to _data/
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True, default_flow_style=False)

    print(f"Successfully updated {updated_count} records and saved to {output_path}!")

if __name__ == "__main__":
    rebalance_linkography()