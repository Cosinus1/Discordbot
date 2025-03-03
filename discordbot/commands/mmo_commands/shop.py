from discord.ext import commands
from database import get_user_data, update_user_data, get_user_inventory, update_user_inventory
from utils.mmo_utils.shop_utils import load_shop_items, get_item_by_id

@commands.command()
async def shop(ctx):
    """Display the items available in the shop."""
    items = load_shop_items()
    shop_list = "\n".join([f"{item['id']}. {item['name']} ({item['rarity'].title()}) - {item['price']} gold" for item in items])
    await ctx.send(f"**Shop Items:**\n{shop_list}")

@commands.command()
async def buy(ctx, item_id: int):
    """Buy an item from the shop."""
    user = get_user_data(ctx.author.id)
    if not user:
        await ctx.send("You are not registered in the database.")
        return

    item = get_item_by_id(item_id)
    if not item:
        await ctx.send("Item not found.")
        return

    if user["money"] < item["price"]:
        await ctx.send("You don't have enough gold to buy this item.")
        return

    # Deduct money and add item to user's inventory
    user["money"] -= item["price"]
    inventory = get_user_inventory(ctx.author.id)
    inventory.append(item)
    update_user_inventory(ctx.author.id, inventory)
    update_user_data(ctx.author.id, money=user["money"])

    await ctx.send(f"You bought a {item['name']} ({item['rarity'].title()}) for {item['price']} gold!")

@commands.command()
async def sell(ctx, item_id: int):
    """Sell an item from your inventory."""
    user = get_user_data(ctx.author.id)
    if not user:
        await ctx.send("You are not registered in the database.")
        return

    inventory = get_user_inventory(ctx.author.id)
    if not inventory:
        await ctx.send("Your inventory is empty.")
        return

    # Find the item in the user's inventory
    item_to_sell = None
    for item in inventory:
        if item["id"] == item_id:
            item_to_sell = item
            break

    if not item_to_sell:
        await ctx.send("Item not found in your inventory.")
        return

    # Add money and remove item from inventory
    sell_price = item_to_sell["price"] // 2  # Sell for half the price
    user["money"] += sell_price
    inventory.remove(item_to_sell)
    update_user_inventory(ctx.author.id, inventory)
    update_user_data(ctx.author.id, money=user["money"])

    await ctx.send(f"You sold a {item_to_sell['name']} ({item_to_sell['rarity'].title()}) for {sell_price} gold!")