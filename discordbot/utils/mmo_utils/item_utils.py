# Prefixes and suffixes for item names based on rarity
RARITY_MODIFIERS = {
    "common": {
        "prefixes": ["Rusty", "Old", "Basic", "Worn", "Simple"],
        "suffixes": ["of the Beginner", "of Mediocrity", "of the Commoner", "of Simplicity"]
    },
    "rare": {
        "prefixes": ["Sharp", "Sturdy", "Polished", "Reinforced", "Reliable"],
        "suffixes": ["of the Apprentice", "of Precision", "of the Journeyman", "of Skill"]
    },
    "epic": {
        "prefixes": ["Mighty", "Enchanted", "Gleaming", "Radiant", "Ethereal"],
        "suffixes": ["of the Master", "of Power", "of the Adept", "of Brilliance"]
    },
    "legendary": {
        "prefixes": ["Divine", "Eternal", "Legendary", "Celestial", "Immortal"],
        "suffixes": ["of the Gods", "of Immortality", "of the Ancients", "of Eternity"]
    }
}

# Stat constraints for each item type
STAT_CONSTRAINTS = {
    "weapon": {
        "attack": {"min": 5, "max": 50},
        "critical_chance": {"min": 0.0, "max": 0.2},
        "lifesteal": {"min": 0.0, "max": 0.1},  # Only for epic and legendary
        "armor_penetration": {"min": 0.0, "max": 0.3},
        "stunt_chance": {"min": 0.0, "max": 0.1}  # Only for epic and legendary
    },
    "shield": {
        "armor": {"min": 10, "max": 60},
        "stunt_chance": {"min": 0.0, "max": 0.2},  # Only for epic and legendary
        "health": {"min": 0, "max": 50},
        "parry_chance": {"min": 0.0, "max": 0.15}  # Only for epic and legendary
    },
    "helm": {
        "armor": {"min": 5, "max": 30},
        "health": {"min": 10, "max": 50},
        "critical_chance": {"min": 0.0, "max": 0.1}
    },
    "chest": {
        "armor": {"min": 10, "max": 40},
        "health": {"min": 20, "max": 70},
        "critical_chance": {"min": 0.0, "max": 0.1}
    },
    "legs": {
        "armor": {"min": 8, "max": 35},
        "health": {"min": 15, "max": 60},
        "critical_chance": {"min": 0.0, "max": 0.1}
    },
    "feet": {
        "armor": {"min": 5, "max": 25},
        "health": {"min": 10, "max": 40},
        "critical_chance": {"min": 0.0, "max": 0.1}
    }
}

# Stat budget based on rarity
STAT_BUDGET = {
    "common": 50,
    "rare": 80,
    "epic": 120,
    "legendary": 200
}

# Base price multiplier based on rarity
PRICE_MULTIPLIER = {
    "common": 10,
    "rare": 50,
    "epic": 100,
    "legendary": 500
}

# Item templates for the shop
ITEM_TEMPLATES = {
    "common": [
        {"name": "Rusty Sword", "type": "weapon"},
        {"name": "Cloth Armor", "type": "chest"},
        {"name": "Leather Boots", "type": "feet"},
        {"name": "Wooden Shield", "type": "shield"}
    ],
    "rare": [
        {"name": "Iron Axe", "type": "weapon"},
        {"name": "Chainmail Armor", "type": "chest"},
        {"name": "Steel Helmet", "type": "helm"},
        {"name": "Reinforced Shield", "type": "shield"}
    ],
    "epic": [
        {"name": "Demonic Wand", "type": "weapon"},
        {"name": "Crystal Armor", "type": "chest"},
        {"name": "Dragonbone Helm", "type": "helm"},
        {"name": "Tower Shield", "type": "shield"}
    ],
    "legendary": [
        {"name": "Obsidian Tooth", "type": "weapon"},
        {"name": "Dragon Scale Armor", "type": "chest"},
        {"name": "Crown of the Ancients", "type": "helm"},
        {"name": "Aegis of Immortality", "type": "shield"}
    ]
}