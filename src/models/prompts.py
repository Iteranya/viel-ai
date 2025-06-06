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
            instructionvar += roll_d20(self.bot.bot_name)

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

def roll_d20(bot):
    roll = random.randint(1, 20)
    
    outcomes = {
        1: f"{bot} rolled a 1 — {bot} fail spectacularly on whatever {bot} try to do next.",
        2: f"{bot} rolled a 2 — {bot} next action will fumble clumsily.",
        3: f"{bot} rolled a 3 — not good... prepare for a weak outcome or terrible out come for {bot}.",
        4: f"{bot} rolled a 4 — {bot} try, but it’s not impressive still failed or getting hit hard.",
        5: f"{bot} rolled a 5 — {bot} miss the mark or getting hit hard.",
        6: f"{bot} rolled a 6 — {bot} barely managed to do it, but don’t count on it.",
        7: f"{bot} rolled a 7 — it’ll go through, but probably not how {bot} intended.",
        8: f"{bot} rolled an 8 — you’ll get close, but no critical success for {bot}.",
        9: f"{bot} rolled a 9 — mediocre result incoming.",
        10: f"{bot} rolled a 10 — a balanced, neutral outcome awaits.",
        11: f"{bot} rolled an 11 — {bot}'s next move is just slightly better than average.",
        12: f"{bot} rolled a 12 — not bad, could go {bot}'s way.",
        13: f"{bot} rolled a 13 — a stroke of decent fortune may assist {bot}.",
        14: f"{bot} rolled a 14 — likely success with minor effort.",
        15: f"{bot} rolled a 15 — things are leaning in {bot}'s favor.",
        16: f"{bot} rolled a 16 — {bot}'s in the zone, expect a good outcome.",
        17: f"{bot} rolled a 17 — {bot} act with confidence and precision, whatever she does, it's amazing.",
        18: f"{bot} rolled an 18 — {bot}'s near mastery, their next step will shine bright.",
        19: f"{bot} rolled a 19 — whatever {bot} do next will work really well.",
        20: f"{bot} rolled a 20 — a critical success! {bot}'s next action is legendary.",
    }
    print(outcomes[roll])

    return f"[System Note: Refer to the following dice roll for the character's next action: {outcomes[roll]}]"

