import discord
from discord.ui import View
from classes.item_ui import ItemUI

class InventoryUI(View):
    """
    A view for displaying the player's inventory, organized in columns.
    """

    def __init__(self, player):
        super().__init__()
        self.player = player

        # Organize items into columns (e.g., 3 items per row)
        columns = [player["inventory"][i:i + 3] for i in range(0, len(player["inventory"]), 3)]

        # Add ItemUI components for each item
        for column in columns:
            for item in column:
                item_ui = ItemUI(item, context="inventory")
                self.add_item(item_ui)

    async def send_inventory(self, ctx):
        """Send the inventory UI to the channel."""
        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Inventory",
            description="Manage your items below.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, view=self)