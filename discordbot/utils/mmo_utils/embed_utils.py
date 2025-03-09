import discord

def create_combat_embed(player, monster, image_filename="goblin_vecto.png"):
    """
    Creates an embed for combat status.
    """
    embed = discord.Embed(title="Combat", color=discord.Color.red())
    
    # Player stats
    embed.add_field(
        name="Player Stats",
        value=(
            f"❤️ Health: {create_health_bar(player['health'], 100)}\n"
            f"⚔️ Attack: {player['attack']}\n"
            f"🛡️ Armor: {player.get('stats', {}).get('armor', 0)}\n"
            f"💥 Critical Chance: {player.get('stats', {}).get('critical_chance', 0)}%"
        ),
        inline=False,
    )

    # Monster stats
    embed.add_field(
        name="Monster Stats",
        value=(
            f"❤️ Health: {create_health_bar(monster['health'], monster['max_health'])}\n"
            f"⚔️ Attack: {monster['attack']}\n"
            f"🛡️ Armor: {monster.get('stats', {}).get('armor', 0)}"
        ),
        inline=False,
    )

    # Center the monster's image
    embed.set_image(url=f"attachment://{image_filename}")

    return embed

def create_health_bar(current, max):
    """
    Creates a health bar using emojis.
    """
    filled = "🟩" * int((current / max) * 10)
    empty = "🟥" * (10 - len(filled))
    return f"{filled}{empty} {current}/{max}"