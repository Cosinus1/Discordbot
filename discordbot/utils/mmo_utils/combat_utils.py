def calculate_damage(attacker, defender):
    # Simple damage calculation formula
    base_damage = attacker["attack"] - defender["defense"]
    return max(1, base_damage)  # Ensure at least 1 damage