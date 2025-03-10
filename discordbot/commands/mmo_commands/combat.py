import discord
from discord import File
from discord.ext import commands
from database import get_player_data, update_player_data
from classes.combat_ui import CombatView
from utils.mmo_utils.monster_utils import get_monster, get_monster_base_name
from utils.mmo_utils.combat_utils import calculate_damage
from utils.mmo_utils.embed_utils import create_combat_embed, create_hp_embed
import asyncio
import os

@commands.command()
async def pve(ctx, difficulty="easy"):
    player = get_player_data(ctx.author.id)
    monster = get_monster(difficulty)
    embed = create_combat_embed(player, monster)
    view = CombatView(player, monster)
    
    # Get the appropriate image for the monster
    # Extract the base name from the monster name (ignoring prefixes and suffixes)
    base_name = get_monster_base_name(monster["name"])
    
    # Try to find the image file
    image_path = f"data/mmo/PNG/{base_name.lower()}_vecto.png"
    if not os.path.exists(image_path):
        # Use a default image if the specific one isn't found
        image_path = "data/mmo/PNG/monster_default.png"
    
    file = File(image_path, filename=f"{base_name.lower()}_vecto.png")
    await ctx.send(embed=embed, file=file, view=view)
    
@commands.command()
async def attack(ctx, target: discord.Member):
    attacker = get_player_data(ctx.author.id)
    defender = get_player_data(target.id)

    if not attacker or not defender:
        await ctx.send("One or both players not found in the database.")
        return

    damage, is_critical = calculate_damage(attacker, defender)
    defender["health"] -= damage
    
    await ctx.send(
        f"{ctx.author.mention} attacked {target.mention} for {damage} damage!"
        + (" **Critical Hit!**" if is_critical else "")
    )

    defender_survives = defender["health"] > 0
    if defender_survives:    
        update_player_data(defender["user_id"], health=defender["health"])
    else:
        # Player dies: set health to 0 and apply cooldown
        defender["health"] = 0
        update_player_data(defender["user_id"], health=defender["health"])
        await ctx.send(f"{target.mention} You died. Please wait 5 minutes to be reincarnated.")
        
        # Reincarnate after 5 minutes
        await asyncio.sleep(300)  # 5 minutes
        defender["health"] = 100
        update_player_data(defender["user_id"], health=defender["health"])
        await ctx.send(f"{target.mention} You have been reincarnated with full health!")

@commands.command()
async def hp(ctx):
    """Display the player's current health using a health bar."""
    player = get_player_data(ctx.author.id)
    if not player:
        await ctx.send("You are not registered as a player. (type `!join` to play)")
        return

    embed = create_hp_embed(player, ctx.author.display_name)
    await ctx.send(embed=embed)

@commands.command()
async def health(ctx):
    """Display the player's current health using a health bar."""
    player = get_player_data(ctx.author.id)
    if not player:
        await ctx.send("You are not registered as a player. (type `!join` to play)")
        return

    embed = create_hp_embed(player, ctx.author.display_name)
    await ctx.send(embed=embed)