import discord
from discord.ui import View
from classes.item_ui import ItemButton
from database import get_player_data

class InventoryUI(View):
    """
    A view for displaying the player's inventory, organized in columns.
    """

    def __init__(self, player):
        super().__init__()
        self.player = player

        # Organize items into columns (e.g., 3 items per row)
        # This organizes up to 25 items (Discord's component limit)
        columns = [player["inventory"][i:i + 5] for i in range(0, min(len(player["inventory"]), 25), 5)]
        
        row = 0
        for column in columns:
            for item in column:
                # Create a button for each item and set its row
                item_button = ItemButton(item, context="inventory")
                item_button.row = row
                self.add_item(item_button)
            row += 1

    async def send_inventory(self, ctx):
        """Send the inventory UI to the channel."""
        # Count items by type for the description
        item_counts = {}
        for item in self.player["inventory"]:
            item_type = item.get("type", "misc")
            item_counts[item_type] = item_counts.get(item_type, 0) + 1
        
        description = "Manage your items below.\n\n"
        description += "**Inventory Summary:**\n"
        for item_type, count in item_counts.items():
            description += f"• {item_type.title()}: {count}\n"
        
        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Inventory",
            description=description,
            color=discord.Color.green()
        )
        
        # Add a field for gold amount if available
        from database import get_user_data
        user = get_user_data(ctx.author.id)
        if user and "money" in user:
            embed.add_field(name="Gold", value=f"{user['money']}")
        
        # Add a note if inventory is truncated due to Discord's component limit
        if len(self.player["inventory"]) > 25:
            embed.set_footer(text=f"Showing 25/{len(self.player['inventory'])} items. Use !inv2 to see more.")
        
        await ctx.send(embed=embed, view=self)