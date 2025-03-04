from discord.ext import commands
from item_manager import item_manager
from database import get_player_data, update_player_data

@commands.command()
async def shop(ctx):
    """Display the items available in the shop."""
    items = item_manager.shop_items
    shop_list = "\n".join([f"{item['id']}. {item['name']} ({item['rarity'].title()}) - {item['price']} gold" for item in items])
    await ctx.send(f"**Shop Items:**\n{shop_list}")