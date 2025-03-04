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
            armor INTEGER DEFAULT 0,
            inventory TEXT,
            equipped_items TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    # Add columns to users table if they don't exist
    c.execute('PRAGMA table_info(users)')
    columns = [column[1] for column in c.fetchall()]

    if 'money' not in columns:
        c.execute('ALTER TABLE users ADD COLUMN money INTEGER DEFAULT 0')

    if 'last_daily_claim' not in columns:
        c.execute('ALTER TABLE users ADD COLUMN last_daily_claim TEXT')
    
    if 'inventory' in columns:
        # Step 1: Create a new table without the inventory column
        c.execute('''
            CREATE TABLE new_users (
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

        # Step 2: Copy data from the old table to the new table
        c.execute('''
            INSERT INTO new_users (user_id, exp, level, last_activity, role, last_exp_gain_date, daily_exp, money, last_daily_claim)
            SELECT user_id, exp, level, last_activity, role, last_exp_gain_date, daily_exp, money, last_daily_claim
            FROM users
        ''')

        # Step 3: Drop the old table
        c.execute('DROP TABLE users')

        # Step 4: Rename the new table to the original table name
        c.execute('ALTER TABLE new_users RENAME TO users')

    # Add other columns to users table if they don't exist
    if 'money' not in columns:
        c.execute('ALTER TABLE users ADD COLUMN money INTEGER DEFAULT 0')

    # Add columns to players table if they don't exist
    c.execute('PRAGMA table_info(players)')
    columns = [column[1] for column in c.fetchall()]

    if 'health' not in columns:
        c.execute('ALTER TABLE players ADD COLUMN health INTEGER DEFAULT 100')

    if 'attack' not in columns:
        c.execute('ALTER TABLE players ADD COLUMN attack INTEGER DEFAULT 10')

    if 'armor' not in columns:
        c.execute('ALTER TABLE players ADD COLUMN armor INTEGER DEFAULT 0')

    if 'inventory' not in columns:
        c.execute('ALTER TABLE players ADD COLUMN inventory TEXT')

    if 'equipped_items' not in columns:
        c.execute('ALTER TABLE players ADD COLUMN equipped_items TEXT')

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
            "armor": player[3],
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

"""///////////////////////SETTERS//////////////////////"""

def update_user_data(user_id, **kwargs):
    """Update Discord-related user data."""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    updates = []
    params = []
    for key, value in kwargs.items():
        if value is not None:
            updates.append(f"{key} = ?")
            params.append(value.isoformat() if isinstance(value, datetime) else value)
    params.append(user_id)
    c.execute(f'UPDATE users SET {", ".join(updates)} WHERE user_id = ?', params)
    conn.commit()
    conn.close()

def create_player(user_id):
    """Create a new player entry in the players table."""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('INSERT INTO players (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()
    
def update_player_data(user_id, **kwargs):
    """Update MMORPG-related player data."""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    updates = []
    params = []
    for key, value in kwargs.items():
        if value is not None:
            updates.append(f"{key} = ?")
            params.append(json.dumps(value) if isinstance(value, (list, dict)) else value)
    params.append(user_id)
    c.execute(f'UPDATE players SET {", ".join(updates)} WHERE user_id = ?', params)
    conn.commit()
    conn.close()
    
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
