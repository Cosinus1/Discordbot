import discord
from discord.ext import commands
from database import get_user_data, update_user_data, get_player_data, update_player_data, get_all_users, get_all_players
from datetime import datetime
from config import DAILY_EXP_THRESHOLD, EXP_PAR_MINUTE_VOCAL
from events.on_voice_state_update import user_join_times
from config import bot
from classes.item_manager import item_manager


@commands.command()
async def admin(ctx, action: str, target: str = None, value: int = None):
    """Admin command to manage users."""
    # Check if the user has the 'dev' role
    if 'dev' not in [role.name.lower() for role in ctx.author.roles]:
        await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
        return

    # Validate the action
    action = action.lower()
    valid_actions = [
        "setlevel", "setmoney", "sethealth", "setexp", 
        "resetinventory", "revive", "kill", "additem", "removeitem", "resetstuff", "rmitems"
    ]
    if action not in valid_actions:
        await ctx.send(f"{ctx.author.mention}, invalid action. Use one of: {', '.join(valid_actions)}.")
        return

    # Handle the action first
    if action == "rmitems":
        # Special case: rmitems affects all players and the item_manager
        await handle_rmitems(ctx)
        return

    # For other actions, check if the target is valid
    if not target:
        await ctx.send(f"{ctx.author.mention}, you must specify a target (user or 'all').")
        return

    # Handle the target (single user or all)
    if target.lower() == "all":
        await handle_all_targets(ctx, action, value)
    else:
        await handle_single_target(ctx, action, target, value)

async def handle_rmitems(ctx):
    """Handle the rmitems action (reset all items and player inventories)."""
    # Remove all items from the item_manager
    item_manager.items = []
    item_manager.available_ids = set()
    item_manager.next_id = 1
    item_manager.save_items()

    # Reset inventory and equipped items for all players
    all_players = get_all_players()
    for player_id in all_players:
        update_player_data(player_id, inventory=[], equipped_items={})

    await ctx.send(f"{ctx.author.mention}, removed all items from the game and reset all player inventories.")

async def handle_all_targets(ctx, action, value):
    """Handle actions for all targets."""
    await ctx.send("Processing 'all' targets ...")
    targets = get_all_users() if action in ["setlevel", "setmoney", "setexp"] else get_all_players()

    if not targets:
        await ctx.send(f"{ctx.author.mention}, no targets found.")
        return

    for user_id in targets:
        try:
            await apply_action(ctx, action, user_id, value)
        except Exception as e:
            await ctx.send(f"{ctx.author.mention}, an error occurred: {str(e)}")
            return

    await ctx.send(f"{ctx.author.mention}, applied `{action}` to all {'users' if action in ['setlevel', 'setmoney', 'setexp'] else 'players'}.")

async def handle_single_target(ctx, action, target, value):
    """Handle actions for a single target."""
    try:
        target_member = await commands.MemberConverter().convert(ctx, target)
    except commands.MemberNotFound:
        await ctx.send(f"{ctx.author.mention}, user `{target}` not found.")
        return

    target_user = get_user_data(target_member.id)
    if not target_user:
        await ctx.send(f"{ctx.author.mention}, no data found for {target_member.mention}.")
        return

    try:
        await apply_action(ctx, action, target_member.id, value)
    except Exception as e:
        await ctx.send(f"{ctx.author.mention}, an error occurred: {str(e)}")

async def apply_action(ctx, action, user_id, value):
    """Apply the specified action to the target."""
    if action == "setlevel":
        if not validate_value(value):
            await ctx.send(f"{ctx.author.mention}, the value must be a positive number.")
            return
        update_user_data(user_id, level=value)
        await ctx.send(f"{ctx.author.mention}, set level to **{value}** for user ID {user_id}.")

    elif action == "setmoney":
        if not validate_value(value):
            await ctx.send(f"{ctx.author.mention}, the value must be a positive number.")
            return
        update_user_data(user_id, money=value)
        await ctx.send(f"{ctx.author.mention}, set money to **{value}** for user ID {user_id}.")

    elif action == "sethealth":
        if not validate_value(value):
            await ctx.send(f"{ctx.author.mention}, the value must be a positive number.")
            return
        update_player_data(user_id, health=value)
        await ctx.send(f"{ctx.author.mention}, set health to **{value}** for user ID {user_id}.")

    elif action == "setexp":
        if not validate_value(value):
            await ctx.send(f"{ctx.author.mention}, the value must be a positive number.")
            return
        update_user_data(user_id, exp=value)
        await ctx.send(f"{ctx.author.mention}, set experience to **{value}** for user ID {user_id}.")

    elif action == "resetinventory":
        update_player_data(user_id, inventory=[])
        await ctx.send(f"{ctx.author.mention}, reset inventory for user ID {user_id}.")

    elif action == "revive":
        update_player_data(user_id, health=100)
        await ctx.send(f"{ctx.author.mention}, revived user ID {user_id} to full health.")

    elif action == "kill":
        update_player_data(user_id, health=0)
        await ctx.send(f"{ctx.author.mention}, killed user ID {user_id}.")

    elif action == "additem":
        if value is None:
            await ctx.send(f"{ctx.author.mention}, please specify an item ID.")
            return
        item = item_manager.get_item_by_id(value)
        if not item:
            await ctx.send(f"{ctx.author.mention}, item with ID {value} not found.")
            return
        player_data = get_player_data(user_id)
        if player_data:
            player_data["inventory"].append(item)
            update_player_data(user_id, inventory=player_data["inventory"])
            await ctx.send(f"{ctx.author.mention}, added {item['name']} to inventory for user ID {user_id}.")

    elif action == "removeitem":
        if value is None:
            await ctx.send(f"{ctx.author.mention}, please specify an item ID.")
            return
        player_data = get_player_data(user_id)
        if player_data:
            item_to_remove = next((item for item in player_data["inventory"] if item["id"] == value), None)
            if item_to_remove:
                player_data["inventory"].remove(item_to_remove)
                update_player_data(user_id, inventory=player_data["inventory"])
                await ctx.send(f"{ctx.author.mention}, removed {item_to_remove['name']} from inventory for user ID {user_id}.")
            else:
                await ctx.send(f"{ctx.author.mention}, item with ID {value} not found in inventory for user ID {user_id}.")

    elif action == "resetstuff":
        update_player_data(user_id, equipped_items={})
        await ctx.send(f"{ctx.author.mention}, reset equipped items for user ID {user_id}.")

def validate_value(value):
    """Validate that the value is a positive number."""
    return value is not None and value >= 0

@commands.command()
async def setallmoney(ctx, value: int):
    """Admin command to manage users."""
    # Check if the user has the 'dev' role
    if 'dev' not in [role.name.lower() for role in ctx.author.roles]:
        await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
        return
    targets = get_all_users()
    print(targets)
    try:
        await ctx.send(f"setting all users money to {value} ...")
        for target in targets :
            update_user_data(target["id"], money = value)
        await ctx.send("Done.")
    except Exception as e:
        await ctx.send(f"{ctx.author.mention}, an error occurred: {str(e)}")
    
            
@commands.command()
async def bye(ctx):
    """Stop the bot and process XP for users in voice channels."""
    # Check if the user has the 'dev' role
    if 'dev' not in [role.name.lower() for role in ctx.author.roles]:
        await ctx.send("You do not have permission to stop the bot!")
        return

    await ctx.send("Miaou ! Zzzzz....")

    # Process XP for users in voice channels
    for user_id, join_time in user_join_times.items():
        user = get_user_data(user_id)
        if user:
            time_spent = (datetime.now() - join_time).total_seconds() / 60
            if user["daily_exp"] < DAILY_EXP_THRESHOLD:
                remaining_exp = DAILY_EXP_THRESHOLD - user["daily_exp"]
                exp_gain = min(EXP_PAR_MINUTE_VOCAL * time_spent, remaining_exp)
                exp_gain = int(exp_gain)

                user["exp"] += exp_gain
                user["daily_exp"] += exp_gain
                user["last_activity"] = datetime.now()
                update_user_data(
                    user_id,
                    exp=user["exp"],
                    daily_exp=user["daily_exp"],
                    last_activity=user["last_activity"],
                    last_exp_gain_date=user["last_exp_gain_date"]
                )

                print(f"{user_id} gained {exp_gain} XP after leaving the voice channel.")

    # Close the bot
    await bot.close()