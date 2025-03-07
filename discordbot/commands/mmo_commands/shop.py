from discord.ext import commands
from classes.shop_manager import shop_manager
from database import get_player_data, update_player_data, get_user_data, update_user_data
from classes.item_manager import item_manager
import threading

lock = threading.Lock()

@commands.command()
async def shop(ctx):
    """Display the items available in the shop."""
    with lock:
        items = shop_manager.items + shop_manager.potions
        shop_list = "\n".join([f"{item['id']}. {item['name']} ({item['rarity'].title()}) - {item['price']} gold" for item in items])
        await ctx.send(f"**Shop Items:**\n{shop_list}")

@commands.command()
async def buy(ctx, item_reference: str):
    """Buy an item from the shop by name or ID."""
    with lock:
        player = get_player_data(ctx.author.id)
        if not player:
            await ctx.send("You are not registered as a player. (type !join to play)")
            return

        # Try to find the item by ID or name
        item = None
        if item_reference.isdigit():
            item_id = int(item_reference)
            item = next((item for item in shop_manager.items + shop_manager.potions if item["id"] == item_id), None)
        else:
            item = next((item for item in shop_manager.items + shop_manager.potions if item["name"].lower() == item_reference.lower()), None)

        if not item:
            await ctx.send("Item not found.")
            return
        
        user = get_user_data(ctx.author.id)
        if not user:
            await ctx.send("You are not registered in the database")
            return
        
        if user["money"] < item["price"]:
            await ctx.send("You don't have enough gold to buy this item.")
            return

        # Deduct money and add item to inventory
        user["money"] -= item["price"]
        player["inventory"].append(item)
        update_player_data(ctx.author.id, inventory=player["inventory"])
        update_user_data(ctx.author.id, money=user["money"])

        # Handle potions (unlimited stock)
        if item["type"] == "consumable":
            await ctx.send(f"You bought a {item['name']} (ID: {item['id']}, {item['rarity'].title()}) for {item['price']} gold!")
        else:
            # Replace sold item with a new one of the same rarity
            shop_manager.replace_sold_item(item["id"])
            await ctx.send(f"You bought a {item['name']} (ID: {item['id']}, {item['rarity'].title()}) for {item['price']} gold!")

    
@commands.command()
async def sell(ctx, item_reference: str):
    """Sell an item from your inventory by name or display number."""
    with lock:
        user = get_user_data(ctx.author.id)
        if not user:
            await ctx.send("You are not registered in the database")
            return
        player = get_player_data(ctx.author.id)
        if not player:
            await ctx.send("You are not registered as a player. (type !join to play)")
            return

        inventory = player["inventory"]
        if not inventory:
            await ctx.send("Your inventory is empty.")
            return

        # Try to find the item by display number or name
        item_to_sell = None
        if item_reference.isdigit():
            idx = int(item_reference) - 1
            if 0 <= idx < len(inventory):
                item_to_sell = inventory[idx]
        else:
            for item in inventory:
                if item["name"].lower() == item_reference.lower():
                    item_to_sell = item
                    break

        if not item_to_sell:
            await ctx.send("Item not found in your inventory.")
            return

        # Add money and remove item from inventory
        sell_price = item_to_sell["price"] // 2  # Sell for half the price
        user["money"] += sell_price
        inventory.remove(item_to_sell)
        update_player_data(ctx.author.id, inventory=inventory)
        update_user_data(ctx.author.id, money=user["money"])
        item_manager.remove_item(item_to_sell["id"])

        await ctx.send(f"You sold a {item_to_sell['name']} (ID: {item_to_sell['id']}, {item_to_sell['rarity'].title()}) for {sell_price} gold!")
