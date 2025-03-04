import random
from classes.item_manager import item_manager

# Monster name generation based on rarity
RARITY_MODIFIERS = {
    "common": {
        "prefixes": ["Weak", "Small", "Pathetic"],
        "suffixes": ["of the Forest", "of the Swamp"],
        "base_names": ["Goblin", "Slime", "Rat"],
        "health_range": (40, 60),
        "attack_range": (8, 12),
        "defense_range": (4, 6),
        "gold_range": (5, 15),
        "item_templates": [
            {"name": "Rusty Sword", "type": "weapon", "price": 200},
            {"name": "Cloth Armor", "type": "armor", "price": 150}
        ]
    },
    "rare": {
        "prefixes": ["Strong", "Large", "Fierce"],
        "suffixes": ["of the Mountains", "of the Caves"],
        "base_names": ["Orc", "Troll", "Wolf"],
        "health_range": (80, 120),
        "attack_range": (15, 25),
        "defense_range": (8, 12),
        "gold_range": (40, 60),
        "item_templates": [
            {"name": "Sturdy Shield", "type": "armor", "price": 500},
            {"name": "Iron Axe", "type": "weapon", "price": 400}
        ]
    },
    "epic": {
        "prefixes": ["Mighty", "Giant", "Terrifying"],
        "suffixes": ["of the Abyss", "of the Depths"],
        "base_names": ["Demon", "Elemental", "Giant"],
        "health_range": (400, 600),
        "attack_range": (30, 50),
        "defense_range": (20, 30),
        "gold_range": (300, 700),
        "item_templates": [
            {"name": "Demonic Wand", "type": "weapon", "price": 1200},
            {"name": "Crystal Armor", "type": "armor", "price": 1000}
        ]
    },
    "legendary": {
        "prefixes": ["Ancient", "Colossal", "Demonic"],
        "suffixes": ["of the Void", "of the Apocalypse"],
        "base_names": ["Dragon", "Phoenix", "Leviathan"],
        "health_range": (1000, 1500),
        "attack_range": (80, 120),
        "defense_range": (50, 70),
        "gold_range": (5000, 10000),
        "item_templates": [
            {"name": "Obsidian Tooth", "type": "weapon", "price": 5500},
            {"name": "Dragon Scale Armor", "type": "armor", "price": 4800}
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
    attack = random.randint(*modifiers.get("attack_range", (10, 20)))
    defense = random.randint(*modifiers.get("defense_range", (5, 10)))
    gold = random.randint(*modifiers.get("gold_range", (10, 50)))
    
    return health, attack, defense, gold

def generate_monster_rewards(rarity):
    """Generate rewards for a monster based on its rarity."""
    modifiers = RARITY_MODIFIERS.get(rarity, {})
    
    # Generate gold
    gold = random.randint(*modifiers.get("gold_range", (10, 50)))
    
    # Generate items
    item_templates = modifiers.get("item_templates", [])
    num_items = random.randint(1, 2)  # Randomly choose 1-2 items to drop
    items = []
    for _ in range(num_items):
        template = random.choice(item_templates)
        item = item_manager.generate_item(
            name=template["name"],
            rarity=rarity,
            price=template["price"],
            item_type=template["type"]
        )
        items.append(item)
    
    return {
        "gold": gold,
        "items": items
    }

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
    monster = {
        "name": generate_monster_name(base_rarity),
        "health": generate_monster_stats(base_rarity)[0],
        "attack": generate_monster_stats(base_rarity)[1],
        "defense": generate_monster_stats(base_rarity)[2],
        "rarity": base_rarity,
        "rewards": generate_monster_rewards(base_rarity)
    }
    
    return monster