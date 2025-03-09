import discord
from discord.ui import View, Button
from utils.mmo_utils.embed_utils import create_item_embed
from database import get_player_data, update_player_data, get_user_data, update_user_data, increment_player_stat
from classes.item_manager import item_manager
from classes.shop_manager import shop_manager

class ItemUI(View):
    def __init__(self, item, context="shop"):
        super().__init__()
        self.item = item
        self.context = context  # Can be "shop", "inventory", or "loot"
        
        # Add a button for this item
        self.add_item(ItemButton(item))
        
    def create_item_embed(self):
        return create_item_embed(self.item)

class ItemButton(Button):
    def __init__(self, item):
        super().__init__(style=discord.ButtonStyle.secondary, label=item["name"], row=0)
        self.item = item
        
    async def callback(self, interaction: discord.Interaction):
        """Handles the button click."""
        embed = create_item_embed(self.item)
        view = ItemActionsView(self.item, interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ItemActionsView(View):
    def __init__(self, item, user_id, context="inventory"):
        super().__init__()
        self.item = item
        self.context = context
        self.user_id = user_id
        
        # Add buttons based on the context
        if self.context == "shop":
            self.add_item(BuyButton(item))
        elif self.context == "inventory":
            player = get_player_data(self.user_id)
            if item["type"] == "consumable":
                self.add_item(UseButton(item))
            else:
                if item["type"] in player["equipped_items"] and player["equipped_items"][item["type"]]["id"] == item["id"]:
                    self.add_item(UnEquipButton(item))
                else:
                    self.add_item(EquipButton(item))
            self.add_item(SellButton(item))
        elif self.context == "loot":
            self.add_item(TakeButton(item))

class BuyButton(Button):
    def __init__(self, item):
        super().__init__(style=discord.ButtonStyle.green, label=f"Buy ({item['price']} gold)", row=1)
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

class UseButton(Button):
    def __init__(self, item):
        super().__init__(style=discord.ButtonStyle.blurple, label="Use", row=1)
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

class EquipButton(Button):
    def __init__(self, item):
        super().__init__(style=discord.ButtonStyle.green, label="Equip", row=1)
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
        super().__init__(style=discord.ButtonStyle.red, label="Unequip", row=1)
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

class SellButton(Button):
    def __init__(self, item):
        super().__init__(style=discord.ButtonStyle.gray, label="Sell", row=1)
        self.item = item

    async def callback(self, interaction: discord.Interaction):
        player = get_player_data(interaction.user.id)
        inventory = player["inventory"]
        equipped_items = player["equipped_items"]

        # Check if the item is equipped
        if self.item["type"] in equipped_items and equipped_items[self.item["type"]]["id"] == self.item["id"]:
            # Unequip the item first
            for stat, value in self.item.get("stats", {}).items():
                increment_player_stat(interaction.user.id, stat, -value)
            del equipped_items[self.item["type"]]
            update_player_data(interaction.user.id, equipped_items=equipped_items)

        # Find the item in the inventory by its ID
        item_to_remove = next((item for item in inventory if item["id"] == self.item["id"]), None)
        if item_to_remove:
            # Remove the item from the inventory
            inventory.remove(item_to_remove)
            item_manager.remove_item(self.item["id"])
            update_player_data(interaction.user.id, inventory=inventory)

            # Add the item's price to the player's money
            player_money = get_user_data(interaction.user.id).get("money", 0)
            new_money = player_money + self.item["price"]
            update_user_data(interaction.user.id, money=new_money)

            await interaction.response.send_message(f"You sold {self.item['name']} for {self.item['price']} gold.", ephemeral=True)
        else:
            await interaction.response.send_message("Item not found in inventory.", ephemeral=True)

class TakeButton(Button):
    def __init__(self, item):
        super().__init__(style=discord.ButtonStyle.green, label="Take", row=1)
        self.item = item

    async def callback(self, interaction: discord.Interaction):
        player = get_player_data(interaction.user.id)
        if not player:
            await interaction.response.send_message("You are not registered as a player.", ephemeral=True)
            return

        # Add the item to the player's inventory
        player["inventory"].append(self.item)
        update_player_data(interaction.user.id, inventory=player["inventory"])

        await interaction.response.send_message(f"You took {self.item['name']} (ID: {self.item['id']}).", ephemeral=True)