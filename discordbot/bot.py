from config import bot, TOKEN
from database import init_db

# Initialize the database
init_db()

# Run the bot
bot.run(TOKEN)