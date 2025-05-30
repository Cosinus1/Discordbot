from discord.ext import commands
from classes.shop_ui import ShopUI
import threading

lock = threading.Lock()

@commands.command()
async def shop(ctx):
    """Display the items available in the shop."""
    with lock:
        shop_ui = ShopUI()
        await shop_ui.send_shop(ctx)