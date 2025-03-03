import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

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

    # Add columns if they don't exist
    c.execute('PRAGMA table_info(users)')
    columns = [column[1] for column in c.fetchall()]

    if 'money' not in columns:
        c.execute('ALTER TABLE users ADD COLUMN money INTEGER DEFAULT 0')

    if 'last_daily_claim' not in columns:
        c.execute('ALTER TABLE users ADD COLUMN last_daily_claim TEXT')

    conn.commit()
    conn.close()

def get_user_data(user_id):
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

def update_user_data(user_id, **kwargs):
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