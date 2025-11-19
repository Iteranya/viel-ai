from __future__ import annotations
from typing import Optional, List, Dict, Any
import discord
from api.db.database import Database

# A constant ID for your virtual DM server
DM_SERVER_ID = "DM_VIRTUAL_SERVER"

class ActiveChannel:
    """
    Represents the configuration for a specific, active channel.
    """

    def __init__(self, channel_record: Dict[str, Any], db: Database):
        self.db = db
        
        self.channel_id: str = channel_record['channel_id']
        self.server_id: str = channel_record['server_id']
        self.server_name: str = channel_record['server_name']
        
        data = channel_record.get('data', {})
        self.name: str = data.get('name', '')
        self.description: Optional[str] = data.get('description')
        self.global_note: Optional[str] = data.get('global') 
        self.instruction: Optional[str] = data.get('instruction')
        self.whitelist: List[str] = data.get('whitelist', [])
        self.is_system_channel: bool = data.get('is_system_channel', False)

    @classmethod
    def from_id(cls, channel_id: str, db: Database) -> Optional[ActiveChannel]:
        channel_record = db.get_channel(channel_id)
        if channel_record:
            return cls(channel_record, db)
        return None

    @classmethod
    def from_dm(cls, dm_channel: discord.DMChannel, db: Database) -> ActiveChannel:
        """
        Gets a DM channel from the DB. 
        If the 'DM Server' or this specific DM channel doesn't exist in the DB,
        it creates them automatically.
        """
        
        # 1. Ensure the Virtual DM Server exists
        server = db.get_server(DM_SERVER_ID)
        if not server:
            print("Initializing Virtual DM Server in Database...")
            db.create_server(
                server_id=DM_SERVER_ID, 
                server_name="Direct Messages", 
                description="A virtual container for all Bot DMs", 
                instruction="These are private conversations."
            )

        # 2. Try to find this specific DM channel
        channel_id = str(dm_channel.id)
        channel_record = db.get_channel(channel_id)

        # 3. If it doesn't exist, create it
        if not channel_record:
            print(f"New DM detected. Registering channel {channel_id} to database.")
            
            # Default data for a new DM
            user_name = dm_channel.recipient.name if dm_channel.recipient else "Unknown"
            new_data = {
                "name": f"DM with {user_name}",
                "description": f"Private Direct Message history with {user_name}",
                "global": None,
                "instruction": None, # You can set a default instruction here if you want
                "whitelist": [],
                "is_system_channel": False
            }
            
            db.create_channel(
                channel_id=channel_id, 
                server_id=DM_SERVER_ID, 
                server_name="Direct Messages", 
                data=new_data
            )
            
            # Fetch the record we just created
            channel_record = db.get_channel(channel_id)

        return cls(channel_record, db)

    def save(self):
        """Saves the current state to the database."""
        data_to_save = {
            "name": self.name,
            "description": self.description,
            "global": self.global_note, 
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