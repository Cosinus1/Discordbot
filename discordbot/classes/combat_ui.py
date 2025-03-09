import discord
from discord.ui import Button, View
from utils.mmo_utils.mmo_utils.embed_utils import create_combat_embed, create_health_bar
from utils.mmo_utils.combat_utils import calculate_damage

class CombatView(View):
    """
    A view for handling combat interactions (Attack, Flee, etc.).
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
        # Calculate damage and update monster health
        damage, is_critical = calculate_damage(self.player, self.monster)
        self.monster["health"] -= damage

        # Create a new embed with updated combat status
        embed = create_combat_embed(self.player, self.monster)
        embed.add_field(
            name="Combat Log",
            value=f"You attacked the {self.monster['name']} for {damage} damage! {'**Critical Hit!**' if is_critical else ''}",
            inline=False,
        )

        # Check if the monster is defeated
        if self.monster["health"] <= 0:
            embed.add_field(name="Victory!", value=f"You defeated the {self.monster['name']}! 🎉", inline=False)
            await interaction.response.edit_message(embed=embed, view=None)  # Disable buttons
            return

        # Update the message with the new embed
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Flee", style=discord.ButtonStyle.gray, emoji="🏃‍♂️")
    async def flee_button(self, interaction: discord.Interaction, button: Button):
        """
        Handles the Flee button click.
        """
        # Create a new embed to indicate fleeing
        embed = create_combat_embed(self.player, self.monster)
        embed.add_field(name="Combat Log", value="You fled from combat! 🏃‍♂️", inline=False)

        # Update the message and disable buttons
        await interaction.response.edit_message(embed=embed, view=None)