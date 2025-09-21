# database.py
import sqlite3
import json
from typing import Dict, Any

def init_db():
    """Initializes the database and creates the game_rooms table if it doesn't exist."""
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_rooms (
            room_id TEXT PRIMARY KEY,
            game_state TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def get_game_state(room_id: str) -> Dict[str, Any] | None:
    """Fetches the game state for a given room_id from the database."""
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()
    cursor.execute('SELECT game_state FROM game_rooms WHERE room_id = ?', (room_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0]) # Convert JSON string back to Python dict
    return None

def update_game_state(room_id: str, new_state: Dict[str, Any]):
    """Creates or updates the game state for a given room_id in the database."""
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()
    # Use INSERT OR REPLACE to handle both creation of new rooms and updates to existing ones
    cursor.execute(
        'INSERT OR REPLACE INTO game_rooms (room_id, game_state) VALUES (?, ?)',
        (room_id, json.dumps(new_state)) # Convert Python dict to JSON string for storage
    )
    conn.commit()
    conn.close()