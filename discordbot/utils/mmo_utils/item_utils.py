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

# Stat for each item type
item_stats =  {
    "common": {
        "weapon": {"attack": 5},
        "shield": {"armor": 3},
        "helm": {"armor": 2, "health": 10},
        "chest": {"armor": 4, "health": 15},
        "legs": {"armor": 3, "health": 10},
        "feet": {"armor": 1, "health": 5}
    },
    "rare": {
        "weapon": {"attack": 10, "critical_chance": 0.05},
        "shield": {"armor": 6, "health": 20},
        "helm": {"armor": 4, "health": 25},
        "chest": {"armor": 8, "health": 30},
        "legs": {"armor": 6, "health": 20},
        "feet": {"armor": 3, "health": 15}
    },
    "epic": {
        "weapon": {"attack": 18, "critical_chance": 0.1, "lifesteal": 0.05},
        "shield": {"armor": 12, "health": 40, "stunt_chance": 0.08},
        "helm": {"armor": 8, "health": 45, "critical_chance": 0.03},
        "chest": {"armor": 15, "health": 60, "critical_chance": 0.03},
        "legs": {"armor": 10, "health": 40},
        "feet": {"armor": 6, "health": 30}
    },
    "legendary": {
        "weapon": {"attack": 30, "critical_chance": 0.15, "lifesteal": 0.1, "armor_penetration": 0.2},
        "shield": {"armor": 20, "health": 80, "stunt_chance": 0.15, "parry_chance": 0.1},
        "helm": {"armor": 15, "health": 70, "critical_chance": 0.05},
        "chest": {"armor": 25, "health": 100, "critical_chance": 0.05},
        "legs": {"armor": 18, "health": 60},
        "feet": {"armor": 12, "health": 50}
    }
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