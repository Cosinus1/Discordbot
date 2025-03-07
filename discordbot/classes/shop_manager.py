import random
from classes.item_manager import item_manager
from utils.mmo_utils.item_utils import ITEM_TEMPLATES
import threading

class ShopManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.items = []
            self.potions = []
            self.refresh_shop()
            self.initialized = True

    def refresh_shop(self):
        """Refresh the shop's items."""
        with self._lock:
            for item in self.items:
                item_manager.remove_item(item["id"])
            self.items = []
            # Add at least one item of each rarity
            rarities = ["common", "rare", "epic", "legendary"]
            for rarity in rarities:
                self.items.append(self.generate_shop_item(rarity))
            # Generate unlimited stack of potions
            for potion in self.potions:
                item_manager.remove_item(potion["id"])
            self.potions = []
            self.potions.append(self.generate_potion())

    def generate_shop_item(self, rarity):
        """Generate a shop item of the specified rarity."""
        template = random.choice(ITEM_TEMPLATES[rarity])
        return item_manager.generate_item(template["name"], rarity, template["type"])

    def generate_potion(self):
        """Generate a potion."""
        return item_manager.generate_item("Health Potion", "common", "consumable")

    def replace_sold_item(self, item_id):
        """Replace a sold item with a new one of the same rarity."""
        with self._lock:
            sold_item = next((item for item in self.items if item["id"] == item_id), None)
            if sold_item:
                rarity = sold_item["rarity"]
                self.items.remove(sold_item)
                self.items.append(self.generate_shop_item(rarity))

# Singleton instance of Shop
shop_manager = ShopManager()