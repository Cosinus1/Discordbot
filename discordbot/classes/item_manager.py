import json
import random
from utils.mmo_utils.shop_utils import load_shop_items
class ItemManager:
    def __init__(self, items_file="data/mmo/items.json"):
        self.items_file = items_file
        self.items = self._load_items()
        self.shop_items = load_shop_items()
        self.next_id = self._get_max_id() + 1

    def _load_items(self):
        """Load items from the JSON file."""
        try:
            with open(self.items_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def _get_max_id(self):
        """Get the highest ID from the existing items."""
        return max((item.get("id", 0) for item in self.items), default=0)

    def save_items(self):
        """Save items to the JSON file."""
        with open(self.items_file, "w") as file:
            json.dump(self.items, file, indent=4)

    def generate_item(self, name, rarity, price, item_type):
        """Generate a new item with a unique ID."""
        item = {
            "id": self.next_id,
            "name": name,
            "rarity": rarity,
            "price": price,
            "type": item_type
        }
        self.items.append(item)
        self.next_id += 1
        self.save_items()
        return item

    def get_item_by_id(self, item_id):
        """Get an item by its ID."""
        for item in self.items:
            if item["id"] == item_id:
                return item
        return None

    def get_item_by_name(self, item_name):
        """Get an item by its name."""
        for item in self.items:
            if item["name"].lower() == item_name.lower():
                return item
        return None

    def generate_monster_reward_items(self, rarity):
        """Generate reward items for a monster based on its rarity."""
        # Define possible items for each rarity
        ITEM_TEMPLATES = {
            "common": [
                {"name": "Rusty Sword", "type": "weapon", "price": 5},
                {"name": "Cloth Armor", "type": "armor", "price": 5}
            ],
            "rare": [
                {"name": "Sturdy Shield", "type": "armor", "price": 50},
                {"name": "Iron Axe", "type": "weapon", "price": 50}
            ],
            "epic": [
                {"name": "Demonic Wand", "type": "weapon", "price": 200},
                {"name": "Crystal Armor", "type": "armor", "price": 200}
            ],
            "legendary": [
                {"name": "Obsidian Tooth", "type": "weapon", "price": 500},
                {"name": "Dragon Scale Armor", "type": "armor", "price": 500}
            ]
        }

        # Randomly choose 1-2 items to drop
        templates = ITEM_TEMPLATES.get(rarity, [])
        num_items = random.randint(1, 2)
        chosen_templates = random.sample(templates, min(num_items, len(templates)))

        # Generate items with unique IDs
        items = []
        for template in chosen_templates:
            item = self.generate_item(
                name=template["name"],
                rarity=rarity,
                price=template["price"],
                item_type=template["type"]
            )
            items.append(item)

        return items

# Singleton instance of ItemManager
item_manager = ItemManager()