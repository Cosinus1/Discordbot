import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import asyncio
import sqlite3
import requests
from google.cloud import secretmanager
import random

# Configuration
with open("token.txt", "r") as file:
    TOKEN = file.read().strip()

def get_deepseek_api_key():
    client = secretmanager.SecretManagerServiceClient()
    name = "projects/discordbot-452223/secrets/deepseek-api-key/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

DEEPSEEK_API_KEY = get_deepseek_api_key()  # Store your API key in an environment variable
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"  # API endpoint

EXP_PAR_MESSAGE = 10  # Experience gained per message
EXP_PAR_MINUTE_VOCAL = 5  # Experience gained per minute in voice
EXP_POUR_CHEVALIER = 700  # Experience required to become Chevalier
EXP_POUR_BARON = 1400
EXP_POUR_DUC = 2100
INACTIVITE_JOURS = 7  # Days of inactivity before reverting to Gueux
LEVEL_THRESHOLD = 100  # Experience required to level up
DAILY_EXP_THRESHOLD = 100  # Maximum experience a user can gain per day

# Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Create the bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Database setup
def init_db():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            exp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 0,
            last_activity TEXT,
            role TEXT DEFAULT 'Gueux',
            last_exp_gain_date TEXT,
            daily_exp INTEGER DEFAULT 0,
            money INTEGER DEFAULT 0,
            last_daily_claim TEXT  -- New column
        )
    ''')
    
    # Add the last_daily_claim column if it doesn't exist
    c.execute('PRAGMA table_info(users)')
    columns = [column[1] for column in c.fetchall()]
    if 'last_daily_claim' not in columns:
        c.execute('ALTER TABLE users ADD COLUMN last_daily_claim TEXT')
        
    # Add the money column if it doesn't exist
    if 'money' not in columns:
        c.execute('ALTER TABLE users ADD COLUMN money INTEGER DEFAULT 0')
    
    conn.commit()
    conn.close()

init_db()  # Initialize the database

# Function to get user data from the database
def get_user_data(user_id):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        try:
            last_daily_claim = datetime.fromisoformat(user[8]) if user[8] else None
        except (TypeError, ValueError):
            last_daily_claim = None  # Handle invalid or NULL data

        return {
            "user_id": user[0],
            "exp": user[1],
            "level": user[2],
            "last_activity": datetime.fromisoformat(user[3]),
            "role": user[4],
            "last_exp_gain_date": datetime.fromisoformat(user[5]) if user[5] else None,
            "daily_exp": user[6],
            "money": user[7] if user[7] is not None else 0,  # Handle NULL values
            "last_daily_claim": last_daily_claim  # Handle invalid or NULL data
        }
    return None

def update_user_data(user_id, exp=None, level=None, last_activity=None, role=None, last_exp_gain_date=None, daily_exp=None, money=None, last_daily_claim=None):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    if get_user_data(user_id):
        updates = []
        params = []
        if exp is not None:
            updates.append("exp = ?")
            params.append(exp)
        if level is not None:
            updates.append("level = ?")
            params.append(level)
        if last_activity is not None:
            updates.append("last_activity = ?")
            params.append(last_activity.isoformat())
        if role is not None:
            updates.append("role = ?")
            params.append(role)
        if last_exp_gain_date is not None:
            updates.append("last_exp_gain_date = ?")
            params.append(last_exp_gain_date.isoformat())
        if daily_exp is not None:
            updates.append("daily_exp = ?")
            params.append(daily_exp)
        if money is not None:
            updates.append("money = ?")
            params.append(money)
        if last_daily_claim is not None:
            updates.append("last_daily_claim = ?")
            params.append(last_daily_claim.isoformat())
        params.append(user_id)
        c.execute(f'UPDATE users SET {", ".join(updates)} WHERE user_id = ?', params)
    else:
        c.execute('''
            INSERT INTO users (user_id, exp, level, last_activity, role, last_exp_gain_date, daily_exp, money, last_daily_claim)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            exp or 0,
            level or 0,
            last_activity.isoformat() if last_activity else None,
            role or 'Gueux',
            last_exp_gain_date.isoformat() if last_exp_gain_date else None,
            daily_exp or 0,
            money or 0,
            last_daily_claim.isoformat() if last_daily_claim else None
        ))
    conn.commit()
    conn.close()

# Function to call the DeepSeek API
def get_deepseek_response(message_content, user):
    if user["role"] == "Gueux":
        MAX_TOKENS = 100
    else :
        MAX_TOKENS = 1000
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": message_content}],
        "max_tokens": MAX_TOKENS  
    }

    try:
        # Send the request to the API
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Désolé, je n'ai pas pu comprendre votre message. (Status Code: {response.status_code})"
    except Exception as e:
        # Print any exceptions that occur
        print(f"An error occurred while calling the DeepSeek API: {e}")
        return "Désolé, une erreur s'est produite lors de la communication avec l'API."

# Function to get a role by name, creating it if it doesn't exist
async def get_or_create_role(guild, role_name, color):
    role = discord.utils.get(guild.roles, name=role_name)
    if not role:
        role = await guild.create_role(name=role_name, color=color)
        await send_to_bot_channel(guild, f"Rôle '{role_name}' créé.")
    return role

# Function to send a message to the "bot" channel
async def send_to_bot_channel(guild, message):
    channel = discord.utils.get(guild.text_channels, name="bot")
    if channel:
        await channel.send(message)
    else:
        print(f"Le canal 'bot' n'existe pas sur le serveur {guild.name}.")

# Event: When a new user joins the server
@bot.event
async def on_member_join(member):
    guild = member.guild
    role_Gueux = await get_or_create_role(guild, "Gueux", discord.Color.dark_grey())
    await member.add_roles(role_Gueux)
    update_user_data(member.id, role='Gueux')
    await send_to_bot_channel(guild, f"{member.name} a reçu le rôle Gueux.")

# Dictionary to store the join time of users
user_join_times = {}

@bot.event
async def on_voice_state_update(member, before, after):
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

# Check if a user should be promoted
async def check_role_upgrade(member):
    user = get_user_data(member.id)
    if not user:
        return

    guild = member.guild
    role_Gueux = await get_or_create_role(guild, "Gueux", discord.Color.dark_grey())
    role_Chevalier = await get_or_create_role(guild, "Chevalier", discord.Color.gold())
    role_Baron = await get_or_create_role(guild, "Baron", discord.Color.purple())
    role_Duc = await get_or_create_role(guild, "Duc", discord.Color.dark_blue())
    
    if user["exp"] >= EXP_POUR_CHEVALIER and user["role"] == "Gueux":
        await member.remove_roles(role_Gueux)
        await member.add_roles(role_Chevalier)
        update_user_data(member.id, role="Chevalier")
        await send_to_bot_channel(guild, f"{member.mention} a été adoubé.")
    if user["exp"] >= EXP_POUR_BARON and user["role"] == "Chevalier":
        await member.remove_roles(role_Chevalier)
        await member.add_roles(role_Baron)
        update_user_data(member.id, role="Baron")
        await send_to_bot_channel(guild, f"{member.mention} a été promu Baron.")
    if user["exp"] >= EXP_POUR_DUC and user["role"] == "Baron":
        await member.remove_roles(role_Baron)
        await member.add_roles(role_Duc)
        update_user_data(member.id, role="Duc")
        await send_to_bot_channel(guild, f"{member.mention} a été promu Duc.")

# Check if a user has leveled up
async def check_level_upgrade(member):
    user = get_user_data(member.id)
    if not user:
        return

    new_level = user["exp"] // LEVEL_THRESHOLD

    if new_level > user["level"]:
        update_user_data(member.id, level=new_level)
        await send_to_bot_channel(member.guild, f"🎉 {member.mention} a atteint le niveau **{new_level}** ! Félicitations ! 🎉")

# Background task: Check for inactivity
@tasks.loop(hours=24)
async def check_inactivity():
    for guild in bot.guilds:
        role_Gueux = await get_or_create_role(guild, "Gueux", discord.Color.dark_grey())
        role_Chevalier = await get_or_create_role(guild, "Chevalier", discord.Color.gold())

        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE role = ?', ("Chevalier",))
        for user in c.fetchall():
            last_activity = datetime.fromisoformat(user[3])
            if (datetime.now() - last_activity).days >= INACTIVITE_JOURS:
                member = guild.get_member(user[0])
                if member:
                    await member.remove_roles(role_Chevalier)
                    await member.add_roles(role_Gueux)
                    update_user_data(user[0], role="Gueux")
                    await send_to_bot_channel(guild, f"{member.mention} est redevenu 'Gueux'.")
        conn.close()

""" User Commands """
@bot.command()
async def exp(ctx):
    user = get_user_data(ctx.author.id)
    if user:
        current_exp = user["exp"]
        next_level_exp = (user["level"] + 1) * LEVEL_THRESHOLD
        await ctx.send(f"{ctx.author.mention}, tu as actuellement {current_exp} XP. Il te faut {next_level_exp - current_exp} XP pour atteindre le prochain niveau ! \n (daily exp : {user['daily_exp']}/{DAILY_EXP_THRESHOLD})" )
    else:
        await ctx.send(f"{ctx.author.mention}, aucune donnée trouvée pour toi.")

@bot.command()
async def money(ctx):
    user = get_user_data(ctx.author.id)
    if user:
        await ctx.send(f"{ctx.author.mention}, you have {user['money']} $.")
    else:
        await ctx.send(f"{ctx.author.mention}, no data found for you.")

@bot.command()
async def bet(ctx, amount: int, choice: str):
    # Validate the choice (head or tail)
    choice = choice.lower()
    if choice not in ["head", "tail"]:
        await ctx.send(f"{ctx.author.mention}, please choose either 'head' or 'tail'.")
        return

    # Get the user's data
    user = get_user_data(ctx.author.id)
    if not user:
        await ctx.send(f"{ctx.author.mention}, no data found for you.")
        return

    # Check if the user has enough money
    if amount <= 0:
        await ctx.send(f"{ctx.author.mention}, the bet amount must be greater than 0.")
        return
    if user['money'] < amount:
        await ctx.send(f"{ctx.author.mention}, you don't have enough money to place this bet.")
        return

    # Simulate a coin flip
    coin_flip = random.choice(["head", "tail"])
    result_message = f"The coin landed on **{coin_flip}**."

    # Determine if the user won or lost
    if choice == coin_flip:
        winnings = amount * 2
        user['money'] += winnings
        result_message += f" Congratulations, {ctx.author.mention}! You won **{winnings}** $!"
    else:
        user['money'] -= amount
        result_message += f" Sorry, {ctx.author.mention}, you lost **{amount}** $."

    # Update the user's money in the database
    update_user_data(ctx.author.id, money=user['money'])

    # Send the result to the user
    await ctx.send(result_message)
    
@bot.command()
async def daily(ctx):
    user = get_user_data(ctx.author.id)
    if not user:
        await ctx.send(f"{ctx.author.mention}, no data found for you.")
        return

    now = datetime.now()
    last_claim = user.get("last_daily_claim")

    # Check if the user has already claimed their daily reward today
    if last_claim and last_claim.date() == now.date():
        next_claim_time = (last_claim + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        await ctx.send(f"{ctx.author.mention}, you have already claimed your daily reward today. You can claim again on **{next_claim_time}**.")
        return

    # Ensure user['money'] is not None
    if user['money'] is None:
        user['money'] = 0

    # Give the user 500 money
    user['money'] += 500
    user['last_daily_claim'] = now
    update_user_data(ctx.author.id, money=user['money'], last_daily_claim=user['last_daily_claim'])

    await ctx.send(f"{ctx.author.mention}, you claimed your daily reward of **500 $**! You now have **{user['money']} $**.")
    
@bot.command()
async def expvoice(ctx):
    await ctx.send(f"Current user join times in voice channels: {user_join_times}")
    print(user_join_times)
    
    
""" admin commands """
@bot.command()
async def admin(ctx, action: str, target: discord.Member, value: int):
    # Check if the user has the 'dev' role
    if 'dev' not in [role.name.lower() for role in ctx.author.roles]:
        await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
        return

    # Validate the action (setlevel or setmoney)
    action = action.lower()
    if action not in ["setlevel", "setmoney"]:
        await ctx.send(f"{ctx.author.mention}, invalid action. Use `setlevel` or `setmoney`.")
        return

    # Validate the value
    if value < 0:
        await ctx.send(f"{ctx.author.mention}, the value must be a positive number.")
        return

    # Get the target user's data
    target_user = get_user_data(target.id)
    if not target_user:
        await ctx.send(f"{ctx.author.mention}, no data found for {target.mention}.")
        return

    # Update the target user's data
    if action == "setlevel":
        update_user_data(target.id, level=value)
        await ctx.send(f"{ctx.author.mention}, set {target.mention}'s level to **{value}**.")
    elif action == "setmoney":
        update_user_data(target.id, money=value)
        await ctx.send(f"{ctx.author.mention}, set {target.mention}'s money to **{value}**.")
        
@bot.command()
async def bye(ctx):
    if 'dev' in [role.name.lower() for role in ctx.author.roles]:
        await ctx.send("Miaou ! Zzzzz....")

        for user_id, join_time in user_join_times.items():
            user = get_user_data(user_id)
            if user:
                time_spent = (datetime.now() - join_time).total_seconds() / 60
                if user["daily_exp"] < DAILY_EXP_THRESHOLD:
                    remaining_exp = DAILY_EXP_THRESHOLD - user["daily_exp"]
                    exp_gain = min(EXP_PAR_MINUTE_VOCAL * time_spent, remaining_exp)
                    exp_gain = int(exp_gain)

                    user["exp"] += exp_gain
                    user["daily_exp"] += exp_gain
                    user["last_activity"] = datetime.now()
                    update_user_data(user_id, exp=user["exp"], daily_exp=user["daily_exp"], last_activity=user["last_activity"], last_exp_gain_date=user["last_exp_gain_date"])

                    print(f"{user_id} gained {exp_gain} XP after leaving the voice channel.")
        
        await bot.close()
    else:
        await ctx.send("You do not have permission to stop the bot!")

""" Event Functions """
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
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
        update_user_data(**user)

    if user["last_exp_gain_date"].date().day != datetime.now().date().day:
        user["daily_exp"] = 0
        user["last_exp_gain_date"] = datetime.now()

    if user["daily_exp"] < DAILY_EXP_THRESHOLD:
        remaining_exp = DAILY_EXP_THRESHOLD - user["daily_exp"]
        exp_gain = min(EXP_PAR_MESSAGE, remaining_exp)

        user["exp"] += exp_gain
        user["daily_exp"] += exp_gain
        user["last_activity"] = datetime.now()
        update_user_data(user_id, exp=user["exp"], daily_exp=user["daily_exp"], last_activity=user["last_activity"], last_exp_gain_date=user["last_exp_gain_date"])
                 
    await check_role_upgrade(message.author)
    await check_level_upgrade(message.author)
    
    if message.author.bot:
        return
    
    if ("wtf" or "omg") in message.content.lower():
        emoji = discord.utils.get(message.guild.emojis, name="Chat_Cosi")
        if emoji:
            await message.add_reaction(emoji)
    
    if "quoi" in message.content.lower():
        emoji = discord.utils.get(message.guild.emojis, name="Chat_Cosi")
        await message.channel.send(f"feur {emoji}")
    
    if message.content.lower() == 'wiwiwi':
        await message.channel.send("wiwiwi", file=discord.File("wiwiwi.gif"))
    
    #Deepseek response to bot mention
    if bot.user in message.mentions:
        # Extract the message content without the mention
        message_content = message.content.replace(f"<@{bot.user.id}>", "").strip()
        
        # Get a response from DeepSeek
        response = get_deepseek_response(message_content, user)
        
        # Send the response back to the channel
        await message.channel.send(response)
    
    # Allow other commands to work
    await bot.process_commands(message)

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
                    last_daily_claim=None  # Initialize last_daily_claim
                )
                print(f"{member.name} a été ajouté à la base de données avec le rôle '{user_role}'.")

                if member.voice:
                    user_join_times[member.id] = datetime.now()

            else:
                if member.voice:
                    user_join_times[member.id] = datetime.now()

@bot.event
async def on_ready():
    print(bot.guilds)
    for guild in bot.guilds:
        await fetch_and_store_data(guild)
    check_inactivity.start()
    print(f"Bot connecté en tant que {bot.user}")

# Run the bot
bot.run(TOKEN)
