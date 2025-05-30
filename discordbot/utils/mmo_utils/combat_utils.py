import random

def calculate_damage(attacker, defender):
    """
    Calculate damage dealt by the attacker to the defender,
    taking into account all available stats from both participants.
    
    Args:
        attacker (dict): Attacker's stats
        defender (dict): Defender's stats
        
    Returns:
        tuple: (damage_amount, is_critical_hit)
    """
    # Get attacker's stats
    attack_value = attacker.get("attack", 0)
    attacker_stats = attacker.get("stats", {})
    
    # Get defender's stats
    defender_armor = defender.get("armor", 0)
    if defender_armor == 0:  # If no direct armor attribute
        defender_armor = defender.get("stats", {}).get("armor", 0)
    
    # Get special combat stats
    armor_penetration = attacker_stats.get("armor_penetration", 0)
    critical_chance = attacker_stats.get("critical_chance", 0)
    
    # Calculate effective armor after penetration
    effective_armor = defender_armor * (1 - armor_penetration)
    
    # Base damage calculation
    base_damage = max(1, attack_value - effective_armor)
    
    # Round to 2 decimal places
    base_damage = round(base_damage, 2)
    
    # Critical hit check
    is_critical = random.random() < critical_chance
    if is_critical:
        base_damage *= 2
        base_damage = round(base_damage, 2)
    
    return base_damage, is_critical

def apply_combat_effects(attacker, defender, damage_dealt):
    """
    Apply additional combat effects like lifesteal, stuns, etc.
    
    Args:
        attacker (dict): Attacker's stats
        defender (dict): Defender's stats
        damage_dealt (float): Amount of damage that was dealt
        
    Returns:
        dict: Effects applied with their values
    """
    effects = {}
    attacker_stats = attacker.get("stats", {})
    
    # Lifesteal effect
    lifesteal = attacker_stats.get("lifesteal", 0)
    if lifesteal > 0:
        heal_amount = round(damage_dealt * lifesteal, 2)
        # Update attacker's health directly
        new_health = min(
            attacker.get("max_health", attacker.get("health", 100)), 
            attacker.get("health", 0) + heal_amount
        )
        attacker["health"] = round(new_health, 2)
        effects["lifesteal"] = heal_amount
    
    # Stun effect
    stunt_chance = attacker_stats.get("stunt_chance", 0)
    effects["stunned"] = random.random() < stunt_chance
    
    # Parry effect
    parry_chance = defender.get("stats", {}).get("parry_chance", 0)
    effects["parried"] = random.random() < parry_chance
    
    return effects