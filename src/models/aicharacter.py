from __future__ import annotations
from typing import Optional, List, Dict, Any

# Assuming your database class is in a file that can be imported
# from api.db.database import Database
# For standalone testing, we'll include a placeholder.
from api.db.database import Database  # Adjust this import path to match your project structure


class ActiveCharacter:
    """
    Represents the character that has been triggered by a message.
    It is initialized by searching a message for trigger words and loading
    the corresponding character data from the database.
    """

    def __init__(self, character_data: Dict[str, Any], db: Database):
        """
        Initializes an ActiveCharacter instance from a dictionary of character data.
        This constructor should typically be called by the `from_message` classmethod.
        """
        self.db = db
        
        # Unpack data from the database record
        self.id: int = character_data['id']
        self.name: str = character_data['name']
        self.triggers: List[str] = character_data.get('triggers', [])
        
        # Unpack the nested 'data' dictionary
        data = character_data.get('data', {})
        self.persona: str = data.get('persona', '')
        self.examples: List[str] = data.get('examples', [])
        self.instructions: str = data.get('instructions', '')
        self.avatar: Optional[str] = data.get('avatar', None)
        self.info: Optional[str] = data.get('info', None)

    @classmethod
    def from_message(cls, text: str, db: Database) -> Optional[ActiveCharacter]:
        """
        Returns the character whose name or trigger appears earliest in the text.
        """
        all_characters = db.list_characters()
        text_lower = text.lower()

        earliest_match = None  # (index, character_data)

        for char_data in all_characters:
            name = char_data.get("name", "").lower()
            triggers = [t.lower() for t in char_data.get("triggers", [])]

            # Add the name into the trigger pool
            extended_triggers = triggers + [name]

            for trigger in extended_triggers:
                if not trigger:
                    continue

                idx = text_lower.find(trigger)
                if idx != -1:
                    # If it's the first match OR earlier than our current best, keep it
                    if earliest_match is None or idx < earliest_match[0]:
                        earliest_match = (idx, char_data)

        if earliest_match:
            return cls(character_data=earliest_match[1], db=db)

        return None



    def save(self):
        """Saves the current state of the character's data back to the database."""
        data_to_save = {
            "persona": self.persona,
            "examples": self.examples,
            "instructions": self.instructions,
            "avatar": self.avatar,
            "info": self.info
        }
        self.db.update_character(name=self.name, data=data_to_save)
        print(f"Successfully saved character '{self.name}' to the database.")

    def get_character_prompt(self, user_name: str = "User") -> str:
        """
        Generates the final character prompt for the LLM, replacing placeholders.
        """
        # Replace placeholders in the persona and examples
        persona_processed = self.persona.replace('{{char}}', self.name).replace('{{user}}', user_name)
        
        examples_processed = []
        for example in self.examples:
            processed_line = example.replace('{{char}}', self.name).replace('{{user}}', user_name)
            if not processed_line.startswith("[System"):
                processed_line = f"[Reply] {processed_line} [End]"
            examples_processed.append(processed_line)

        # Build the prompt string
        character_desc = f"You are {self.name}, you embody their character, persona, goals, personality, and bias which is described in detail below:"
        persona_prompt = f"Your persona: {persona_processed}"
        examples_prompt = "A history reference to your speaking quirks and behavior:\n" + '\n'.join(examples_processed)

        return f"{character_desc}\n{persona_prompt}\n{examples_prompt}\n{self.instructions}"

    # --- Setters ---
    # Each setter now modifies the instance attribute and persists the change to the database.

    def set_persona(self, persona: str):
        """Setter for character persona."""
        self.persona = persona
        self.save()

    def set_examples(self, examples: list):
        """Setter for character examples."""
        self.examples = examples
        self.save()

    def set_instructions(self, instructions: str):
        """Setter for character instructions."""
        self.instructions = instructions
        self.save()

    def set_avatar(self, avatar: str):
        """Setter for character avatar."""
        self.avatar = avatar
        self.save()

    def set_info(self, info: str):
        """Setter for character info."""
        self.info = info
        self.save()