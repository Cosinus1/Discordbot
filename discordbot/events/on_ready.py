from config import bot
from database import get_user_data, update_user_data
from datetime import datetime

async def on_ready():
    print(bot.guilds)
    for guild in bot.guilds:
        await fetch_and_store_data(guild)
    print(f"Bot connecté en tant que {bot.user}")

async def fetch_and_store_data(guild):
    for member in guild.members:
        if not member.bot:
            user = get_user_data(member.id)
            if not user:
                user_role = member.top_role.name if member.top_role != guild.default_role else 'Gueux'
                update_user_data(
                    user_id=member.id,
                    exp=0,
                    level=0,
                    last_activity=datetime.now(),
                    role=user_role,
                    last_exp_gain_date=datetime.now(),
                    daily_exp=0,
                    money=0,
                    last_daily_claim=None
                )
                print(f"{member.name} a été ajouté à la base de données avec le rôle '{user_role}'.")