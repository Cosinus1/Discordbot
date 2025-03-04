from discord.ext import commands
from classes.shop_manager import shop_manager
from database import get_player_data, update_player_data, get_user_data, update_user_data

@commands.command()
async def shop(ctx):
    """Display the items available in the shop."""
    items = shop_manager.items + shop_manager.potions
    shop_list = "\n".join([f"{item['id']}. {item['name']} ({item['rarity'].title()}) - {item['price']} gold" for item in items])
    await ctx.send(f"**Shop Items:**\n{shop_list}")

@commands.command()
async def buy(ctx, item_reference: str):
    """Buy an item from the shop by name or ID."""
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
    update_user_data(ctx.author.id, money=player["money"])

    # Handle potions (unlimited stock)
    if item["type"] == "consumable":
        await ctx.send(f"You bought a {item['name']} (ID: {item['id']}, {item['rarity'].title()}) for {item['price']} gold!")
    else:
        # Replace sold item with a new one of the same rarity
        shop_manager.replace_sold_item(item["id"])
        await ctx.send(f"You bought a {item['name']} (ID: {item['id']}, {item['rarity'].title()}) for {item['price']} gold!")