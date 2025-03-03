import discord
from discord.ext import commands
from config import LEVEL_THRESHOLD, DAILY_EXP_THRESHOLD, EXP_PAR_MINUTE_VOCAL
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
async def xp(ctx): #fk krol
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

@commands.command()
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

@commands.command()
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

@commands.command()
async def send(ctx, recipient: discord.Member, amount: int):
    # Vérifier que le montant est positif
    if amount <= 0:
        await ctx.send(f"{ctx.author.mention}, le montant doit être supérieur à 0.")
        return

    # Récupérer les données de l'utilisateur actuel (expéditeur)
    sender = get_user_data(ctx.author.id)
    if not sender:
        await ctx.send(f"{ctx.author.mention}, aucune donnée trouvée pour vous.")
        return

    # Vérifier que l'expéditeur a suffisamment d'argent
    if sender['money'] < amount:
        await ctx.send(f"{ctx.author.mention}, vous n'avez pas assez d'argent pour envoyer {amount} $.")
        return

    # Récupérer les données du destinataire
    recipient_data = get_user_data(recipient.id)
    if not recipient_data:
        await ctx.send(f"{ctx.author.mention}, aucune donnée trouvée pour {recipient.mention}.")
        return

    # Retirer l'argent de l'expéditeur
    sender['money'] -= amount
    update_user_data(ctx.author.id, money=sender['money'])

    # Ajouter l'argent au destinataire
    recipient_data['money'] += amount
    update_user_data(recipient.id, money=recipient_data['money'])

    # Envoyer un message de confirmation
    await ctx.send(f"{ctx.author.mention} a envoyé {amount} $ à {recipient.mention}.")

@commands.command()
async def roll(ctx, value: int):
    try:
        # Vérifier que le dé a au moins 2 faces
        if value <= 2:
            await ctx.send(f"{ctx.author.mention}, le dé doit avoir au moins 2 faces.")
            return

        # Générer un résultat aléatoire
        result = random.randint(1, value)

        # Envoyer le résultat
        await ctx.send(f"{ctx.author.mention} a lancé un roll {value} et a obtenu : **{result}** !")
    except Exception as e:
        await ctx.send(f"{ctx.author.mention}, une erreur s'est produite : {e}")