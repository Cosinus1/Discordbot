from discord.ext import commands
from config import bot, TOKEN
from database import init_db
from events import on_ready, on_message, on_member_join, on_voice_state_update
from tasks import check_inactivity
from commands.user_commands import *
from commands.admin_commands import admin, bye

# Initialize the database
init_db()

# Register events
bot.event(on_ready)
bot.event(on_message)
bot.event(on_member_join)
bot.event(on_voice_state_update)

# Register tasks
check_inactivity.start()

# Register user commands
bot.add_command(exp)
bot.add_command(money)
bot.add_command(bet)
bot.add_command(daily)
bot.add_command(send)
bot.add_command(roll)
bot.add_command(expvoice)
# Register admin commands
bot.add_command(admin)
bot.add_command(bye)

# Run the bot
bot.run(TOKEN)