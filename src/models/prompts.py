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
            instructionvar += roll_defend(self.bot.bot_name)
            instructionvar += roll_attack(self.bot.bot_name)

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
        1: f"{bot} rolled a 1/20 — {bot} fail spectacularly on whatever {bot} try to do next. If {bot}'s defending, they're fucked",
        2: f"{bot} rolled a 2/20 — {bot} next action will fumble clumsily. If {bot}'s defending, they're fucked",
        3: f"{bot} rolled a 3/20 — Terrible prepare for a weak outcome for {bot}. If {bot}'s defending, they're fucked",
        4: f"{bot} rolled a 4/20 — {bot} try, but it’s not impressive still failed or If {bot}'s defending, {bot} got hit where it Hurts.",
        5: f"{bot} rolled a 5/20 — {bot} miss the mark or getting hit hard.",
        6: f"{bot} rolled a 6/20 — {bot} barely managed to do it, but don’t count on it.",
        7: f"{bot} rolled a 7/20 — things happen but probably not how {bot} intended.",
        8: f"{bot} rolled an 8/20 — you’ll get close, but nothing good for {bot}.",
        9: f"{bot} rolled a 9/20 — mediocre result incoming if {bot}'s attacking, or if defending {bot}'s still getting hit.",
        10: f"{bot} rolled a 10/20 — a balanced, neutral outcome awaits.",
        11: f"{bot} rolled an 11/20 — {bot}'s next move is just slightly better than average.",
        12: f"{bot} rolled a 12/20 — not bad, could go {bot}'s way.",
        13: f"{bot} rolled a 13/20 — a stroke of decent fortune may assist {bot}.",
        14: f"{bot} rolled a 14/20 — likely success with minor effort.",
        15: f"{bot} rolled a 15/20 — things are leaning in {bot}'s favor.",
        16: f"{bot} rolled a 16/20 — {bot}'s in the zone, expect a good outcome.",
        17: f"{bot} rolled a 17/20 — {bot} act with confidence and precision, whatever they do, it's amazing.",
        18: f"{bot} rolled an 18/20 — {bot}'s near mastery, their next step will shine bright.",
        19: f"{bot} rolled a 19/20 — whatever {bot} do next will work really well.",
        20: f"{bot} rolled a 20/20 — a critical success! {bot}'s next action is legendary.",
    }
    print(outcomes[roll])

    return f"[System Note: Refer to the following dice roll for the character's next action: {outcomes[roll]}]"

def roll_defend(bot):
    roll = random.randint(1, 20)
    
    outcomes = {
        1: f"{bot} rolled a 1/20 — {bot} failed miserably to defend themselves, they're gonna get wrecked",
        2: f"{bot} rolled a 2/20 — {bot} failed miserably to defend themselves, they're gonna get wrecked",
        3: f"{bot} rolled a 3/20 — {bot} failed miserably to defend themselves, they're gonna get hit where it hurts",
        4: f"{bot} rolled a 4/20 — {bot} failed to defend themselves, they're gonna get hit where it hurts.",
        5: f"{bot} rolled a 5/20 — {bot} tried to defend themselves, they're gonna get hit where it hurts.",
        6: f"{bot} rolled a 6/20 — {bot} tried to defend themselves, they tanked it but it hurts",
        7: f"{bot} rolled a 7/20 — {bot} tried to defend themselves, they tanked the damage",
        8: f"{bot} rolled an 8/20 — {bot} defend themselves, they tanked the damage.",
        9: f"{bot} rolled a 9/20 — {bot} defend themselves, they took the hit",
        10: f"{bot} rolled a 10/20 — {bot} defend themselves and took the hit like a champ",
        11: f"{bot} rolled an 11/20 — {bot} defend themselves and just barely dodged the attack, it still hit them hard",
        12: f"{bot} rolled a 12/20 — {bot} defend themselves and just barely dodged the attack, it still hit them head on",
        13: f"{bot} rolled a 13/20 — {bot} defend themselves and dodged the attack, it still hit them head on",
        14: f"{bot} rolled a 14/20 — {bot} defend themselves and dodged the attack, it still hit them",
        15: f"{bot} rolled a 15/20 — {bot} defend themselves and dodged the attack, it barely hit them",
        16: f"{bot} rolled a 16/20 — {bot} defend themselves and dodged the attack, it grazed them",
        17: f"{bot} rolled a 17/20 — {bot} defend themselves and dodged the attack, it barely grazed them",
        18: f"{bot} rolled an 18/20 — {bot} defend themselves and dodged the attack, it didn't leave a scratch",
        19: f"{bot} rolled a 19/20 — {bot} defend themselves and dodged the attack, it has little effect on {bot}",
        20: f"{bot} rolled a 20/20 — {bot} defend themselves and dodged the attack, it has little effect on {bot}",
    }
    print(outcomes[roll])

    return f"[System Note: Refer to the following dice roll for the character's defensive action: {outcomes[roll]}]"

import random

def roll_attack(bot):
    roll = random.randint(1, 20)
    
    outcomes = {
        1: f"{bot} rolled a 1/20 — {bot} fumbled their attack horribly! They might've hurt themselves...",
        2: f"{bot} rolled a 2/20 — {bot} missed completely and looks foolish doing it.",
        3: f"{bot} rolled a 3/20 — {bot} swung wide and lost their balance.",
        4: f"{bot} rolled a 4/20 — {bot}'s attack missed by a mile.",
        5: f"{bot} rolled a 5/20 — {bot}'s attack barely missed the target.",
        6: f"{bot} rolled a 6/20 — {bot}'s attack connected, but did almost no damage.",
        7: f"{bot} rolled a 7/20 — {bot} landed a weak hit.",
        8: f"{bot} rolled an 8/20 — {bot} hit their target, but it wasn’t impressive.",
        9: f"{bot} rolled a 9/20 — {bot} hit the target, but it's not very effective.",
        10: f"{bot} rolled a 10/20 — {bot} landed a standard hit.",
        11: f"{bot} rolled an 11/20 — {bot} struck solidly, causing noticeable damage.",
        12: f"{bot} rolled a 12/20 — {bot} landed a strong hit!",
        13: f"{bot} rolled a 13/20 — {bot}'s attack hit with decent force.",
        14: f"{bot} rolled a 14/20 — {bot} delivered a well-placed hit.",
        15: f"{bot} rolled a 15/20 — {bot}'s attack was clean and effective.",
        16: f"{bot} rolled a 16/20 — {bot} delivered a powerful strike!",
        17: f"{bot} rolled a 17/20 — {bot}'s attack was very strong and well-executed.",
        18: f"{bot} rolled an 18/20 — {bot} struck with impressive power!",
        19: f"{bot} rolled a 19/20 — {bot} delivered a devastating blow!",
        20: f"{bot} rolled a 20/20 — Critical hit! {bot}'s attack is perfectly executed and devastating!",
    }
    print(outcomes[roll])
    
    return f"[System Note: Refer to the following dice roll for the character's attack action: {outcomes[roll]}]"
