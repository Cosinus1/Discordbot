import asyncio
from database import update_user_data, get_all_users
from datetime import datetime

async def start(bot):
    print(f"Bot connecté en tant que {bot.user}")
    for guild in bot.guilds:
        await fetch_and_store_data(guild)

async def fetch_and_store_data(guild):
    print(f"Traitement des membres du serveur : {guild.name}")
    
    existing_users = {user["id"] for user in get_all_users()}  # Optimisation
    new_users = []

    for member in guild.members:
        if not member.bot and member.id not in existing_users:
            user_role = member.top_role.name if member.top_role != guild.default_role else 'Gueux'
            new_users.append({
                "user_id": member.id,
                "exp": 0,
                "level": 0,
                "last_activity": datetime.now(),
                "role": user_role,
                "last_exp_gain_date": datetime.now(),
                "daily_exp": 0,
                "money": 0,
                "last_daily_claim": None
            })
            print(f"{member.name} ajouté avec le rôle '{user_role}'.")

    if new_users:
        for user in new_users:
            # Unpack the user dictionary into keyword arguments
            update_user_data(
                user_id=user["user_id"],
                exp=user["exp"],
                level=user["level"],
                last_activity=user["last_activity"],
                role=user["role"],
                last_exp_gain_date=user["last_exp_gain_date"],
                daily_exp=user["daily_exp"],
                money=user["money"],
                last_daily_claim=user["last_daily_claim"]
            )
    else:
        print("Aucun nouveau membre à ajouter.")

    await asyncio.sleep(1)  # Évite d'être rate-limited si le bot est sur plusieurs serveurs