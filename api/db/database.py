import sqlite3
import json
from typing import Any, Optional, Dict, List, Tuple
import os

DB_PATH = "bot.db"


class Database:
    """A class to manage all CRUD operations for the bot's SQLite database."""

    def __init__(self, path: str = DB_PATH):
        """Initializes the Database manager."""
        self.db_path = path
        self._init_db()

    def _parse_json_value(self, value: Any) -> Any:
        """
        Parses a value from a JSON column. If it's a string, it's decoded.
        Otherwise, it's assumed to be a valid Python type (int, float, bool).
        """
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                # If it's a string that isn't valid JSON, return it as-is.
                return value
        # If it's not a string (e.g., float, int), return it directly.
        return value

    def _get_connection(self):
        """Returns a new database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;") # Ensure foreign key constraints are enforced
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes the database and creates tables if they don't exist."""
        with self._get_connection() as conn:
            # Config
            conn.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value JSON NOT NULL
                );
            """)
            # Captions
            conn.execute("""
                CREATE TABLE IF NOT EXISTS captions (
                    message_id TEXT PRIMARY KEY,
                    caption TEXT NOT NULL
                );
            """)
            conn.commit()
            # Servers
            conn.execute("""
                CREATE TABLE IF NOT EXISTS servers (
                    server_id TEXT PRIMARY KEY,
                    server_name TEXT NOT NULL,
                    description TEXT,
                    instruction TEXT
                );
            """)
            # Channels
            conn.execute("""
                CREATE TABLE IF NOT EXISTS channels (
                    channel_id TEXT PRIMARY KEY,
                    server_id TEXT NOT NULL,
                    server_name TEXT NOT NULL,
                    data JSON NOT NULL,
                    FOREIGN KEY (server_id) REFERENCES servers(server_id) ON DELETE CASCADE
                );
            """)
            # Characters
            conn.execute("""
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    data JSON NOT NULL
                );
            """)
            # Character Triggers
            conn.execute("""
                CREATE TABLE IF NOT EXISTS character_triggers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INTEGER NOT NULL,
                    trigger TEXT NOT NULL,
                    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
                );
            """)
            # Presets
            conn.execute("""
                CREATE TABLE IF NOT EXISTS presets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    prompt_template TEXT
                );
            """)
            conn.commit()

    # ------------------------------------------------------
    # Helper for dynamic updates
    # ------------------------------------------------------
    def _update_record(self, table_name: str, identifier_col: str, identifier_val: Any, **kwargs):
        """Generic helper to update any record in any table."""
        if not kwargs:
            return # Nothing to update
        
        # JSON fields need to be dumped to string
        for key, value in kwargs.items():
            if isinstance(value, (dict, list)):
                kwargs[key] = json.dumps(value)
        
        fields = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = tuple(kwargs.values()) + (identifier_val,)
        
        with self._get_connection() as conn:
            query = f"UPDATE {table_name} SET {fields} WHERE {identifier_col} = ?"
            conn.execute(query, values)
            conn.commit()

    # ------------------------------------------------------
    # Config (Key-Value Store)
    # ------------------------------------------------------
    def set_config(self, key: str, value: Any):
        """Create or update a configuration key-value pair."""
        with self._get_connection() as conn:
            # No change here, this was always correct.
            conn.execute("REPLACE INTO config (key, value) VALUES (?, ?)", (key, json.dumps(value)))
            conn.commit()

    def get_config(self, key: str) -> Optional[Any]:
        """Read a configuration value by its key."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT value FROM config WHERE key = ?", (key,)).fetchone()
            # --- MODIFIED LINE ---
            return self._parse_json_value(row["value"]) if row else None
            
    def list_configs(self) -> Dict[str, Any]:
        """List all configuration key-value pairs."""
        with self._get_connection() as conn:
            rows = conn.execute("SELECT key, value FROM config").fetchall()
            # --- MODIFIED LINE ---
            return {row["key"]: self._parse_json_value(row["value"]) for row in rows}

    def delete_config(self, key: str):
        # ... (this is the same) ...
        with self._get_connection() as conn:
            conn.execute("DELETE FROM config WHERE key = ?", (key,))
            conn.commit()

    # ------------------------------------------------------
    # Servers
    # ------------------------------------------------------
    def create_server(self, server_id: str, server_name: str, description: Optional[str] = None, instruction: Optional[str] = None):
        """Create a new server record."""
        with self._get_connection() as conn:
            conn.execute("INSERT INTO servers (server_id, server_name, description, instruction) VALUES (?, ?, ?, ?)",
                         (server_id, server_name, description, instruction))
            conn.commit()

    def get_server(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Read a server's data by its ID."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM servers WHERE server_id = ?", (server_id,)).fetchone()
            return dict(row) if row else None
            
    def update_server(self, server_id: str, **kwargs):
        """Update a server's data (e.g., server_name, description)."""
        self._update_record("servers", "server_id", server_id, **kwargs)

    def delete_server(self, server_id: str):
        """Delete a server and its associated channels."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM servers WHERE server_id = ?", (server_id,))
            conn.commit()

    def list_servers(self) -> List[Dict[str, Any]]:
        """List all servers."""
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM servers").fetchall()
            return [dict(row) for row in rows]

    # ------------------------------------------------------
    # Channels
    # ------------------------------------------------------
    def create_channel(self, channel_id: str, server_id: str, server_name: str, data: Dict[str, Any]):
        """Create a new channel record."""
        with self._get_connection() as conn:
            conn.execute("INSERT INTO channels (channel_id, server_id, server_name, data) VALUES (?, ?, ?, ?)",
                         (channel_id, server_id, server_name, json.dumps(data)))
            conn.commit()
    
    def get_channel(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Read a channel's data by its ID."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM channels WHERE channel_id = ?", (channel_id,)).fetchone()
            if not row:
                return None
            channel = dict(row)
            channel['data'] = json.loads(channel['data'])
            return channel
            
    def update_channel(self, channel_id: str, **kwargs):
        """Update a channel's data (e.g., server_name, data)."""
        self._update_record("channels", "channel_id", channel_id, **kwargs)

    def delete_channel(self, channel_id: str):
        """Delete a channel record."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
            conn.commit()

    def list_channels(self) -> List[Dict[str, Any]]:
        """List all channels across all servers."""
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM channels").fetchall()
            channels = []
            for row in rows:
                channel = dict(row)
                channel['data'] = json.loads(channel['data'])
                channels.append(channel)
            return channels
        
    def list_channels_for_server(self, server_id: str) -> List[Dict[str, Any]]:
        """List all channels for a specific server by its ID."""
        with self._get_connection() as conn:
            # Use a WHERE clause to filter by server_id
            rows = conn.execute("SELECT * FROM channels WHERE server_id = ?", (server_id,)).fetchall()
            channels = []
            for row in rows:
                channel = dict(row)
                # The 'data' column is a JSON string, so we need to parse it
                channel['data'] = json.loads(channel['data'])
                channels.append(channel)
            return channels

    # ------------------------------------------------------
    # Characters & Triggers
    # ------------------------------------------------------
    def create_character(self, name: str, data: Dict[str, Any], triggers: Optional[List[str]] = None) -> int:
        """Create a new character and optionally add its trigger words."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO characters (name, data) VALUES (?, ?)", (name, json.dumps(data)))
            char_id = cur.lastrowid
            if triggers:
                trigger_data = [(char_id, trigger) for trigger in triggers]
                cur.executemany("INSERT INTO character_triggers (character_id, trigger) VALUES (?, ?)", trigger_data)
            conn.commit()
            return char_id

    def get_character(self, name: str) -> Optional[Dict[str, Any]]:
        """Read a character's data and triggers by name."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT id, data FROM characters WHERE name = ?", (name,)).fetchone()
            if not row: return None
            
            char_id = row["id"]
            triggers = [r["trigger"] for r in conn.execute("SELECT trigger FROM character_triggers WHERE character_id = ?", (char_id,)).fetchall()]
            return {"id": char_id, "name": name, "data": json.loads(row["data"]), "triggers": triggers}

    def update_character(self, name: str, **kwargs):
        """Update a character's data (e.g., data)."""
        self._update_record("characters", "name", name, **kwargs)

    def delete_character(self, name: str):
        """Delete a character and its associated triggers."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM characters WHERE name = ?", (name,))
            conn.commit()

    def list_characters(self) -> List[Dict[str, Any]]:
        """List all characters with their data and triggers."""
        with self._get_connection() as conn:
            chars = [dict(row) for row in conn.execute("SELECT id, name, data FROM characters").fetchall()]
            for char in chars:
                char['data'] = json.loads(char['data'])
                triggers = [r["trigger"] for r in conn.execute("SELECT trigger FROM character_triggers WHERE character_id = ?", (char["id"],)).fetchall()]
                char['triggers'] = triggers
        return chars
    
    def update_character_triggers(self, character_id: int, triggers: List[str]):
        """
        Replaces all triggers for a given character.
        Deletes existing triggers and inserts the new list.
        """
        with self._get_connection() as conn:
            cur = conn.cursor()
            # Delete old triggers first
            cur.execute("DELETE FROM character_triggers WHERE character_id = ?", (character_id,))
            # Insert new ones if any are provided
            if triggers:
                trigger_data = [(character_id, trigger) for trigger in triggers]
                cur.executemany("INSERT INTO character_triggers (character_id, trigger) VALUES (?, ?)", trigger_data)
            conn.commit()

    # ------------------------------------------------------
    # Presets
    # ------------------------------------------------------
    def create_preset(self, name: str, description: str, prompt_template: str) -> int:
        """Create a new preset."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO presets (name, description, prompt_template) VALUES (?, ?, ?)", (name, description, prompt_template))
            conn.commit()
            return cur.lastrowid

    def get_preset(self, name: str) -> Optional[Dict[str, Any]]:
        """Read a preset by its unique name."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM presets WHERE name = ?", (name,)).fetchone()
            return dict(row) if row else None
            
    def update_preset(self, name: str, **kwargs):
        """Update a preset's data (e.g., description, prompt_template)."""
        self._update_record("presets", "name", name, **kwargs)

    def delete_preset(self, name: str):
        """Delete a preset by its name."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM presets WHERE name = ?", (name,))
            conn.commit()

    def list_presets(self) -> List[Dict[str, Any]]:
        """List all available presets."""
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM presets").fetchall()
            return [dict(row) for row in rows]
        
    def get_caption(self, message_id: str) -> Optional[str]:
        """Read a caption for a given message ID."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT caption FROM captions WHERE message_id = ?", (message_id,)).fetchone()
            return row['caption'] if row else None

    def set_caption(self, message_id: str, caption: str):
        """Create or update a caption for a message ID."""
        with self._get_connection() as conn:
            conn.execute("REPLACE INTO captions (message_id, caption) VALUES (?, ?)", (message_id, caption))
            conn.commit()

    def delete_caption(self, message_id: str):
        """Delete a caption for a message ID."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM captions WHERE message_id = ?", (message_id,))
            conn.commit()