import discord
from discord.ext import commands
from database import get_player_data, get_user_data, update_player_data, update_user_data
from utils.mmo_utils.monster_utils import get_monster
from utils.mmo_utils.combat_utils import simulate_combat, calculate_damage
import random
import asyncio

@commands.command()
async def pve(ctx, difficulty="easy"):
    """Fight a randomly generated monster based on difficulty."""
    # Validate difficulty input
    valid_difficulties = ["easy", "medium", "hard", "hardcore"]
    if difficulty.lower() not in valid_difficulties:
        await ctx.send(f"Invalid difficulty. Choose from: {', '.join(valid_difficulties)}")
        return
    
    player = get_player_data(ctx.author.id)
    user = get_user_data(ctx.author.id)
    if not player:
        await ctx.send(f"{ctx.author.mention} You are not registered as a player. Use `!join` to create a player profile.")
        return

    if player.get("health", 100) <= 0:
        await ctx.send(f"{ctx.author.mention} You are dead. Please wait 5 minutes to be reincarnated.")
        return

    # Get monster based on difficulty
    monster = get_monster(difficulty.lower())
    await ctx.send(f"{ctx.author.mention} You encountered a {monster['name']} ({monster['rarity'].title()})!")

    # Simulate combat
    combat_log, player_wins = simulate_combat(player, monster)
    for log in combat_log:
        await ctx.send(log)
        await asyncio.sleep(1)  # Add a delay for dramatic effect

    if player_wins:
        # Player wins: give rewards
        rewards = monster["rewards"]
        gold = rewards.get("gold", 0)
        items = rewards.get("items", [])

        user["money"] += gold
        if items:
            item = random.choice(items)
            player["inventory"].append(item)
            await ctx.send(f"{ctx.author.mention} You defeated the {monster['name']} and gained {gold} gold and a {item['name']}!")
        else:
            await ctx.send(f"{ctx.author.mention} You defeated the {monster['name']} and gained {gold} gold!")

        update_player_data(ctx.author.id, inventory=player["inventory"])
        update_user_data(ctx.author.id, money=user["money"])
    else:
        # Player dies: set health to 0 and apply cooldown
        player["health"] = 0
        update_player_data(ctx.author.id, health=player["health"])
        await ctx.send(f"{ctx.author.mention} You died. Please wait 5 minutes to be reincarnated.")

        # Reincarnate after 5 minutes
        await asyncio.sleep(300)  # 5 minutes
        player["health"] = 100
        update_player_data(ctx.author.id, health=player["health"])
        await ctx.send(f"{ctx.author.mention} You have been reincarnated with full health!")
        

@commands.command()
async def attack(ctx, target: discord.Member):
    attacker = get_player_data(ctx.author.id)
    defender = get_player_data(target.id)

    if not attacker or not defender:
        await ctx.send("One or both players not found in the database.")
        return

    damage = calculate_damage(attacker, defender)
    defender["health"] -= damage
    update_player_data(defender["user_id"], health=defender["health"])

    await ctx.send(f"{ctx.author.mention} attacked {target.mention} for {damage} damage!")
    
@commands.command()
async def hp(ctx):
    player = get_player_data(ctx.author.id)
    if player:
        current_hp = player["health"]
        await ctx.send(f"{ctx.author.mention}, tu as actuellement {current_hp} HP." )
    else:
        await ctx.send(f"{ctx.author.mention}, aucune donnée trouvée pour toi.")
        
@commands.command()
async def health(ctx):
    player = get_player_data(ctx.author.id)
    if player:
        current_hp = player["health"]
        await ctx.send(f"{ctx.author.mention}, tu as actuellement {current_hp} HP." )
    else:
        await ctx.send(f"{ctx.author.mention}, aucune donnée trouvée pour toi.")