from discord.ext import commands
from classes.shop_ui import ShopView
import threading

lock = threading.Lock()

@commands.command()
async def shop(ctx):
    """Display the items available in the shop."""
    with lock:
        view = ShopView()
        await ctx.send("Select an item to buy:", view=view)