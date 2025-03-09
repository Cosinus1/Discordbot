import discord
from discord.ui import View
from classes.item_ui import ItemUI
from classes.shop_manager import shop_manager

class ShopUI(View):
    """
    A view for displaying all items in the shop, organized in columns.
    """

    def __init__(self):
        super().__init__()
        items = shop_manager.items + shop_manager.potions

        # Organize items into columns (e.g., 3 items per row)
        columns = [items[i:i + 3] for i in range(0, len(items), 3)]

        # Add ItemUI components for each item
        for column in columns:
            for item in column:
                item_ui = ItemUI(item, context="shop")
                self.add_item(item_ui)

    async def send_shop(self, ctx):
        """Send the shop UI to the channel."""
        embed = discord.Embed(
            title="Shop",
            description="Browse the available items below.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed, view=self)