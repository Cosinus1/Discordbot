import asyncio
from classes.shop_manager import shop_manager

async def refresh_shop_task():
    """Task to refresh the shop every 10 minutes."""
    while True:
        await asyncio.sleep(600)  # 10 minutes
        shop_manager.refresh_shop()
        print("Shop refreshed!")