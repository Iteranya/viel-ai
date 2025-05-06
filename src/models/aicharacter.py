import os
import json

class AICharacter:
    def __init__(self, bot_name:str):
        self.bot_name = bot_name
        self.char_dict:dict = self.replace_placeholders(self.get_card(bot_name),bot_name,"User")
        self.name:str = self.get_name()
        self.persona:str = self.get_persona()
        self.examples:list = self.get_examples()
        self.instructions:str = self.get_instructions()
        self.avatar:str = self.get_avatar()
        self.info:str = self.get_info()

    def getDictFromJson(self,json_path):
        with open(json_path, 'r') as f:
            try:
                # Load JSON data
                data = json.load(f)
                return data

            except json.JSONDecodeError as e:
                print(f"Error parsing {json_path}: {e}")
        return None
    
    def saveDictToJson(self):
        data = self.char_dict
        json_path = f"../characters/{self.bot_name}.json"
        try:
            with open(json_path, 'w') as f:
                # Save the dictionary as JSON
                json.dump(data, f, indent=4)
                print(f"Successfully saved data to {json_path}")
        except TypeError as e:
            print(f"Error saving data to {json_path}: {e}")
        except IOError as e:
            print(f"I/O error occurred while writing to {json_path}: {e}")

    def get_card(self,bot_name: str)->dict:
        directory = "res/characters"
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                filepath = os.path.join(directory, filename)
                try:
                    # Open and load JSON file
                    with open(filepath, 'r', encoding='utf-8') as file:
                        data = json.load(file)

                    # Check if 'name' field matches target_name
                    if "data" in data and str(data["data"]["name"]).lower() == str(bot_name).lower():
                        return data["data"]
                    elif "name" in data and str(data["name"]).lower() == str(bot_name).lower():
                        return data
                    
                except json.JSONDecodeError:
                    print(f"Error decoding JSON in file: {filepath}")
                except Exception as e:
                    print(f"Error processing file {filepath}: {e}")

    def replace_placeholders(self,data: dict, bot_name: str, user_name: str) -> dict:

        # Convert dict to JSON string
        json_str = json.dumps(data)
        
        # Replace placeholders in the string
        replaced_str = json_str.replace('{{char}}', bot_name).replace('{{user}}', user_name)
        
        # Parse back to dictionary
        return json.loads(replaced_str)

    async def get_character_prompt(self) -> str | None:
        # Your name is <name>.
        character: str = "You are " + self.name + ", you embody their character, persona, goals, personality, and bias which is described in detail below:"

        # Your name is <name>. You are a <persona>.
        character = character + "Your persona: " + self.persona + ". "

        # Instructions on what the bot should do. This is where an instruction model will get its stuff.

        examples = self.examples  # put example responses here

        for example in examples:
            if example.startswith("[System"):
                pass
            else:
                example = f"[Reply] {example}"

        # Example messages!
        character_prompt = character + " A history reference to your speaking quirks and behavior: " + \
        "\n" + '\n'.join(examples) + "\n"

        return character_prompt

    def get_name(self) -> str:
        """Getter for character name."""
        name = self.char_dict.get("name","")
        if name == "":
            data:dict = self.char_dict.get("data",None)
            if data!=None:
                name = data.get("name","")
        return name

    def get_persona(self) -> str:
        """Getter for character persona."""
        persona = self.char_dict.get("persona",None)
        if persona ==None:
            data:dict = self.char_dict.get("data",None)
            if data != None:
                persona = data.get("description","")
            else:
                persona = self.char_dict.get("description","")
        return persona

    def get_examples(self) -> list:
        """Getter for character examples."""
        examples = self.char_dict.get("examples","")
        return examples

    def get_instructions(self) -> str:
        """Getter for character instructions."""
        instruction = self.char_dict.get("instructions","")
        return instruction

    def get_avatar(self) -> str:
        """Getter for character avatar."""
        avatar = self.char_dict.get("image","")
        if avatar == "":
                data:dict = self.char_dict.get("data",None)
                if data != None:
                    avatar = data.get("avatar","")
                else:
                    avatar = self.char_dict.get("avatar","")
        return avatar

    def get_info(self) -> str:
        """Getter for character info."""
        info = self.char_dict.get("info","")
        return info

    # Setters
    def set_name(self, name: str):
        """Setter for character name."""
        self.name = name
        self.char_dict["name"] = name

    def set_persona(self, persona: str):
        """Setter for character persona."""
        self.persona = persona
        self.char_dict["persona"] = persona

    def set_examples(self, examples: list):
        """Setter for character examples."""
        self.examples = examples
        self.char_dict["examples"] = examples

    def set_instructions(self, instructions: str):
        """Setter for character instructions."""
        self.instructions = instructions
        self.char_dict["instructions"] = instructions

    def set_avatar(self, avatar: str):
        """Setter for character avatar."""
        self.avatar = avatar
        self.char_dict["image"] = avatar

    def set_info(self, info: str):
        """Setter for character info."""
        self.info = info
        self.char_dict["info"] = info
    

    


   
    


