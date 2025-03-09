import discord
from discord.ui import Select, View
from utils.embed_utils import create_item_embed

class InventorySelect(Select):
    """
    A select menu for choosing an item from the inventory.
    """

    def __init__(self, player):
        options = []
        for item in player["inventory"]:
            options.append(
                discord.SelectOption(
                    label=item["name"],
                    description=f"Type: {item['type'].title()}",
                    value=str(item["id"]),  # Use item ID as the value
                )
            )
        super().__init__(placeholder="Choose an item to view...", options=options)

    async def callback(self, interaction: discord.Interaction):
        """
        Handles the select menu interaction.
        """
        # Find the selected item in the player's inventory
        item_id = int(self.values[0])
        item = next((item for item in interaction.user["inventory"] if item["id"] == item_id), None)

        if item:
            # Create an embed for the selected item
            embed = create_item_embed(item)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("Item not found.", ephemeral=True)

class InventoryView(View):
    """
    A view for handling inventory interactions.
    """

    def __init__(self, player):
        super().__init__()
        self.add_item(InventorySelect(player))