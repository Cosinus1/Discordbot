import random
from classes.item_manager import item_manager

class Shop_manager:
    def __init__(self):
        self.items = []
        self.potions = []
        self.refresh_shop()

    def refresh_shop(self):
        """Refresh the shop's items."""
        self.items = []
        self.potions = []

        # Add at least one item of each rarity
        rarities = ["common", "rare", "epic", "legendary"]
        for rarity in rarities:
            self.items.append(self.generate_shop_item(rarity))

        # Add unlimited potions
        self.potions.append(self.generate_potion())

    def generate_shop_item(self, rarity):
        """Generate a shop item of the specified rarity."""
        item_templates = {
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
        template = random.choice(item_templates[rarity])
        return item_manager.generate_item(template["name"], rarity, template["price"], template["type"])

    def generate_potion(self):
        """Generate a potion."""
        return item_manager.generate_item("Health Potion", "common", 10, "consumable")

    def replace_sold_item(self, item_id):
        """Replace a sold item with a new one of the same rarity."""
        sold_item = next((item for item in self.items if item["id"] == item_id), None)
        if sold_item:
            rarity = sold_item["rarity"]
            self.items.remove(sold_item)
            self.items.append(self.generate_shop_item(rarity))

# Singleton instance of Shop
shop_manager = Shop_manager()