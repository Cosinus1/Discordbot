import asyncio
from discord.ext import tasks
from classes.shop_manager import shop_manager

@tasks.loop(minutes=120)
async def refresh_shop_task():
    """Task to refresh the shop every 120 minutes."""
    shop_manager.refresh_shop()
    print("Shop refreshed!")