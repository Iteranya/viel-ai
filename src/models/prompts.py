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
        if "<battle_rp>" in self.dimension.instruction:
            instructionvar += roll_d20()

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
import random

def roll_d20():
    roll = random.randint(1, 20)
    
    outcomes = {
        1: "You rolled a 1 — you fail spectacularly on whatever you try to do next.",
        2: "You rolled a 2 — your next action will fumble clumsily.",
        3: "You rolled a 3 — not good... prepare for a weak outcome.",
        4: "You rolled a 4 — you try, but it’s not impressive.",
        5: "You rolled a 5 — you miss the mark.",
        6: "You rolled a 6 — barely functional, but don’t count on it.",
        7: "You rolled a 7 — it’ll go through, but probably not how you intended.",
        8: "You rolled an 8 — you’ll get close, but no critical success.",
        9: "You rolled a 9 — mediocre result incoming.",
        10: "You rolled a 10 — a balanced, neutral outcome awaits.",
        11: "You rolled an 11 — your next move is just slightly better than average.",
        12: "You rolled a 12 — not bad, could go your way.",
        13: "You rolled a 13 — a stroke of decent fortune may assist you.",
        14: "You rolled a 14 — likely success with minor effort.",
        15: "You rolled a 15 — things are leaning in your favor.",
        16: "You rolled a 16 — you’re in the zone, expect a good outcome.",
        17: "You rolled a 17 — you act with confidence and precision.",
        18: "You rolled an 18 — near mastery, your next step will shine.",
        19: "You rolled a 19 — whatever you do next will probably work really well.",
        20: "You rolled a 20 — a critical success! Your next action is legendary.",
    }
    print(outcomes[roll])

    return f"[System Note: Refer to the following dice roll for the character's next action: {outcomes[roll]}]"

