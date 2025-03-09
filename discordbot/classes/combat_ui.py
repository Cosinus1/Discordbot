import discord
from discord.ui import Button, View
from utils.mmo_utils.embed_utils import create_combat_embed
from utils.mmo_utils.combat_utils import calculate_damage
from database import get_player_data, update_player_data, get_user_data, update_user_data
from classes.item_ui import ItemUI
import random

class CombatView(View):
    """
    A view for handling combat interactions (Attack, Use Potion, Flee, etc.).
    """

    def __init__(self, player, monster):
        super().__init__()
        self.player = player
        self.monster = monster

    @discord.ui.button(label="Attack", style=discord.ButtonStyle.red, emoji="⚔️")
    async def attack_button(self, interaction: discord.Interaction, button: Button):
        """
        Handles the Attack button click.
        """
        # Player attacks monster
        player_damage, is_critical = calculate_damage(self.player, self.monster)
        self.monster["health"] -= player_damage

        # Create a new embed with updated combat status
        embed = create_combat_embed(self.player, self.monster)
        embed.add_field(
            name="Combat Log",
            value=f"You attacked the {self.monster['name']} for {player_damage} damage! {'**Critical Hit!**' if is_critical else ''}",
            inline=False,
        )

        # Check if the monster is defeated
        if self.monster["health"] <= 0:
            embed.add_field(name="Victory!", value=f"You defeated the {self.monster['name']}! 🎉", inline=False)
            await interaction.response.edit_message(embed=embed, view=None)  # Disable buttons
            await self.display_loot(interaction)  # Display loot
            return

        # Monster attacks back
        monster_damage, is_critical = calculate_damage(self.monster, self.player)
        self.player["health"] -= monster_damage
        embed.add_field(
            name="Combat Log",
            value=f"The {self.monster['name']} attacked you for {monster_damage} damage! {'**Critical Hit!**' if is_critical else ''}",
            inline=False,
        )

        # Check if the player is defeated
        if self.player["health"] <= 0:
            embed.add_field(name="Defeat!", value=f"You were defeated by the {self.monster['name']}! 💀", inline=False)
            await interaction.response.edit_message(embed=embed, view=None)  # Disable buttons
            return

        # Update the message with the new embed
        await interaction.response.edit_message(embed=embed)

    async def display_loot(self, interaction: discord.Interaction):
        """
        Displays the loot won after defeating the monster.
        """
        rewards = self.monster["rewards"]
        gold = rewards.get("gold", 0)
        items = rewards.get("items", [])

        # Update the player's gold and inventory
        player = get_player_data(self.player["user_id"])
        user = get_user_data(self.player["user_id"])
        user["money"] += gold
        if items:
            item = random.choice(items)
            player["inventory"].append(item)
        update_player_data(self.player["user_id"], inventory=player["inventory"])
        update_user_data(self.player["user_id"], money=user["money"])

        # Create an embed to display the loot
        loot_embed = discord.Embed(title="Loot", color=discord.Color.gold())
        loot_embed.add_field(name="Gold", value=f"{gold} gold", inline=False)
        if items:
            for item in items:
                embed = ItemUI(item, context="loot").create_item_embed()
                view = ItemUI(item, context="loot")
                await interaction.followup.send(embed=embed, view=view)