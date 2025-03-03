import json
import random

def get_monster():
    with open("data/mmo/monsters.json", "r") as file:
        monsters = json.load(file)
    return random.choice(monsters)