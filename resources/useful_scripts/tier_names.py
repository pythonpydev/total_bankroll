import json

# Define the tier mapping
tier_map = {
    "1. PREMIUM (MAGNUM)": "1 (Elite)",
    "2. PREMIUM (Top Rundowns/Pairs)": "2 (Premium)",
    "3. SPECULATIVE": "3 (Strong)",
    "4. MARGINAL": "4 (Playable)",
    "5. TRASH / AVOID": "5 (Trash/Marginal)"
}

# Load the JSON file
with open('hand_strength_all.json', 'r') as f:
    data = json.load(f)

# Process each hand and update the tier
for item in data:
    current_tier = item.get('tier')
    if current_tier in tier_map:
        item['tier'] = tier_map[current_tier]

# Save the modified JSON to a new file
with open('modified_hand_strength_all.json', 'w') as f:
    json.dump(data, f, indent=4)

print("JSON file modified and saved to 'modified_hand_strength_all.json'.")
