import discord
from discord.ext import commands
from database import get_user_data, update_user_data, get_player_data, update_player_data, get_all_users, get_all_players
from datetime import datetime
from config import DAILY_EXP_THRESHOLD, EXP_PAR_MINUTE_VOCAL
from events.on_voice_state_update import user_join_times
from config import bot
from classes.item_manager import item_manager

@commands.command()
async def admin(ctx, action: str, target: str, value: int = None):
    """Admin command to manage users."""
    # Check if the user has the 'dev' role
    if 'dev' not in [role.name.lower() for role in ctx.author.roles]:
        await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
        return

    # Validate the action
    action = action.lower()
    valid_actions = [
        "setlevel", "setmoney", "sethealth", "setexp", 
        "resetinventory", "revive", "kill", "additem", "removeitem"
    ]
    if action not in valid_actions:
        await ctx.send(f"{ctx.author.mention}, invalid action. Use one of: {', '.join(valid_actions)}.")
        return

    # Handle "all" target
    if target.lower() == "all":
        await ctx.send("Processing 'all' targets ...")
        # Get all users or players based on the action
        if action in ["setlevel", "setmoney", "setexp"]:
            targets = get_all_users()
        else:
            targets = get_all_players()

        if not targets:
            await ctx.send(f"{ctx.author.mention}, no targets found.")
            return

        # Apply the action to all targets
        for user_id in targets:
            try:
                if action == "setlevel":
                    if value is None or value < 0:
                        await ctx.send(f"{ctx.author.mention}, the value must be a positive number.")
                        return
                    update_user_data(user_id, level=value)
                elif action == "setmoney":
                    if value is None or value < 0:
                        await ctx.send(f"{ctx.author.mention}, the value must be a positive number.")
                        return
                    update_user_data(user_id, money=value)
                elif action == "sethealth":
                    if value is None or value < 0:
                        await ctx.send(f"{ctx.author.mention}, the value must be a positive number.")
                        return
                    update_player_data(user_id, health=value)
                elif action == "setexp":
                    if value is None or value < 0:
                        await ctx.send(f"{ctx.author.mention}, the value must be a positive number.")
                        return
                    update_user_data(user_id, exp=value)
                elif action == "resetinventory":
                    update_player_data(user_id, inventory=[])
                elif action == "revive":
                    update_player_data(user_id, health=100)
                elif action == "kill":
                    update_player_data(user_id, health=0)
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
                elif action == "removeitem":
                    if value is None:
                        await ctx.send(f"{ctx.author.mention}, please specify an item ID.")
                        return
                    player_data = get_player_data(user_id)
                    if player_data:
                        item_to_remove = None
                        for item in player_data["inventory"]:
                            if item["id"] == value:
                                item_to_remove = item
                                break
                        if item_to_remove:
                            player_data["inventory"].remove(item_to_remove)
                            update_player_data(user_id, inventory=player_data["inventory"])
                elif action == "resetstuff":
                    # Reset equipped items
                    update_player_data(user_id, equipped_items= {})
                
                    await ctx.send(f"{ctx.author.mention}, reset {target.mention}'s equipped items.")
            except Exception as e:
                await ctx.send(f"{ctx.author.mention}, an error occurred: {str(e)}")
                return
        await ctx.send(f"{ctx.author.mention}, applied `{action}` to all {'users' if action in ['setlevel', 'setmoney', 'setexp'] else 'players'}.")
        return

    # Handle single user target
    try:
        target_member = await commands.MemberConverter().convert(ctx, target)
    except commands.MemberNotFound:
        await ctx.send(f"{ctx.author.mention}, user `{target}` not found.")
        return

    # Get the target user's data
    target_user = get_user_data(target_member.id)
    if not target_user:
        await ctx.send(f"{ctx.author.mention}, no data found for {target_member.mention}.")
        return

    # Handle actions for single user
    try:
        if action == "setlevel":
            if value is None or value < 0:
                await ctx.send(f"{ctx.author.mention}, the value must be a positive number.")
                return
            update_user_data(target_member.id, level=value)
            await ctx.send(f"{ctx.author.mention}, set {target_member.mention}'s level to **{value}**.")

        elif action == "setmoney":
            if value is None or value < 0:
                await ctx.send(f"{ctx.author.mention}, the value must be a positive number.")
                return
            update_user_data(target_member.id, money=value)
            await ctx.send(f"{ctx.author.mention}, set {target_member.mention}'s money to **{value}**.")

        elif action == "sethealth":
            if value is None or value < 0:
                await ctx.send(f"{ctx.author.mention}, the value must be a positive number.")
                return
            update_player_data(target_member.id, health=value)
            await ctx.send(f"{ctx.author.mention}, set {target_member.mention}'s health to **{value}**.")

        elif action == "setexp":
            if value is None or value < 0:
                await ctx.send(f"{ctx.author.mention}, the value must be a positive number.")
                return
            update_user_data(target_member.id, exp=value)
            await ctx.send(f"{ctx.author.mention}, set {target_member.mention}'s experience to **{value}**.")

        elif action == "resetinventory":
            update_player_data(target_member.id, inventory=[])
            await ctx.send(f"{ctx.author.mention}, reset {target_member.mention}'s inventory.")

        elif action == "revive":
            update_player_data(target_member.id, health=100)
            await ctx.send(f"{ctx.author.mention}, revived {target_member.mention} to full health.")

        elif action == "kill":
            update_player_data(target_member.id, health=0)
            await ctx.send(f"{ctx.author.mention}, killed {target_member.mention}.")

        elif action == "additem":
            if value is None:
                await ctx.send(f"{ctx.author.mention}, please specify an item ID.")
                return
            item = item_manager.get_item_by_id(value)
            if not item:
                await ctx.send(f"{ctx.author.mention}, item with ID {value} not found.")
                return
            player_data = get_player_data(target_member.id)
            if not player_data:
                await ctx.send(f"{ctx.author.mention}, no player data found for {target_member.mention}.")
                return
            player_data["inventory"].append(item)
            update_player_data(target_member.id, inventory=player_data["inventory"])
            await ctx.send(f"{ctx.author.mention}, added {item['name']} to {target_member.mention}'s inventory.")

        elif action == "removeitem":
            if value is None:
                await ctx.send(f"{ctx.author.mention}, please specify an item ID.")
                return
            player_data = get_player_data(target_member.id)
            if not player_data:
                await ctx.send(f"{ctx.author.mention}, no player data found for {target_member.mention}.")
                return
            item_to_remove = None
            for item in player_data["inventory"]:
                if item["id"] == value:
                    item_to_remove = item
                    break
            if not item_to_remove:
                await ctx.send(f"{ctx.author.mention}, item with ID {value} not found in {target_member.mention}'s inventory.")
                return
            player_data["inventory"].remove(item_to_remove)
            update_player_data(target_member.id, inventory=player_data["inventory"])
            await ctx.send(f"{ctx.author.mention}, removed {item_to_remove['name']} from {target_member.mention}'s inventory.")
        
        elif action == "resetstuff":
            # Reset equipped items
            update_player_data(target_member.id, equipped_items={})
        
            await ctx.send(f"{ctx.author.mention}, reset {target.mention}'s equipped items.")

    except Exception as e:
        await ctx.send(f"{ctx.author.mention}, an error occurred: {str(e)}")

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