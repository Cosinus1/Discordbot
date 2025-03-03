from discord.ext import commands
from config import bot, TOKEN
from database import init_db
from events import on_ready, on_message, on_member_join, on_voice_state_update
from tasks import check_inactivity
from commands import user_commands, admin_commands

# Initialize the database
init_db()

# Register events
@bot.event
async def ready():
    await on_ready.on_ready()  # Call the on_ready function from the events module

@bot.event
async def message(message):
    await on_message.on_message(message)  # Call the on_message function from the events module

@bot.event
async def member_join(member):
    await on_member_join.on_member_join(member)  # Call the on_member_join function from the events module

@bot.event
async def voice_state_update(member, before, after):
    await on_voice_state_update.on_voice_state_update(member, before, after)  # Call the on_voice_state_update function from the events module

# Register tasks
check_inactivity.check_inactivity()

# Register commands
bot.add_command(user_commands.exp)
bot.add_command(user_commands.xp)
bot.add_command(user_commands.money)
bot.add_command(user_commands.bet)
bot.add_command(user_commands.daily)
bot.add_command(user_commands.send)
bot.add_command(user_commands.roll)
bot.add_command(admin_commands.admin)
bot.add_command(admin_commands.bye)

# Run the bot
bot.run(TOKEN)