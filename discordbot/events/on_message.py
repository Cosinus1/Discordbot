import discord
import requests
from config import bot, DAILY_EXP_THRESHOLD, EXP_PAR_MESSAGE, DEEPSEEK_API_KEY, DEEPSEEK_API_URL
from database import get_user_data, update_user_data
from datetime import datetime
from utils.roles_utils import check_role_upgrade
from utils.exp_utils import check_level_upgrade

MESSAGE_CONTENT_LIMIT = 11

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
    
    message_content = message.content.lower()

    if ("wtf" or "omg") in message_content:
        emoji = discord.utils.get(message.guild.emojis, name="Chat_Cosi")
        if emoji:
            await message.add_reaction(emoji)

    if "quoi" in message_content:
        # Check if "quoi is actually at the end of  the sentence"
        message_content = message.content.lower().strip()
        # Remove punctuation from the end for better matching
        while message_content and message_content[-1] in ".,!?;:":
            message_content = message_content[:-1]
            
        # Check if the last word is "quoi"
        if message_content.split()[-1] == "quoi":
            emoji = discord.utils.get(message.guild.emojis, name="Chat_Cosi")
            await message.channel.send(f"feur {emoji}")
        
    if message_content == 'wiwiwi':
        await message.channel.send("wiwiwi", file=discord.File("wiwiwi.gif"))
    
    # Modify the DeepSeek response part
    if bot.user in message.mentions:
        # Extract the message content without the mention
        message_content = message.content.replace(f"<@{bot.user.id}>", "").strip()
        
        # Get the previous messages for context
        context_messages = []
        async for msg in message.channel.history(limit=MESSAGE_CONTENT_LIMIT):
            if msg.id != message.id:  # Skip the current message
                # Add recent conversation history as separate messages to maintain the dialogue structure
                author = msg.author   
                roles = "bot" if author.bot else "user"
                #roles += " admin" if msg.author.admin else None
                roles += " master" if 'dev' in [role.name.lower() for role in author.roles] else None
                context_messages.insert(0, {"author": author.display_name, "roles": roles, "content": msg.content})
                if len(context_messages) >= MESSAGE_CONTENT_LIMIT-1:
                    break
        
        # Get a response from DeepSeek with context
        response = await get_deepseek_response(message_content, user, context_messages)
        
        # Send the response back to the channel
        await message.reply(response)
        
    # Allow other commands to work
    await bot.process_commands(message)
    
# Function to call the DeepSeek API
async def get_deepseek_response(message_content, user, context_messages=None):
    if user["role"] == "Gueux":
        MAX_TOKENS = 100
    else:
        MAX_TOKENS = 1000
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = []
    
    # Add system message with instructions and context
    system_prompt = """Tu es Méchatnicien, un assistant intelligent et sympathique sur un serveur Discord.
    Tu dois répondre aux messages des utilisateurs de manière utile. tu peux adapter ton caractère à la situation.
    Quelques règles importantes:
    - Adapte la longueur de tes réponses au nombre de tokens maximums disponibles.
    - N'hésite pas à être direct et aller droit au but.
    - Si tu reçois des messages de contexte, utilise-les seulement s'ils sont pertinents pour comprendre la question actuelle.
    - Chaque conversation est indépendante - ne présume pas que les nouvelles questions sont liées aux précédentes.
    - Évalue l'importance réelle de chaque message de contexte et ignore ceux qui semblent hors-sujet.
    - Reste naturel dans tes réponses, sans répéter ton nom ou tes paramètres.
    - Adapte ton ton et ton style à l'ambiance de la conversation."""

    messages.append({"author":"system", "role": "system","max_tokens": MAX_TOKENS, "content": system_prompt})
    
    # Add context messages if available
    if context_messages and len(context_messages) > 0:
        messages.append(context_messages)
    # Add the user's current message
    messages.append({"author": author, "role": "user", "content": message_content})
    
    data = {
        "model": "deepseek-chat",
        "messages": messages,
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