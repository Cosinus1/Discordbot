import discord
from discord.ext import commands
from database import get_player_data, update_player_data
from utils.mmo_utils.combat_utils import calculate_damage
from utils.mmo_utils.monster_utils import get_monster
import random

@commands.command()
async def attack(ctx, target: discord.Member):
    attacker = get_player_data(ctx.author.id)
    defender = get_player_data(target.id)

    if not attacker or not defender:
        await ctx.send("One or both users not found in the database.")
        return

    damage = calculate_damage(attacker, defender)
    defender["health"] -= damage
    update_player_data(defender["user_id"], health=defender["health"])

    await ctx.send(f"{ctx.author.mention} attacked {target.mention} for {damage} damage!")

@commands.command()
async def farm(ctx):
    monster = get_monster()
    await ctx.send(f"You encountered a {monster['name']}!")

    # Simulate combat
    damage = random.randint(5, 15)
    await ctx.send(f"You dealt {damage} damage to the {monster['name']}!")