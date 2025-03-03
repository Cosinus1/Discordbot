import discord
import requests
from config import bot, DAILY_EXP_THRESHOLD, EXP_PAR_MESSAGE, DEEPSEEK_API_KEY, DEEPSEEK_API_URL
from database import get_user_data, update_user_data
from datetime import datetime
from utils.roles_utils import check_role_upgrade
from utils.exp_utils import check_level_upgrade

async def start(message):
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