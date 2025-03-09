import discord

def create_combat_embed(player, monster):
    """
    Creates an embed for combat status.
    """
    embed = discord.Embed(title="Combat", color=discord.Color.red())
    embed.add_field(name="Player", value=f"❤️ {create_health_bar(player['health'], 100)}\n⚔️ Attack: {player['attack']}", inline=True)
    embed.add_field(name="Monster", value=f"❤️ {create_health_bar(monster['health'], monster['max_health'])}\n⚔️ Attack: {monster['attack']}", inline=True)
    embed.set_image(url="data/mmo/PNG/goblin_vecto.png")  # Use the monster's image URL
    return embed

def create_item_embed(item):
    """
    Creates an embed for item details.
    """
    embed = discord.Embed(title=item["name"], description=f"Type: {item['type'].title()}\nRarity: {item['rarity'].title()}", color=discord.Color.blue())
    embed.add_field(name="Price", value=f"{item['price']} gold", inline=False)
    if "stats" in item:
        embed.add_field(name="Stats", value="\n".join([f"{k}: {v}" for k, v in item["stats"].items()]), inline=False)
    embed.set_thumbnail(url="data/mmo/PNG/item.png")  # Use the item's image URL
    return embed

def create_health_bar(current, max):
    """
    Creates a health bar using emojis.
    """
    filled = "🟩" * int((current / max) * 10)
    empty = "🟥" * (10 - len(filled))
    return f"{filled}{empty} {current}/{max}"