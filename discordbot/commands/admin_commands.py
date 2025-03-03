import discord
from discord.ext import commands
from database import get_user_data, update_user_data
from datetime import datetime
from config import DAILY_EXP_THRESHOLD, EXP_PAR_MINUTE_VOCAL
from events.on_voice_state_update import user_join_times
from config import bot

@commands.command()
async def admin(ctx, action: str, target: discord.Member, value: int):
    # Check if the user has the 'dev' role
    if 'dev' not in [role.name.lower() for role in ctx.author.roles]:
        await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
        return

    # Validate the action (setlevel or setmoney)
    action = action.lower()
    if action not in ["setlevel", "setmoney"]:
        await ctx.send(f"{ctx.author.mention}, invalid action. Use `setlevel` or `setmoney`.")
        return

    # Validate the value
    if value < 0:
        await ctx.send(f"{ctx.author.mention}, the value must be a positive number.")
        return

    # Get the target user's data
    target_user = get_user_data(target.id)
    if not target_user:
        await ctx.send(f"{ctx.author.mention}, no data found for {target.mention}.")
        return

    # Update the target user's data
    if action == "setlevel":
        update_user_data(target.id, level=value)
        await ctx.send(f"{ctx.author.mention}, set {target.mention}'s level to **{value}**.")
    elif action == "setmoney":
        update_user_data(target.id, money=value)
        await ctx.send(f"{ctx.author.mention}, set {target.mention}'s money to **{value}**.")

@commands.command()
async def bye(ctx):
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