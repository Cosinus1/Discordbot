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

def create_item_embed(item, image_filename="item.png"):
    """
    Creates an embed for item details.
    """
    # Set the embed title and color
    embed = discord.Embed(title=item["name"], color=discord.Color.blue())

    # Add the item type to the description
    embed.description = f"Type: {item['type'].title()}"

    # Add rarity only if the item is not a consumable
    if item["type"] != "consumable":
        embed.description += f"\nRarity: {item['rarity'].title()}"

    # Add the price field
    embed.add_field(name="Price", value=f"{item['price']} gold", inline=False)

    # Add stats if the item has stats (for equipment)
    if "stats" in item and item["type"] != "consumable":
        embed.add_field(name="Stats", value="\n".join([f"{k}: {v}" for k, v in item["stats"].items()]), inline=False)

    # Add effect if the item is a consumable
    if item["type"] == "consumable" and "effect" in item:
        embed.add_field(name="Effect", value=f"Restores {item['effect']} health", inline=False)

    # Set the thumbnail image
    embed.set_thumbnail(url=f"attachment://{image_filename}")

    return embed

def create_stats_embed(player, display_name):
    """Create an embed for displaying player stats."""
    health = player.get("health", 0)
    attack = player.get("attack", 0)
    stats = player.get("stats", {})

    embed = discord.Embed(
        title=f"{display_name}'s Stats",
        color=discord.Color.blue()
    )

    # Add health and attack fields
    embed.add_field(name="❤️ Health", value=f"{health}", inline=True)
    embed.add_field(name="⚔️ Attack", value=f"{attack}", inline=True)

    # Add additional stats if they exist
    if stats:
        for stat, value in stats.items():
            embed.add_field(
                name=f"✨ {stat.replace('_', ' ').title()}",
                value=f"{value}",
                inline=True
            )

    return embed

def create_equipped_items_embed(player, display_name):
    """Create an embed for displaying equipped items."""
    equipped_items = player["equipped_items"]
    if not equipped_items:
        return None

    embed = discord.Embed(
        title=f"{display_name}'s Equipped Items",
        color=discord.Color.green()
    )

    # Add each equipped item to the embed
    for item in equipped_items.values():
        embed.add_field(
            name=f"🔹 {item['name']}",
            value=(
                f"**Type:** {item['type'].title()}\n"
                f"**Rarity:** {item['rarity'].title()}\n"
                f"**ID:** {item['id']}"
            ),
            inline=False
        )

    return embed

def create_hp_embed(player, display_name):
    """Create an embed for displaying the player's current health."""
    health = player.get("health", 0)
    max_health = player.get("stats", {}).get("max_hp", 100)

    embed = discord.Embed(
        title=f"{display_name}'s Health",
        color=discord.Color.red()
    )

    # Add health bar and current/max health
    embed.add_field(
        name="❤️ Health",
        value=create_health_bar(health, max_health),
        inline=False
    )

    return embed