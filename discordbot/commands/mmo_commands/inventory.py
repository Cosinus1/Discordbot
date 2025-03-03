from discord.ext import commands
from database import get_user_inventory, get_user_equipped_items, update_user_equipped_items
import json

@commands.command()
async def inv(ctx):
    """Display the user's inventory."""
    inventory = get_user_inventory(ctx.author.id)
    if not inventory:
        await ctx.send("Your inventory is empty.")
        return

    # Format inventory for display
    inventory_list = "\n".join([f"{item['id']}. {item['name']} ({item['type'].title()}, {item['rarity'].title()})" for item in inventory])
    await ctx.send(f"**Your Inventory:**\n{inventory_list}")

@commands.command()
async def equip(ctx, item_id: int):
    """Equip an item from the user's inventory."""
    inventory = get_user_inventory(ctx.author.id)
    if not inventory:
        await ctx.send("Your inventory is empty.")
        return

    # Find the item in the inventory
    item_to_equip = None
    for item in inventory:
        if item["id"] == item_id:
            item_to_equip = item
            break

    if not item_to_equip:
        await ctx.send("Item not found in your inventory.")
        return

    # Get currently equipped items
    equipped_items = get_user_equipped_items(ctx.author.id)

    # Check if the item type is already equipped
    if item_to_equip["type"] in equipped_items:
        await ctx.send(f"You already have a {item_to_equip['type']} equipped.")
        return

    # Equip the item
    equipped_items[item_to_equip["type"]] = item_to_equip
    update_user_equipped_items(ctx.author.id, equipped_items)

    await ctx.send(f"You equipped {item_to_equip['name']} ({item_to_equip['type'].title()}).")

@commands.command()
async def unequip(ctx, item_type: str):
    """Unequip an item."""
    equipped_items = get_user_equipped_items(ctx.author.id)
    if item_type not in equipped_items:
        await ctx.send(f"You don't have a {item_type} equipped.")
        return

    # Unequip the item
    unequipped_item = equipped_items.pop(item_type)
    update_user_equipped_items(ctx.author.id, equipped_items)

    await ctx.send(f"You unequipped {unequipped_item['name']} ({item_type.title()}).")

@commands.command()
async def stuff(ctx):
    """Display the user's equipped items."""
    equipped_items = get_user_equipped_items(ctx.author.id)
    if not equipped_items:
        await ctx.send("You have no items equipped.")
        return

    # Format equipped items for display
    equipped_list = "\n".join([f"{item['name']} ({item['type'].title()}, {item['rarity'].title()})" for item in equipped_items.values()])
    await ctx.send(f"**Your Equipped Items:**\n{equipped_list}")