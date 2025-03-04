from discord.ext import commands
import asyncio
from config import bot, TOKEN
from database import init_db
from events import on_ready as on_ready_handler, on_message as on_message_handler, on_member_join as on_member_join_handler, on_voice_state_update as on_voice_state_update_handler
from tasks import check_inactivity, shop_tasks
from commands import user_commands, admin_commands
from commands.mmo_commands.combat import attack, pve, hp, health
from commands.mmo_commands.inventory import inv, stats, equip, unequip, stuff, buy, sell
from commands.mmo_commands.shop import shop
from commands.mmo_commands.join import join

# Initialize the database
init_db()

# Register events
@bot.event
async def on_ready():
    await on_ready_handler.start(bot)  # Pass bot as an argument
    
    # Start background tasks after the bot is ready
    check_inactivity.start()
    shop_tasks.refresh_shop_task.start()


@bot.event
async def on_message(message):
    await on_message_handler.start(message)  # Call the on_message function from the events module

@bot.event
async def on_member_join(member):
    await on_member_join_handler.start(member)  # Call the on_member_join function from the events module

@bot.event
async def on_voice_state_update(member, before, after):
    await on_voice_state_update_handler.start(member, before, after)  # Call the on_voice_state_update function from the events module

# Register commands
# User Commands
bot.add_command(user_commands.exp)
bot.add_command(user_commands.xp)
bot.add_command(user_commands.money)
bot.add_command(user_commands.bet)
bot.add_command(user_commands.daily)
bot.add_command(user_commands.send)
bot.add_command(user_commands.roll)
# Admin Commands
bot.add_command(admin_commands.admin)
bot.add_command(admin_commands.setallmoney)
bot.add_command(admin_commands.bye)
# MMO Commands
bot.add_command(join)
bot.add_command(attack)
bot.add_command(pve)
bot.add_command(hp)
bot.add_command(health)
bot.add_command(inv)
bot.add_command(stats)
bot.add_command(equip)
bot.add_command(unequip)
bot.add_command(stuff)
bot.add_command(shop)
bot.add_command(buy)
bot.add_command(sell)

# Run the bot
bot.run(TOKEN)