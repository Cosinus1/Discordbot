import random

def calculate_damage(attacker, defender):
    """Calculate damage dealt by the attacker to the defender."""
    # Base damage calculation
    base_damage = attacker.get("attack", 0) - (defender.get("stats", {}).get("armor", 0)-(attacker.get("stats", {}).get("armor_penetration", 0)))
    base_damage = max(1, base_damage)  # Ensure at least 1 damage

    # Critical hit chance
    critical_chance = attacker.get("stats", {}).get("critical_chance", 0)
    if random.random() < critical_chance:
        base_damage *= 2  # Double damage on critical hit
        return base_damage, True  # Return damage and critical hit flag

    return base_damage, False  # Return damage and no critical hit

def simulate_combat(player, monster):
    """Simulate combat between the player and a monster."""
    combat_log = []
    while player["health"] > 0 and monster["health"] > 0:
        # Player attacks monster
        player_damage, is_critical = calculate_damage(player, monster)
        monster["health"] -= player_damage
        combat_log.append(
            f"You dealt {player_damage} damage to the {monster['name']}!"
            + (" **Critical Hit!**" if is_critical else "")
        )

        # Apply lifesteal
        lifesteal = player.get("stats", {}).get("lifesteal", 0)
        if lifesteal > 0:
            health_gained = int(player_damage * lifesteal)
            player["health"] = min(100, player["health"] + health_gained)
            combat_log.append(f"You gained {health_gained} health from lifesteal!")
                  
        # Check if monster is stunned
        stunt_chance = player.get("stats", {}).get("stunt_chance", 0)
        is_monster_stunted = False
        if random.random() < stunt_chance:
            combat_log.append(f"You stunned {monster['name']}!")
            is_monster_stunted = True
            
        # Check if monster is dead
        if monster["health"] <= 0:
            break

        # Monster attacks player
        if not is_monster_stunted:
            monster_damage, is_critical = calculate_damage(monster, player)
            
            # Check if the attack is parried
            parry_chance = player.get("stats", {}).get("parry_chance", 0)
            if random.random() < parry_chance:
                combat_log.append("You parried the attack!")
            else:
                player["health"] -= monster_damage
                combat_log.append(
                    f"The {monster['name']} dealt {monster_damage} damage to you!"
                    + (" **Critical Hit!**" if is_critical else "")
                )
    
            # Check if player is stunned
            stunt_chance = monster.get("stats", {}).get("stunt_chance", 0)
            if random.random() < stunt_chance:
                combat_log.append(f"The {monster['name']} stunned you! You skip your next turn.")
                continue  # Skip player's next turn

    return combat_log, player["health"]