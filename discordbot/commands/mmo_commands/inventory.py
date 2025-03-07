from discord.ext import commands
from database import get_player_data, update_player_data,increment_player_stat
from classes.item_manager import item_manager
import threading

lock = threading.Lock()

@commands.command()
async def inv(ctx):
    """Display the user's inventory."""
    with lock:
        player = get_player_data(ctx.author.id)
        if not player:
            await ctx.send("You are not registered as a player. (type !join to play)")
            return

        inventory = player["inventory"]
        if not inventory:
            await ctx.send("Your inventory is empty.")
            return

        # Group potions by name and count them
        potion_counts = {}
        equipment_items = []

        for item in inventory:
            if item["type"] == "consumable":
                potion_name = item["name"]
                if potion_name in potion_counts:
                    potion_counts[potion_name] += 1
                else:
                    potion_counts[potion_name] = 1
            else:
                equipment_items.append(item)

        # Format potions for display
        potion_list = []
        for potion_name, count in potion_counts.items():
            potion_list.append(f"  - **{potion_name}:** {count}")

        # Format equipment for display
        equipment_list = []
        for idx, item in enumerate(equipment_items):
            item_info = (
                f"**{idx + 1}. {item['name']}**\n"
                f"  - **ID:** {item['id']}\n"
                f"  - **Type:** {item['type'].title()}\n"
                f"  - **Rarity:** {item['rarity'].title()}\n"
                f"  - **Price:** {item['price']} gold\n"
            )
            # Add stats if they exist
            if "stats" in item:
                item_info += "  - **Stats:**\n"
                for stat, value in item["stats"].items():
                    item_info += f"    - **{stat.replace('_', ' ').title()}:** {value}\n"
            equipment_list.append(item_info)

        # Combine potions and equipment into a single message
        inventory_message = "**Your Inventory:**\n\n"

        if potion_list:
            inventory_message += "**Potions:**\n" + "\n".join(potion_list) + "\n\n"

        if equipment_list:
            inventory_message += "**Equipment:**\n" + "\n".join(equipment_list)

        # Send the formatted inventory
        await ctx.send(inventory_message)

@commands.command()
async def stats(ctx):
    """Display the player's health, attack, and other stats."""
    player = get_player_data(ctx.author.id)
    if not player:
        await ctx.send("You are not registered as a player. (type `!join` to play)")
        return

    # Fetch player stats
    health = player.get("health", 0)
    attack = player.get("attack", 0)
    stats = player.get("stats", 0)

    # Format the stats for display
    stats_message = (
        f"**{ctx.author.display_name}'s Stats:**\n"
        f"❤️ **Health:** {health}\n"
        f"⚔️ **Attack:** {attack}\n"
    )
    if stats:
        for stat, value in stats.items():
            stats_message += f"  **{stat.replace('_', ' ').title()}:** {value}\n"
    await ctx.send(stats_message)
    
@commands.command()
async def equip(ctx, item_id: int):
    with lock:
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
    
        # Apply item stats to the player
        for stat, value in item_to_equip.get("stats", {}).items():
            increment_player_stat(ctx.author.id, stat, value)
    
        # Equip the item
        new_equipped_items = player["equipped_items"]
        new_equipped_items[item_to_equip["type"]] = item_to_equip
        update_player_data(ctx.author.id, equipped_items=new_equipped_items)
    
        await ctx.send(f"You equipped {item_to_equip['name']} (ID: {item_to_equip['id']}, {item_to_equip['type'].title()}).")
        
@commands.command()
async def unequip(ctx, item_type: str):
    """Unequip an item."""
    with lock:
        player = get_player_data(ctx.author.id)
        if not player:
            await ctx.send("You are not registered as a player.")
            return

        new_equipped_items = player["equipped_items"]
        if item_type not in new_equipped_items:
            await ctx.send(f"You don't have a {item_type} equipped.")
            return
        
        # Update player's stats
        for stat, value in new_equipped_items.get("stats", {}).items():
            increment_player_stat(ctx.author.id, stat, -value)
        # Unequip the item
        unequipped_item=new_equipped_items.pop(item_type)
        update_player_data(ctx.author.id, equipped_items=new_equipped_items)

        await ctx.send(f"You unequipped {unequipped_item['name']} (ID: {unequipped_item['id']}, {item_type.title()}).")

@commands.command()
async def stuff(ctx):
    """Display the user's equipped items."""
    with lock:
        player = get_player_data(ctx.author.id)
        if not player:
            await ctx.send("You are not registered as a player. (type !join)")
            return

        equipped_items = player["equipped_items"]
        if not equipped_items:
            await ctx.send("You have no items equipped.")
            return

        # Format equipped items for display
        equipped_list = "\n".join([f"{item['name']} (ID: {item['id']}, {item['type'].title()}, {item['rarity'].title()})" for item in equipped_items.values()])
        await ctx.send(f"**Your Equipped Items:**\n{equipped_list}")

@commands.command()
async def use(ctx, item_reference: str):
    """Use a consumable item (e.g., health potion)."""
    with lock:
        player = get_player_data(ctx.author.id)
        if not player:
            await ctx.send("You are not registered as a player. (type !join)")
            return

        # Ensure player health is initialized
        if player.get("health") is None:
            player["health"] = 100  # Default health if not set
            update_player_data(ctx.author.id, health=player["health"])

        inventory = player["inventory"]
        if not inventory:
            await ctx.send("Your inventory is empty.")
            return

        # Find the item in the inventory
        item_to_use = None

        if item_reference.lower() == "potion":
            # Find the first health potion in the inventory
            for item in inventory:
                if item["type"] == "consumable" and item["name"].lower() == "health potion":
                    item_to_use = item
                    break
            if not item_to_use:
                await ctx.send("You don't have any health potions in your inventory.")
                return
        else:
            # Try to find the item by ID
            if item_reference.isdigit():
                item_id = int(item_reference)
                item_to_use = next((item for item in inventory if item["id"] == item_id), None)
            else:
                # Try to find the item by name
                item_to_use = next((item for item in inventory if item["name"].lower() == item_reference.lower()), None)

            if not item_to_use:
                await ctx.send("Item not found in your inventory.")
                return

            # Check if the item is a consumable
            if item_to_use["type"] != "consumable":
                await ctx.send("You can only use consumable items.")
                return

        # Apply the item's effect
        if "effect" in item_to_use:
            health_restored = item_to_use["effect"]
            if not isinstance(health_restored, (int, float)) or health_restored <= 0:
                await ctx.send("This potion has an invalid effect.")
                return

            # Ensure player health is a valid number
            if not isinstance(player["health"], (int, float)):
                player["health"] = 100  # Reset to default if invalid

            # Restore health and cap at 100
            player["health"] = min(100, player["health"] + health_restored)
            update_player_data(ctx.author.id, health=player["health"])
            await ctx.send(f"You used {item_to_use['name']} (ID: {item_to_use['id']}) and restored {health_restored} health.")
        else:
            await ctx.send("This item has no effect.")

        # Remove the item from the inventory
        inventory.remove(item_to_use)
        item_manager.remove_item(item_to_use["id"])
        update_player_data(ctx.author.id, inventory=inventory)