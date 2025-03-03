import discord
from config import EXP_POUR_CHEVALIER, EXP_POUR_BARON, EXP_POUR_DUC
from database import get_user_data, update_user_data

async def get_or_create_role(guild, role_name, color):
    role = discord.utils.get(guild.roles, name=role_name)
    if not role:
        role = await guild.create_role(name=role_name, color=color)
        await send_to_bot_channel(guild, f"Rôle '{role_name}' créé.")
    return role

async def check_role_upgrade(member):
    user = get_user_data(member.id)
    if not user:
        return

    guild = member.guild
    role_Gueux = await get_or_create_role(guild, "Gueux", discord.Color.dark_grey())
    role_Chevalier = await get_or_create_role(guild, "Chevalier", discord.Color.gold())
    role_Baron = await get_or_create_role(guild, "Baron", discord.Color.purple())
    role_Duc = await get_or_create_role(guild, "Duc", discord.Color.dark_blue())
    
    if user["exp"] >= EXP_POUR_CHEVALIER and user["role"] == "Gueux":
        await member.remove_roles(role_Gueux)
        await member.add_roles(role_Chevalier)
        update_user_data(member.id, role="Chevalier")
        await send_to_bot_channel(guild, f"{member.mention} a été adoubé.")
    if user["exp"] >= EXP_POUR_BARON and user["role"] == "Chevalier":
        await member.remove_roles(role_Chevalier)
        await member.add_roles(role_Baron)
        update_user_data(member.id, role="Baron")
        await send_to_bot_channel(guild, f"{member.mention} a été promu Baron.")
    if user["exp"] >= EXP_POUR_DUC and user["role"] == "Baron":
        await member.remove_roles(role_Baron)
        await member.add_roles(role_Duc)
        update_user_data(member.id, role="Duc")
        await send_to_bot_channel(guild, f"{member.mention} a été promu Duc.")
        
async def send_to_bot_channel(guild, message):
    channel = discord.utils.get(guild.text_channels, name="bot")
    if channel:
        await channel.send(message)
    else:
        print(f"Le canal 'bot' n'existe pas sur le serveur {guild.name}.")