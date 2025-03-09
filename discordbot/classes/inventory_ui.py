import discord
from discord.ui import Select, View, Button
from utils.mmo_utils.embed_utils import create_item_embed
from database import get_player_data, update_player_data, increment_player_stat
from classes.item_manager import item_manager

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
        player = get_player_data(interaction.user.id)
        # Find the selected item in the player's inventory
        item_id = int(self.values[0])
        item = next((item for item in player["inventory"] if item["id"] == item_id), None)

        if item:
            # Create an embed for the selected item
            embed = create_item_embed(item)
            view = InventoryItemView(player, item)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        else:
            await interaction.response.send_message("Item not found.", ephemeral=True)

class InventoryItemView(View):
    """
    A view for handling inventory item interactions.
    """

    def __init__(self, player, item):
        super().__init__()
        self.player = player
        self.item = item

        if item["type"] == "consumable":
            self.add_item(UseButton(item))
        else:
            if item["type"] in player["equipped_items"]:
                self.add_item(UnEquipButton(item))
            else:
                self.add_item(EquipButton(item))

class EquipButton(Button):
    def __init__(self, item):
        super().__init__(style=discord.ButtonStyle.green, label="Equip")
        self.item = item

    async def callback(self, interaction: discord.Interaction):
        player = get_player_data(interaction.user.id)
        equipped_items = player["equipped_items"]

        # Unequip any item in the same slot
        if self.item["type"] in equipped_items:
            unequipped_item = equipped_items[self.item["type"]]
            for stat, value in unequipped_item.get("stats", {}).items():
                increment_player_stat(interaction.user.id, stat, -value)
            del equipped_items[self.item["type"]]

        # Equip the new item
        for stat, value in self.item.get("stats", {}).items():
            increment_player_stat(interaction.user.id, stat, value)
        equipped_items[self.item["type"]] = self.item
        update_player_data(interaction.user.id, equipped_items=equipped_items)

        await interaction.response.send_message(f"You equipped {self.item['name']}.", ephemeral=True)

class UnEquipButton(Button):
    def __init__(self, item):
        super().__init__(style=discord.ButtonStyle.red, label="Unequip")
        self.item = item

    async def callback(self, interaction: discord.Interaction):
        player = get_player_data(interaction.user.id)
        equipped_items = player["equipped_items"]

        # Unequip the item
        for stat, value in self.item.get("stats", {}).items():
            increment_player_stat(interaction.user.id, stat, -value)
        del equipped_items[self.item["type"]]
        update_player_data(interaction.user.id, equipped_items=equipped_items)

        await interaction.response.send_message(f"You unequipped {self.item['name']}.", ephemeral=True)

class UseButton(Button):
    def __init__(self, item):
        super().__init__(style=discord.ButtonStyle.blurple, label="Use")
        self.item = item

    async def callback(self, interaction: discord.Interaction):
        player = get_player_data(interaction.user.id)
        inventory = player["inventory"]

        # Apply the item's effect
        if "effect" in self.item:
            health_restored = self.item["effect"]
            player["health"] = min(player["stats"]["max_hp"], player["health"] + health_restored)
            update_player_data(interaction.user.id, health=player["health"])

            # Remove the item from the inventory
            inventory.remove(self.item)
            item_manager.remove_item(self.item["id"])
            update_player_data(interaction.user.id, inventory=inventory)

            await interaction.response.send_message(f"You used {self.item['name']} and restored {health_restored} health.", ephemeral=True)
        else:
            await interaction.response.send_message("This item has no effect.", ephemeral=True)

class InventoryView(View):
    """
    A view for handling inventory interactions.
    """

    def __init__(self, player):
        super().__init__()
        self.add_item(InventorySelect(player))