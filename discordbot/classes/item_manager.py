import json
import random
import threading
from utils.mmo_utils.items_utils import RARITY_MODIFIERS, STAT_CONSTRAINTS, STAT_BUDGET, PRICE_MULTIPLIER

class ItemManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, items_file="data/mmo/items.json"):
        if not hasattr(self, 'initialized'):
            self.items_file = items_file
            self.items = self._load_items()
            self.available_ids = set()
            self.next_id = self._get_max_id() + 1
            self.initialized = True

    def _load_items(self):
        """Load items from the JSON file."""
        try:
            with open(self.items_file, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading items: {e}")
            return []

    def _get_max_id(self):
        """Get the highest ID from the existing items."""
        return max((item.get("id", 0) for item in self.items), default=0)

    def save_items(self):
        """Save items to the JSON file."""
        try:
            with open(self.items_file, "w") as file:
                json.dump(self.items, file, indent=4)
        except IOError as e:
            print(f"Error saving items: {e}")

    def generate_item_name(self, base_name, rarity):
        """Generate a cool name for an item based on its rarity."""
        modifiers = RARITY_MODIFIERS.get(rarity, {})
        prefix = random.choice(modifiers.get("prefixes", [""]))
        suffix = random.choice(modifiers.get("suffixes", [""]))

        name = f"{prefix} {base_name}" if prefix else base_name
        if suffix:
            name += f" {suffix}"

        return name.strip()

    def _generate_stats(self, item_type, rarity):
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

    def generate_item(self, name, rarity, item_type):
        """Generate a new item with a unique ID and random stats."""
        with self._lock:
            if self.available_ids:
                item_id = self.available_ids.pop()
            else:
                item_id = self.next_id
                self.next_id += 1

            # Generate stats for the item
            stats = self._generate_stats(item_type, rarity)

            # Calculate price based on rarity
            price = STAT_BUDGET[rarity] * PRICE_MULTIPLIER[rarity]

            # Generate item name with modifiers
            item_name = self.generate_item_name(name, rarity)

            item = {
                "id": item_id,
                "name": item_name,
                "rarity": rarity,
                "price": price,
                "type": item_type,
                "stats": stats
            }
            self.items.append(item)
            self.save_items()
            return item

    def remove_item(self, item_id):
        """Remove an item and free its ID for reuse."""
        with self._lock:
            item = next((item for item in self.items if item["id"] == item_id), None)
            if item:
                self.items.remove(item)
                self.available_ids.add(item_id)
                self.save_items()

    def get_item_by_id(self, item_id):
        """Get an item by its ID."""
        return next((item for item in self.items if item["id"] == item_id), None)

    def get_item_by_name(self, item_name):
        """Get an item by its name."""
        return next((item for item in self.items if item["name"].lower() == item_name.lower()), None)

# Singleton instance of ItemManager
item_manager = ItemManager()