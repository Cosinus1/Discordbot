from config import bot, EXP_PAR_MINUTE_VOCAL, DAILY_EXP_THRESHOLD
from database import get_user_data, update_user_data
from datetime import datetime
from utils.roles import check_role_upgrade, send_to_bot_channel

# Dictionary to store the join time of users
user_join_times = {}

async def start(member, before, after):
    if member.bot:  # Ignore bots
        return

    user_id = member.id
    user = get_user_data(user_id)
    
    if not user:
        user = {
            "user_id": user_id,
            "exp": 0,
            "level": 0,
            "last_activity": datetime.now(),
            "role": "Gueux",
            "last_exp_gain_date": datetime.now(),
            "daily_exp": 0,
            "money": 0
        }
        update_user_data(user_id, **user)

    # Check if the last experience gain was on a different day
    if user["last_exp_gain_date"].date() != datetime.now().date():
        user["daily_exp"] = 0
        user["last_exp_gain_date"] = datetime.now()

    # When the user joins a voice channel
    if after.channel and not before.channel:
        user_join_times[user_id] = datetime.now()

    # When the user leaves a voice channel
    if before.channel and not after.channel:
        if user_id in user_join_times:
            time_spent = (datetime.now() - user_join_times[user_id]).total_seconds() / 60
            del user_join_times[user_id]

            if user["daily_exp"] < DAILY_EXP_THRESHOLD:
                remaining_exp = DAILY_EXP_THRESHOLD - user["daily_exp"]
                exp_gain = min(EXP_PAR_MINUTE_VOCAL * time_spent, remaining_exp)
                exp_gain = int(exp_gain)

                user["exp"] += exp_gain
                user["daily_exp"] += exp_gain
                user["last_activity"] = datetime.now()
                update_user_data(user_id, exp=user["exp"], daily_exp=user["daily_exp"], last_activity=user["last_activity"], last_exp_gain_date=user["last_exp_gain_date"])

                await send_to_bot_channel(member.guild, f"{member.name} ({member.id}) gained {exp_gain} XP after leaving the voice channel.")

        await check_role_upgrade(member)