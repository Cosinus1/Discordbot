import discord
from config import bot

async def get_or_create_role(guild, role_name, color):
    role = discord.utils.get(guild.roles, name=role_name)
    if not role:
        role = await guild.create_role(name=role_name, color=color)
        await send_to_bot_channel(guild, f"Rôle '{role_name}' créé.")
    return role

async def send_to_bot_channel(guild, message):
    channel = discord.utils.get(guild.text_channels, name="bot")
    if channel:
        await channel.send(message)
    else:
        print(f"Le canal 'bot' n'existe pas sur le serveur {guild.name}.")