from discord.ext import commands
from config import LEVEL_THRESHOLD, DAILY_EXP_THRESHOLD 
from database import get_user_data, update_user_data
from datetime import datetime, timedelta
import random

@commands.command()
async def exp(ctx):
    user = get_user_data(ctx.author.id)
    if user:
        current_exp = user["exp"]
        next_level_exp = (user["level"] + 1) * LEVEL_THRESHOLD
        await ctx.send(f"{ctx.author.mention}, tu as actuellement {current_exp} XP. Il te faut {next_level_exp - current_exp} XP pour atteindre le prochain niveau ! \n (daily exp : {user['daily_exp']}/{DAILY_EXP_THRESHOLD})" )
    else:
        await ctx.send(f"{ctx.author.mention}, aucune donnée trouvée pour toi.")

@commands.command()
async def money(ctx):
    user = get_user_data(ctx.author.id)
    if user:
        await ctx.send(f"{ctx.author.mention}, you have {user['money']} $.")
    else:
        await ctx.send(f"{ctx.author.mention}, no data found for you.")

# Add other user commands here...