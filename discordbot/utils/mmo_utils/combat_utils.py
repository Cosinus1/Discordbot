import random

def calculate_damage(attacker, defender):
    """Calculate damage dealt by the attacker to the defender."""
    base_damage = attacker["attack"] - defender.get("defense", 0)
    return max(1, base_damage)  # Ensure at least 1 damage

def simulate_combat(player, monster):
    """Simulate combat between the player and a monster."""
    combat_log = []
    while player["health"] > 0 and monster["health"] > 0:
        # Player attacks monster
        player_damage = calculate_damage(player, monster)
        monster["health"] -= player_damage
        combat_log.append(f"You dealt {player_damage} damage to the {monster['name']}!")

        if monster["health"] <= 0:
            break

        # Monster attacks player
        monster_damage = calculate_damage(monster, player)
        player["health"] -= monster_damage
        combat_log.append(f"The {monster['name']} dealt {monster_damage} damage to you!")

    return combat_log, player["health"] > 0