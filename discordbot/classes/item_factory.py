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
        stats = {}
        stat_budget = STAT_BUDGET.get(rarity, 0)
        stat_constraints = STAT_CONSTRAINTS.get(item_type, {})

        # Filter out powerful stats for non-epic/legendary items
        if rarity not in ["epic", "legendary"]:
            stat_constraints = {
                stat: constraints for stat, constraints in stat_constraints.items()
                if stat not in ["lifesteal", "parry_chance", "stunt_chance"]
            }

        # Distribute the stat budget randomly
        remaining_budget = stat_budget
        available_stats = list(stat_constraints.keys())

        while remaining_budget > 0 and available_stats:
            stat = random.choice(available_stats)
            min_val = stat_constraints[stat]["min"]
            max_val = stat_constraints[stat]["max"]

            # Assign a random value within constraints, but don't exceed remaining budget
            value = random.uniform(min_val, min(max_val, remaining_budget))
            stats[stat] = round(value, 2)
            remaining_budget -= value

            # Remove the stat if it has reached its maximum value
            if stats[stat] >= max_val:
                available_stats.remove(stat)

        return stats