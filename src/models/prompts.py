from src.models.aicharacter import AICharacter
from src.models.dimension import Dimension
from src.controller.discordo import get_history
import discord


class PromptEngineer:
    def __init__(self, bot:AICharacter, message: discord.Message, dimension:Dimension):
        self.bot = bot
        self.user = str(message.author.display_name)
        self.message = message
        self.dimension = dimension
        self.stopping_string = None
        self.prefill = None
        print(self.user)

    async def create_text_prompt(self) -> str:
        jb = self.bot.instructions
        character = await self.bot.get_character_prompt()
        #jb = "" # Toggle this to disable JB
        globalvar = self.dimension.getDict().get("globalvar", "")
        locationvar = self.dimension.getDict().get("location", "")
        instructionvar = self.dimension.getDict().get("instruction", "")

        # Safety Filter for Discord ToS Sake, please don't disable. Just use NSFW Channel like a normal person.
        if not self.message.channel.is_nsfw():
            instructionvar+="\n\n[System Note: IMPORTANT, Strict Safety Filter Deployed. Bot MUST Refuse To Answer If Content Is Harmful, Sexual, or Controversial in Nature. Try To Stay In Character, But Prioritize Safety Above All Else.]"

        history = await get_history(self.message)
        prompt = (
            f"<character_definition>{character}</character_definition>\n"
            f"<lore>{globalvar}</lore>\n"
            f"<conversation_history>{history}</conversation_history>\n"
            f"<note>{locationvar}</note>\n"
            f"<additional_note>{jb}\n{instructionvar}</additional_note>\n"
        )
        # JUST USE AN F STRING YOU GODDAMN NEANDERTHAL!!!!!
        # SHUT THE FUCK UP I'M PROTOTYPING!!!
        # THERE I USED FSTRING, HAPPY NOW?!!?!?
        self.prefill = f"\n[Reply] {self.bot.name}:"
        self.stopping_string = ["[System", "(System", self.user + ":", "[End","[/"] 
        #print(prompt)
        return prompt

