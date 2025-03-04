from discord.ext import commands
from database import get_player_data, update_player_data
import json

@commands.command()
async def inv(ctx):
    """Display the user's inventory."""
    player = get_player_data(ctx.author.id)
    if not player:
        await ctx.send("You are not registered as a player. (type !join to play)")
        return

    inventory = player["inventory"]
    if not inventory:
        await ctx.send("Your inventory is empty.")
        return

    # Format inventory for display
    inventory_list = "\n".join([f"{item['id']}. {item['name']} ({item['type'].title()}, {item['rarity'].title()})" for item in inventory])
    await ctx.send(f"**Your Inventory:**\n{inventory_list}")

@commands.command()
async def equip(ctx, item_id: int):
    """Equip an item from the user's inventory."""
    player = get_player_data(ctx.author.id)
    if not player:
        await ctx.send("You are not registered as a player.")
        return

    inventory = player["inventory"]
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
    equipped_items = player["equipped_items"]

    # Check if the item type is already equipped
    if item_to_equip["type"] in equipped_items:
        await ctx.send(f"You already have a {item_to_equip['type']} equipped.")
        return

    # Equip the item and update player stats
    if item_to_equip["type"] == "weapon":
        player["attack"] += item_to_equip.get("attack", 0)
    elif item_to_equip["type"] == "armor":
        player["armor"] += item_to_equip.get("armor", 0)

    equipped_items[item_to_equip["type"]] = item_to_equip
    update_player_data(ctx.author.id, equipped_items=equipped_items, attack=player["attack"], armor=player["armor"])

    await ctx.send(f"You equipped {item_to_equip['name']} ({item_to_equip['type'].title()}).")

@commands.command()
async def unequip(ctx, item_type: str):
    """Unequip an item."""
    player = get_player_data(ctx.author.id)
    if not player:
        await ctx.send("You are not registered as a player.")
        return

    equipped_items = player["equipped_items"]
    if item_type not in equipped_items:
        await ctx.send(f"You don't have a {item_type} equipped.")
        return

    # Unequip the item and update player stats
    unequipped_item = equipped_items.pop(item_type)

    if unequipped_item["type"] == "weapon":
        player["attack"] -= unequipped_item.get("attack", 0)
    elif unequipped_item["type"] == "armor":
        player["armor"] -= unequipped_item.get("armor", 0)

    update_player_data(ctx.author.id, equipped_items=equipped_items, attack=player["attack"], armor=player["armor"])

    await ctx.send(f"You unequipped {unequipped_item['name']} ({item_type.title()}).")

@commands.command()
async def stuff(ctx):
    """Display the user's equipped items."""
    player = get_player_data(ctx.author.id)
    if not player:
        await ctx.send("You are not registered as a player. (type !join)")
        return

    equipped_items = player["equipped_items"]
    if not equipped_items:
        await ctx.send("You have no items equipped.")
        return

    # Format equipped items for display
    equipped_list = "\n".join([f"{item['name']} ({item['type'].title()}, {item['rarity'].title()})" for item in equipped_items.values()])
    await ctx.send(f"**Your Equipped Items:**\n{equipped_list}")

@commands.command()
async def use(ctx, item_id: int):
    """Use a consumable item (e.g., health potion)."""
    player = get_player_data(ctx.author.id)
    if not player:
        await ctx.send("You are not registered as a player. (type !join)")
        return

    inventory = player["inventory"]
    if not inventory:
        await ctx.send("Your inventory is empty.")
        return

    # Find the item in the inventory
    item_to_use = None
    for item in inventory:
        if item["id"] == item_id:
            item_to_use = item
            break

    if not item_to_use:
        await ctx.send("Item not found in your inventory.")
        return

    if item_to_use["type"] != "consumable":
        await ctx.send("You can only use consumable items.")
        return

    # Apply the item's effect
    if "health_restore" in item_to_use:
        player["health"] = min(100, player["health"] + item_to_use["health_restore"])
        update_player_data(ctx.author.id, health=player["health"])
        await ctx.send(f"You used {item_to_use['name']} and restored {item_to_use['health_restore']} health.")
    else:
        await ctx.send("This item has no effect.")

    # Remove the item from the inventory
    inventory.remove(item_to_use)
    update_player_data(ctx.author.id, inventory=inventory)