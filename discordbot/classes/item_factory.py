import random
from utils.mmo_utils.item_utils import RARITY_MODIFIERS, STAT_CONSTRAINTS, STAT_BUDGET, PRICE_MULTIPLIER

class ItemFactory:
    """Factory class to create different types of items."""
    @staticmethod
    def create_equipment(name, rarity, item_type):
        """Create an equipment item with stats."""
        stats = ItemFactory._generate_stats(item_type, rarity)
        price = STAT_BUDGET[rarity] * PRICE_MULTIPLIER[rarity]
        item_name = ItemFactory._generate_item_name(name, rarity)

        return {
            "id": None,  # ID will be assigned by ItemManager
            "name": item_name,
            "rarity": rarity,
            "price": price,
            "type": item_type,
            "stats": stats
        }

    @staticmethod
    def create_potion(name, effect):
        """Create a consumable potion."""
        return {
            "id": None,  # ID will be assigned by ItemManager
            "name": name,
            "price": 50,  # Fixed price for potions
            "type": "consumable",
            "effect": effect
        }

    @staticmethod
    def _generate_item_name(base_name, rarity):
        """Generate a cool name for an item based on its rarity."""
        modifiers = RARITY_MODIFIERS.get(rarity, {})
        prefix = random.choice(modifiers.get("prefixes", [""]))
        suffix = random.choice(modifiers.get("suffixes", [""]))

        name = f"{prefix} {base_name}" if prefix else base_name
        if suffix:
            name += f" {suffix}"

        return name.strip()

    @staticmethod
    def _generate_stats(item_type, rarity):
        """Generate random stats for an item based on its type and rarity."""
        # Get the base stats from STAT_CONSTRAINTS based on rarity and item type
        base_stats = STAT_CONSTRAINTS.get(rarity, {}).get(item_type, {})
        VARIANCE_MODIFIER = 0
        # Create a copy of the base stats to work with
        stats = {}
        
        # Apply some randomness to each stat
        for stat_name, base_value in base_stats.items():
            # For percentage-based stats (those with values < 1)
            if isinstance(base_value, float) and base_value < 1:
                # Apply smaller variance for percentage values
                variance = base_value * VARIANCE_MODIFIER
                min_value = max(0, base_value - variance)
                max_value = base_value + variance
                stats[stat_name] = round(random.uniform(min_value, max_value), 2)
            # For integer-based stats
            else:
                # Apply standard variance
                variance = int(base_value * 0.2)  # 20% variance
                min_value = max(1, base_value - variance)
                max_value = base_value + variance
                stats[stat_name] = random.randint(min_value, max_value)
        
        return stats