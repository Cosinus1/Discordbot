from discord.ext import commands
from database import get_player_data, create_player

@commands.command()
async def join(ctx):
    """Join the MMORPG and create a player profile."""
    player = get_player_data(ctx.author.id)
    if player:
        await ctx.send("You are already registered as a player.")
        return

    # Create a new player entry
    create_player(ctx.author.id)
    await ctx.send("Welcome to the MMORPG! Your player profile has been created.")