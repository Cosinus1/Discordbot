from discord.ext import commands
from config import bot, TOKEN
from database import init_db
from events import on_ready, on_message, on_member_join, on_voice_state_update
from tasks import check_inactivity

# Initialize the database
init_db()

# Register events
bot.event(on_ready)
bot.event(on_message)
bot.event(on_member_join)
bot.event(on_voice_state_update)

# Register tasks
check_inactivity.start()

# Run the bot
bot.run(TOKEN)