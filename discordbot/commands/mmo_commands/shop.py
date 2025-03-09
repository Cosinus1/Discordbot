from discord.ext import commands
from classes.shop_manager import shop_manager
from classes.item_ui import ItemUI
import threading

lock = threading.Lock()

@commands.command()
async def shop(ctx):
    """Display the items available in the shop."""
    with lock:
        items = shop_manager.items + shop_manager.potions
        for item in items:
            embed = ItemUI(item, context="shop").create_item_embed()
            view = ItemUI(item, context="shop")
            await ctx.send(embed=embed, view=view)