import sqlite3
from datetime import datetime
import json

def init_db():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    # Create the users table (Discord-related data)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            exp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 0,
            last_activity TEXT,
            role TEXT DEFAULT 'Gueux',
            last_exp_gain_date TEXT,
            daily_exp INTEGER DEFAULT 0,
            money INTEGER DEFAULT 0,
            last_daily_claim TEXT
        )
    ''')

    # Create the players table (MMORPG-related data)
    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            health INTEGER DEFAULT 100,
            attack INTEGER DEFAULT 10,
            stats TEXT DEFAULT {},
            inventory TEXT,
            equipped_items TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    conn.commit()
    conn.close()

"""///////////////////////GETTERS//////////////////////"""

def get_user_data(user_id):
    """Retrieve Discord-related user data."""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return {
            "user_id": user[0],
            "exp": user[1],
            "level": user[2],
            "last_activity": datetime.fromisoformat(user[3]),
            "role": user[4],
            "last_exp_gain_date": datetime.fromisoformat(user[5]) if user[5] else None,
            "daily_exp": user[6],
            "money": user[7] if user[7] is not None else 0,
            "last_daily_claim": datetime.fromisoformat(user[8]) if user[8] else None
        }
    return None

def get_all_users():
    """Retrieve all users from the database."""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    users = c.fetchall()
    conn.close()
    
    # Return a list of user IDs
    return [{"id": user[0]} for user in users]

def get_all_players():
    """Retrieve all players from database"""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT user_id FROM players')
    users = c.fetchall()
    conn.close()
    
    # Return a list of user IDs
    return [{"id": user[0]} for user in users]
    
def player_exists(user_id):
    """Check if a player entry exists for the user."""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT 1 FROM players WHERE user_id = ?', (user_id,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

def get_player_data(user_id):
    """Retrieve MMORPG-related player data."""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM players WHERE user_id = ?', (user_id,))
    player = c.fetchone()
    conn.close()
    if player:
        return {
            "user_id": player[0],
            "health": player[1],
            "attack": player[2],
            "stats": json.loads(player[3]) if player[3] else {},  # Deserialize stats
            "inventory": json.loads(player[4]) if player[4] else [],
            "equipped_items": json.loads(player[5]) if player[5] else {}
        }
    return None

def get_player_inventory(user_id):
    """Retrieve only the user's inventory."""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT inventory FROM players WHERE user_id = ?', (user_id,))
    inventory_json = c.fetchone()
    conn.close()
    
    if inventory_json and inventory_json[0]:
        return json.loads(inventory_json[0])  # Deserialize JSON
    return []

def get_player_equipped_items(user_id):
    """Retrieve only the user's equipped items."""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT equipped_items FROM users WHERE user_id = ?', (user_id,))
    equipped_items_json = c.fetchone()
    conn.close()
    
    if equipped_items_json and equipped_items_json[0]:
        return json.loads(equipped_items_json[0])  # Deserialize JSON
    return {}

def get_player_stat(user_id, stat_name):
    """Retrieve a specific stat for a player."""
    player = get_player_data(user_id)
    if player:
        return player["stats"].get(stat_name, 0)  # Default to 0 if stat doesn't exist
    return 0


"""///////////////////////SETTERS//////////////////////"""

def create_player(user_id):
    """Create a new player entry in the players table."""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('INSERT INTO players (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()


def update_user_data(user_id, **kwargs):
    """Update Discord-related user data. Creates a new user if the user_id doesn't exist."""
    if not kwargs:
        raise ValueError("No fields to update provided.")

    valid_columns = [
        "exp", "level", "last_activity", "role", 
        "last_exp_gain_date", "daily_exp", "money", "last_daily_claim"
    ]
    updates = []
    params = []

    for key, value in kwargs.items():
        if key not in valid_columns:
            raise ValueError(f"Invalid column name: {key}")
        if value is not None:
            # Convert datetime to ISO format string
            if isinstance(value, datetime):
                value = value.isoformat()
            updates.append(f"{key} = ?")
            params.append(value)

    if not updates:
        raise ValueError("No valid fields to update.")

    params.append(user_id)
    update_query = f'UPDATE users SET {", ".join(updates)} WHERE user_id = ?'

    with sqlite3.connect('user_data.db') as conn:
        c = conn.cursor()

        # Check if the user exists
        c.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        user_exists = c.fetchone()

        if user_exists:
            # Update the existing user
            c.execute(update_query, params)
        else:
            # Insert a new user with default values
            default_values = {
                "exp": 0,
                "level": 0,
                "last_activity": datetime.now().isoformat(),
                "role": "Gueux",
                "last_exp_gain_date": datetime.now().isoformat(),
                "daily_exp": 0,
                "money": 0,
                "last_daily_claim": None
            }

            # Merge default values with provided kwargs
            for key, value in kwargs.items():
                if key in valid_columns:
                    default_values[key] = value.isoformat() if isinstance(value, datetime) else value

            # Prepare the insert query
            columns = ", ".join(default_values.keys())
            placeholders = ", ".join("?" * len(default_values))
            insert_query = f'INSERT INTO users (user_id, {columns}) VALUES (?, {placeholders})'

            # Execute the insert query
            c.execute(insert_query, (user_id, *default_values.values()))

        conn.commit()

def update_player_data(user_id, **kwargs):
    """Update MMORPG-related player data."""
    if not kwargs:
        raise ValueError("No fields to update provided.")

    valid_columns = [
        "health", "inventory", "equipped_items", "attack", "stats"
    ]
    updates = []
    params = []

    for key, value in kwargs.items():
        if key not in valid_columns:
            raise ValueError(f"Invalid column name: {key}")
        if value is not None:
            # Serialize lists or dicts to JSON strings
            if isinstance(value, (list, dict)):
                value = json.dumps(value)
            updates.append(f"{key} = ?")
            params.append(value)

    if not updates:
        raise ValueError("No valid fields to update.")

    params.append(user_id)
    query = f'UPDATE players SET {", ".join(updates)} WHERE user_id = ?'

    with sqlite3.connect('user_data.db') as conn:
        c = conn.cursor()
        c.execute(query, params)
        conn.commit()    
        
def update_player_equipped_items(user_id, equipped_items):
    """Update only the user's equipped items."""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('UPDATE players SET equipped_items = ? WHERE user_id = ?', (json.dumps(equipped_items), user_id))
    conn.commit()
    conn.close()
    
def update_player_inventory(user_id, inventory):
    """Update only the user's inventory."""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('UPDATE players SET inventory = ? WHERE user_id = ?', (json.dumps(inventory), user_id))
    conn.commit()
    conn.close()

def set_player_stat(user_id, stat_name, value):
    """Set a specific stat for a player."""
    player = get_player_data(user_id)
    if player:
        player["stats"][stat_name] = value
        update_player_data(user_id, stats=player["stats"])

def increment_player_stat(user_id, stat_name, amount):
    """Increment a specific stat for a player."""
    player = get_player_data(user_id)
    if player:
        # Deal case stats other than hp or ad
        if stat_name != ("health" or "attack"):
            player["stats"][stat_name] = player["stats"].get(stat_name, 0) + amount
            update_player_data(user_id, stats=player["stats"])
        # Deal hp or ad case
        else:
            player[stat_name]+= amount
            update_player_data(user_id, player[stat_name])