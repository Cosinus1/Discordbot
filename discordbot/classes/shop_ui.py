import discord
from discord.ui import Select, View, Button
from utils.mmo_utils.embed_utils import create_item_embed
from database import get_player_data, update_player_data, get_user_data, update_user_data
from classes.item_manager import item_manager
from classes.shop_manager import shop_manager

class ShopSelect(Select):
    """
    A select menu for choosing an item from the shop.
    """

    def __init__(self, items):
        options = []
        for item in items:
            if item["type"] == "consumable":
                # Potions don't have rarity
                options.append(
                    discord.SelectOption(
                        label=f"{item['name']} - {item['price']} gold",
                        description=f"Type: {item['type'].title()}",
                        value=str(item["id"]),  # Use item ID as the value
                    )
                )
            else:
                # Equipment items have rarity
                options.append(
                    discord.SelectOption(
                        label=f"{item['name']} ({item['rarity'].title()}) - {item['price']} gold",
                        description=f"Type: {item['type'].title()}",
                        value=str(item["id"]),  # Use item ID as the value
                    )
                )
        super().__init__(placeholder="Choose an item to buy...", options=options)

    async def callback(self, interaction: discord.Interaction):
        """
        Handles the select menu interaction.
        """
        player = get_player_data(interaction.user.id)
        if not player:
            await interaction.response.send_message("You are not registered as a player.", ephemeral=True)
            return

        # Find the selected item in the shop
        item_id = int(self.values[0])
        item = next((item for item in shop_manager.items + shop_manager.potions if item["id"] == item_id), None)

        if item:
            # Create an embed for the selected item
            embed = create_item_embed(item)
            view = ShopItemView(player, item)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        else:
            await interaction.response.send_message("Item not found.", ephemeral=True)

class ShopItemView(View):
    """
    A view for handling shop item interactions.
    """

    def __init__(self, player, item):
        super().__init__()
        self.player = player
        self.item = item

        # Add a Buy button for the item
        self.add_item(BuyButton(item))

class BuyButton(Button):
    def __init__(self, item):
        super().__init__(style=discord.ButtonStyle.green, label="Buy")
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
    A view for handling shop interactions.
    """

    def __init__(self):
        super().__init__()
        items = shop_manager.items + shop_manager.potions
        self.add_item(ShopSelect(items))