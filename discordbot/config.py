import discord
from discord.ext import commands
from datetime import timedelta
from google.cloud import secretmanager

# Configuration
with open("token.txt", "r") as file:
    TOKEN = file.read().strip()

def get_deepseek_api_key():
    client = secretmanager.SecretManagerServiceClient()
    name = "projects/discordbot-452223/secrets/deepseek-api-key/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

DEEPSEEK_API_KEY = get_deepseek_api_key()
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Experience and Leveling
EXP_PAR_MESSAGE = 10
EXP_PAR_MINUTE_VOCAL = 5
EXP_POUR_CHEVALIER = 700
EXP_POUR_BARON = 1400
EXP_POUR_DUC = 2100
INACTIVITE_JOURS = 7
LEVEL_THRESHOLD = 100
DAILY_EXP_THRESHOLD = 100

# Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Bot
bot = commands.Bot(command_prefix="!", intents=intents)