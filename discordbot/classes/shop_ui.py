import discord
from discord.ui import View, Button
from utils.mmo_utils.embed_utils import create_item_embed
from database import get_player_data, update_player_data, get_user_data, update_user_data
from classes.item_manager import item_manager
from classes.shop_manager import shop_manager

class ShopItemView(View):
    """
    A view for displaying a single shop item with a Buy button.
    """

    def __init__(self, item):
        super().__init__()
        self.item = item
        self.add_item(BuyButton(item))

class BuyButton(Button):
    def __init__(self, item):
        super().__init__(style=discord.ButtonStyle.green, label=f"Buy ({item['price']} gold)")
        self.item = item

    async def callback(self, interaction: discord.Interaction):
        player = get_player_data(interaction.user.id)
        if not player:
            await interaction.response.send_message("You are not registered as a player.", ephemeral=True)
            return

        user = get_user_data(interaction.user.id)
        if not user:
            await interaction.response.send_message("You are not registered in the database.", ephemeral=True)
            return

        # Check if the player has enough gold
        if user["money"] < self.item["price"]:
            await interaction.response.send_message("You don't have enough gold to buy this item.", ephemeral=True)
            return

        # Deduct money and add item to inventory
        user["money"] -= self.item["price"]
        player["inventory"].append(self.item)
        update_player_data(interaction.user.id, inventory=player["inventory"])
        update_user_data(interaction.user.id, money=user["money"])

        # Handle potions (unlimited stock)
        if self.item["type"] == "consumable":
            await interaction.response.send_message(f"You bought a {self.item['name']} (ID: {self.item['id']}) for {self.item['price']} gold!", ephemeral=True)
        else:
            # Replace sold item with a new one of the same rarity
            shop_manager.replace_sold_item(self.item["id"])
            await interaction.response.send_message(f"You bought a {self.item['name']} (ID: {self.item['id']}, {self.item['rarity'].title()}) for {self.item['price']} gold!", ephemeral=True)

        # Update the shop view
        view = ShopView()
        await interaction.followup.send("Shop updated:", view=view, ephemeral=True)

class ShopView(View):
    """
    A view for displaying all items in the shop with Buy buttons.
    """

    def __init__(self):
        super().__init__()
        items = shop_manager.items + shop_manager.potions

        # Add a Buy button for each item
        for item in items:
            self.add_item(BuyButton(item))