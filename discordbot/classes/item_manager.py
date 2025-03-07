import json
import threading
from .item_factory import ItemFactory

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

    def generate_item(self, name, rarity=None, item_type=None, effect=None):
        """Generate a new item or potion with a unique ID."""
        with self._lock:
            if self.available_ids:
                item_id = self.available_ids.pop()
            else:
                item_id = self.next_id
                self.next_id += 1

            # Use ItemFactory to create the item
            if item_type == "consumable":
                item = ItemFactory.create_potion(name, effect)
            else:
                item = ItemFactory.create_equipment(name, rarity, item_type)

            # Assign ID and save the item
            item["id"] = item_id
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