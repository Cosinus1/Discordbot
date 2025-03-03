import discord
import sqlite3
from discord.ext import tasks
from config import bot, INACTIVITE_JOURS
from database import update_user_data
from datetime import datetime
from utils.roles import get_or_create_role, send_to_bot_channel

@tasks.loop(hours=24)
async def check_inactivity():
    for guild in bot.guilds:
        role_Gueux = await get_or_create_role(guild, "Gueux", discord.Color.dark_grey())
        role_Chevalier = await get_or_create_role(guild, "Chevalier", discord.Color.gold())

        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE role = ?', ("Chevalier",))
        for user in c.fetchall():
            last_activity = datetime.fromisoformat(user[3])
            if (datetime.now() - last_activity).days >= INACTIVITE_JOURS:
                member = guild.get_member(user[0])
                if member:
                    await member.remove_roles(role_Chevalier)
                    await member.add_roles(role_Gueux)
                    update_user_data(user[0], role="Gueux")
                    await send_to_bot_channel(guild, f"{member.mention} est redevenu 'Gueux'.")
        conn.close()