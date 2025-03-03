import json
from .item_utils import generate_item_name

def load_shop_items():
    """Load shop items from the JSON file and generate their names."""
    with open("data/mmo/shop_items.json", "r") as file:
        items = json.load(file)
    
    # Generate cool names for each item
    for item in items:
        item["name"] = generate_item_name(item["base_name"], item["rarity"])
    
    return items

def get_item_by_id(item_id):
    """Get an item by its ID."""
    items = load_shop_items()
    for item in items:
        if item["id"] == item_id:
            return item
    return None