from __future__ import annotations
from typing import Optional, List, Dict, Any

# Assuming your database class is in a file that can be imported
# from api.db.database import Database
# For standalone testing, we'll include a placeholder.
from api.db.database import Database  # Adjust this import path to match your project structure


class ActiveChannel:
    """
    Represents the configuration for a specific, active channel.
    It is initialized using a channel_id and loads/saves its data
    directly from/to the database.
    """

    def __init__(self, channel_record: Dict[str, Any], db: Database):
        """
        Initializes an ActiveChannel instance from a channel data record.
        This constructor is best called via the `from_id` classmethod.
        """
        self.db = db
        
        # Unpack top-level data from the database record
        self.channel_id: str = channel_record['channel_id']
        self.server_id: str = channel_record['server_id']
        self.server_name: str = channel_record['server_name']
        
        # Unpack the nested 'data' dictionary which holds the configuration
        data = channel_record.get('data', {})
        self.name: str = data.get('name', '')
        self.description: Optional[str] = data.get('description')
        self.global_note: Optional[str] = data.get('global') # Maps to 'global' key
        self.instruction: Optional[str] = data.get('instruction')
        self.whitelist: List[str] = data.get('whitelist', [])

        self.is_system_channel: bool = data.get('is_system_channel', False)

    @classmethod
    def from_id(cls, channel_id: str, db: Database) -> Optional[ActiveChannel]:
        """
        Fetches a channel's configuration from the database by its ID and
        returns an ActiveChannel instance.

        Args:
            channel_id (str): The unique ID of the channel to load.
            db (Database): An instance of the database manager.

        Returns:
            Optional[ActiveChannel]: An instance of the channel, or None if not found.
        """
        channel_record = db.get_channel(channel_id)
        if channel_record:
            return cls(channel_record, db)
        return None

    def save(self):
        """Saves the current state of the channel's configuration back to the database."""
        # Assemble the dictionary that matches the 'data' column's structure
        data_to_save = {
            "name": self.name,
            "description": self.description,
            "global": self.global_note, # Note the mapping back to 'global'
            "instruction": self.instruction,
            "whitelist": self.whitelist,
            "is_system_channel": self.is_system_channel
        }
        self.db.update_channel(self.channel_id, data=data_to_save)
        print(f"Successfully saved channel '{self.channel_id}' to the database.")

    def get_data_dict(self) -> Dict[str, Any]:
        """Returns the dictionary representation of the channel's configurable data."""
        return {
            "name": self.name,
            "description": self.description,
            "global": self.global_note,
            "instruction": self.instruction,
            "whitelist": self.whitelist
        }

    # --- Setters ---
    # Each setter modifies the instance attribute and persists the change to the database.

    def set_name(self, name: str):
        self.name = name
        self.save()

    def set_description(self, description: Optional[str]):
        self.description = description
        self.save()
        
    def set_global_note(self, note: Optional[str]):
        self.global_note = note
        self.save()

    def set_instruction(self, instruction: Optional[str]):
        self.instruction = instruction
        self.save()

    def set_whitelist(self, whitelist: List[str]):
        self.whitelist = whitelist
        self.save()

    def set_is_system_channel(self, is_system: bool):
        """Sets the system channel flag and saves it to the database."""
        self.is_system_channel = is_system
        self.save()