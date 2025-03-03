from database import get_user_data, update_user_data
from config import LEVEL_THRESHOLD
from utils.roles import send_to_bot_channel

async def check_level_upgrade(member):
    user = get_user_data(member.id)
    if not user:
        return

    new_level = user["exp"] // LEVEL_THRESHOLD

    if new_level > user["level"]:
        update_user_data(member.id, level=new_level)
        await send_to_bot_channel(member.guild, f"🎉 {member.mention} a atteint le niveau **{new_level}** ! Félicitations ! 🎉")