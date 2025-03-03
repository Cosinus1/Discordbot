from discord.ext import commands
from database import get_user_data, update_user_data

@commands.command()
async def admin(ctx, action: str, target: discord.Member, value: int):
    if 'dev' not in [role.name.lower() for role in ctx.author.roles]:
        await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
        return

    action = action.lower()
    if action not in ["setlevel", "setmoney"]:
        await ctx.send(f"{ctx.author.mention}, invalid action. Use `setlevel` or `setmoney`.")
        return

    if value < 0:
        await ctx.send(f"{ctx.author.mention}, the value must be a positive number.")
        return

    target_user = get_user_data(target.id)
    if not target_user:
        await ctx.send(f"{ctx.author.mention}, no data found for {target.mention}.")
        return

    if action == "setlevel":
        update_user_data(target.id, level=value)
        await ctx.send(f"{ctx.author.mention}, set {target.mention}'s level to **{value}**.")
    elif action == "setmoney":
        update_user_data(target.id, money=value)
        await ctx.send(f"{ctx.author.mention}, set {target.mention}'s money to **{value}**.")