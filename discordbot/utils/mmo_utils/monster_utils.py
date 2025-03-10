import random
from classes.item_manager import item_manager

# Monster name generation based on rarity
RARITY_MODIFIERS = {
    "common": {
        "prefixes": ["Weak", "Small", "Pathetic"],
        "suffixes": ["of the Forest", "of the Swamp"],
        "base_names": ["Goblin", "Slime"],
        "health_range": (40, 60),
        "attack_range": (8, 12),
        "armor_range": (4, 6),
        "gold_range": (5, 15),
        "item_templates": [
            {"name": "Rusty Sword", "type": "weapon"},
            {"name": "Cloth Armor", "type": "chest"},
            {"name": "Leather Boots", "type": "feet"},
            {"name": "Wooden Shield", "type": "shield"},
            {"name": "Health Potion", "type": "consumable"}
        ]
    },
    "rare": {
        "prefixes": ["Strong", "Large", "Fierce"],
        "suffixes": ["of the Mountains", "of the Caves"],
        "base_names": ["Orc", "Troll"],
        "health_range": (80, 120),
        "attack_range": (15, 25),
        "armor_range": (8, 12),
        "gold_range": (40, 60),
        "item_templates": [
            {"name": "Iron Axe", "type": "weapon"},
            {"name": "Chainmail Armor", "type": "chest"},
            {"name": "Steel Helmet", "type": "helm"},
            {"name": "Reinforced Shield", "type": "shield"},
            {"name": "Health Potion", "type": "consumable"}
        ]
    },
    "epic": {
        "prefixes": ["Mighty", "Giant", "Terrifying"],
        "suffixes": ["of the Abyss", "of the Depths"],
        "base_names": ["Demon", "Elemental"],
        "health_range": (400, 600),
        "attack_range": (30, 50),
        "armor_range": (20, 30),
        "gold_range": (300, 700),
        "item_templates": [
            {"name": "Demonic Wand", "type": "weapon"},
            {"name": "Crystal Armor", "type": "chest"},
            {"name": "Dragonbone Helm", "type": "helm"},
            {"name": "Tower Shield", "type": "shield"},
            {"name": "Health Potion", "type": "consumable"}
        ]
    },
    "legendary": {
        "prefixes": ["Ancient", "Colossal"],
        "suffixes": ["of the Void", "of the Apocalypse"],
        "base_names": ["Demon King" ],
        "health_range": (1000, 1500),
        "attack_range": (80, 120),
        "armor_range": (50, 70),
        "gold_range": (5000, 7000),
        "item_templates": [
            {"name": "Obsidian Tooth", "type": "weapon"},
            {"name": "Dragon Scale Armor", "type": "chest"},
            {"name": "Crown of the Ancients", "type": "helm"},
            {"name": "Aegis of Immortality", "type": "shield"},
            {"name": "Health Potion", "type": "consumable"}
        ]
    }
}

def generate_monster_name(rarity):
    """Generate a cool name for a monster based on its rarity."""
    modifiers = RARITY_MODIFIERS.get(rarity, {})
    prefix = random.choice(modifiers.get("prefixes", [""]))
    base_name = random.choice(modifiers.get("base_names", ["Monster"]))
    suffix = random.choice(modifiers.get("suffixes", [""]))

    name = f"{prefix} {base_name}" if prefix else base_name
    if suffix:
        name += f" {suffix}"
    
    return name.strip()

def generate_monster_stats(rarity):
    """Generate stats for a monster based on its rarity."""
    modifiers = RARITY_MODIFIERS.get(rarity, {})
    health = random.randint(*modifiers.get("health_range", (50, 100)))
    max_health = health
    attack = random.randint(*modifiers.get("attack_range", (10, 20)))
    armor = random.randint(*modifiers.get("armor_range", (5, 10)))
    gold = random.randint(*modifiers.get("gold_range", (10, 50)))
    
    return health, max_health, attack, armor, gold

def generate_monster_rewards(rarity):
    """Generate rewards for a monster based on its rarity."""
    modifiers = RARITY_MODIFIERS.get(rarity, {})
    
    # Generate gold
    gold = random.randint(*modifiers.get("gold_range", (10, 50)))
    
    # Generate items
    item_templates = modifiers.get("item_templates", [])
    items = []

    # Randomly choose 1-2 items to drop
    num_items = random.randint(1, 2)
    for _ in range(num_items):
        template = random.choice(item_templates)
        item = item_manager.generate_item(
            name=template["name"],
            rarity=rarity,
            item_type=template["type"]
        )
        items.append(item)
    
    # 10% chance to drop an additional potion
    if random.random() < 0.1:
        potion = item_manager.generate_item(
            name="Health Potion",
            rarity="common",
            item_type="consumable"
        )
        items.append(potion)
    
    return {
        "gold": gold,
        "items": items
    }

def get_monster_base_name(monster_name):
    """
    Extract the base name from a monster's full name.
    E.g., "Weak Goblin of the Forest" -> "Goblin"
    """
    # Split the name into words
    words = monster_name.split()
    
    # Get all possible base names from monster_utils
    from utils.mmo_utils.monster_utils import RARITY_MODIFIERS
    all_base_names = []
    for rarity in RARITY_MODIFIERS:
        all_base_names.extend(RARITY_MODIFIERS[rarity]["base_names"])
    
    # Find the first word that matches a base name
    for word in words:
        if word in all_base_names:
            return word
    
    # If no base name is found, return the middle word as a fallback
    if len(words) >= 3:
        return words[1]  # Middle word
    elif len(words) == 2:
        return words[1]  # Second word
    else:
        return words[0]  # Only word

def get_monster(difficulty="easy"):
    """Get a random monster with generated stats, name, and rewards based on difficulty."""
    # Map difficulty to base rarity
    DIFFICULTY_RARITY_MAP = {
        "easy": "common",
        "medium": "rare",
        "hard": "epic",
        "hardcore": "legendary"
    }
    
    # Get base rarity based on difficulty
    base_rarity = DIFFICULTY_RARITY_MAP.get(difficulty, "common")
    
    # 10% chance to increase rarity by one tier
    if random.random() < 0.1:
        rarity_tiers = ["common", "rare", "epic", "legendary"]
        current_index = rarity_tiers.index(base_rarity)
        if current_index < len(rarity_tiers) - 1:
            base_rarity = rarity_tiers[current_index + 1]
    
    # Generate monster based on rarity
    monster_stats = generate_monster_stats(base_rarity)
    monster = {
        "name": generate_monster_name(base_rarity),
        "NPC": True,
        "health": monster_stats[0],
        "max_health": monster_stats[1],
        "attack": monster_stats[2],
        "armor": monster_stats[3],
        "rarity": base_rarity,
        "rewards": generate_monster_rewards(base_rarity)
    }
    
    return monster