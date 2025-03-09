from discord.ext import commands
from database import get_player_data
from classes.inventory_ui import InventoryUI
from utils.mmo_utils.embed_utils import create_stats_embed, create_equipped_items_embed
import threading

lock = threading.Lock()

@commands.command()
async def inv(ctx):
    with lock:
        """Display the player's inventory."""
        player = get_player_data(ctx.author.id)
        if not player:
            await ctx.send("You are not registered as a player.")
            return
            
        if not player["inventory"]:
            await ctx.send("Your inventory is empty.")
            return
            
        # Use the InventoryUI class to organize items
        inventory_view = InventoryUI(player)
        await inventory_view.send_inventory(ctx)

@commands.command()
async def stats(ctx):
    """Display the player's stats using an embed."""
    player = get_player_data(ctx.author.id)
    if not player:
        await ctx.send("You are not registered as a player. (type `!join` to play)")
        return

    embed = create_stats_embed(player, ctx.author.display_name)
    await ctx.send(embed=embed)

@commands.command()
async def stuff(ctx):
    """Display the player's equipped items using an embed."""
    with lock:
        player = get_player_data(ctx.author.id)
        if not player:
            await ctx.send("You are not registered as a player. (type !join)")
            return

        embed = create_equipped_items_embed(player, ctx.author.display_name)
        if embed:
            await ctx.send(embed=embed)
        else:
            await ctx.send("You have no items equipped.")