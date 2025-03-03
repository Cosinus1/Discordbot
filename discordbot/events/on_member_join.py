import discord
from config import bot
from database import update_user_data
from utils.roles import get_or_create_role, send_to_bot_channel

@bot.event
async def on_member_join(member):
    guild = member.guild
    role_Gueux = await get_or_create_role(guild, "Gueux", discord.Color.dark_grey())
    await member.add_roles(role_Gueux)
    update_user_data(member.id, role='Gueux')
    await send_to_bot_channel(guild, f"{member.name} a reçu le rôle Gueux.")