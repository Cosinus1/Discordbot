import random

# Prefixes and suffixes for item names based on rarity
RARITY_MODIFIERS = {
    "common": {
        "prefixes": ["Rusty", "Old", "Basic"],
        "suffixes": ["of the Beginner", "of Mediocrity"]
    },
    "rare": {
        "prefixes": ["Sharp", "Sturdy", "Polished"],
        "suffixes": ["of the Apprentice", "of Precision"]
    },
    "epic": {
        "prefixes": ["Mighty", "Enchanted", "Gleaming"],
        "suffixes": ["of the Master", "of Power"]
    },
    "legendary": {
        "prefixes": ["Divine", "Eternal", "Legendary"],
        "suffixes": ["of the Gods", "of Immortality"]
    }
}

def generate_item_name(base_name, rarity):
    """Generate a cool name for an item based on its rarity."""
    modifiers = RARITY_MODIFIERS.get(rarity, {})
    prefix = random.choice(modifiers.get("prefixes", [""]))
    suffix = random.choice(modifiers.get("suffixes", [""]))

    name = f"{prefix} {base_name}" if prefix else base_name
    if suffix:
        name += f" {suffix}"
    
    return name.strip()