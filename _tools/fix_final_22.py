import os
import re
import yaml

YAML_PATH = '../_data/linkography.yaml'

def fix_remaining():
    if not os.path.exists(YAML_PATH):
        print(f"[ERROR] Could not find YAML file at {YAML_PATH}")
        return

    with open(YAML_PATH, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    seen_ids = set()
    fixed_count = 0

    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            continue
            
        title = entry.get('title', f"Entry #{i+1}")
        
        # 1. Assign missing IDs
        if not entry.get('id'):
            base_id = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
            new_id = base_id
            counter = 1
            while new_id in seen_ids:
                counter += 1
                new_id = f"{base_id}-{counter}"
            entry['id'] = new_id
            fixed_count += 1
            print(f"[FIXED] Added missing ID '{new_id}' to entry #{i+1} ({title})")

        # 2. Resolve duplicate IDs
        curr_id = entry.get('id')
        if curr_id in seen_ids:
            base_id = curr_id
            counter = 2
            while f"{base_id}-{counter}" in seen_ids:
                counter += 1
            new_id = f"{base_id}-{counter}"
            entry['id'] = new_id
            print(f"[FIXED] Resolved duplicate ID '{curr_id}' -> '{new_id}'")
            
        seen_ids.add(entry['id'])

    with open(YAML_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True, width=1000)

    print(f"\n✨ Successfully fixed missing IDs for {fixed_count} entries and cleaned up identifier collisions!")

if __name__ == '__main__':
    fix_remaining()