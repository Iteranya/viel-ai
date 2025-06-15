import random

# --- Data Definitions (Moved outside the function for better practice) ---

# A complete deck of Tarot cards
MAJOR_ARCANA = [
    "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
    "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
    "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
    "The Devil", "The Tower", "The Star", "The Moon", "The Sun",
    "Judgement", "The World"
]

MINOR_SUITS = ["Wands", "Cups", "Swords", "Pentacles"]
MINOR_RANKS = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Page", "Knight", "Queen", "King"]
MINOR_ARCANA = [f"{rank} of {suit}" for suit in MINOR_SUITS for rank in MINOR_RANKS]

SPREADS = {
    "general": {
        "positions": ["Past", "Present", "Future"],
        "description": "This is a 3-card general reading: past influences, current situation, and possible outcome.",
        "reversed": True,
        "cards_used": "all"
    },
    "celtic": {
        "positions": [
            "Present Situation", "Challenge", "Past Influences", "Future Possibilities",
            "Conscious Goal", "Subconscious Influence", "Advice", "External Influences",
            "Hopes and Fears", "Outcome"
        ],
        "description": "This is the Celtic Cross spread, a 10-card layout providing deep insight into a complex situation.",
        "reversed": True,
        "cards_used": "all"
    },
    "relationship": {
        "positions": ["You", "The Other Person", "The Relationship"],
        "description": "A 3-card spread exploring dynamics in a relationship.",
        "reversed": True,
        "cards_used": "all"
    },
    "career": {
        "positions": ["Current Job", "Challenges", "Advice"],
        "description": "A 3-card career-focused spread identifying work-related insights.",
        "reversed": True,
        "cards_used": "all"
    },
    "decision": {
        "positions": ["Option 1", "Option 2", "Advice on Choice"],
        "description": "A 3-card spread to help weigh two options and guide your decision.",
        "reversed": True,
        "cards_used": "all"
    },
    "week": {
        "positions": [
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Overall Theme"
        ],
        "description": "An 8-card spread to get a feel for the week ahead and its overarching energy.",
        "reversed": True,
        "cards_used": "minor"
    },
    "self reflection": {
        "positions": ["Mind", "Body", "Spirit"],
        "description": "A 3-card spread for a quick check-in with your mental, physical, and spiritual well-being.",
        "reversed": True,
        "cards_used": "all"
    },
    "new moon": {
        "positions": ["What to Release", "What to Cultivate", "Guidance for the Cycle"],
        "description": "A 3-card spread to set intentions and align with the energy of the new moon.",
        "reversed": False,
        "cards_used": "all"
    },
    "full moon": {
        "positions": ["What has Culminated", "What to be Grateful For", "What to Let Go Of"],
        "description": "A 3-card spread for reflection and release during the full moon.",
        "reversed": True,
        "cards_used": "all"
    },
    "pathway": {
        "positions": [
            "Where You Are Now", "Your Destination", "The Steps to Take",
            "Obstacles to Overcome", "Helpful Resources"
        ],
        "description": "A 5-card spread that outlines the path from your current position to a desired goal.",
        "reversed": True,
        "cards_used": "all"
    },
    "horseshoe": {
        "positions": [
            "Past Influences", "Present Situation", "Near Future Development",
            "The Querent's Attitude", "External Environment", "Hopes and Fears", "Final Outcome"
        ],
        "description": "A 7-card spread offering a more detailed look at a situation than a simple 3-card reading.",
        "reversed": True,
        "cards_used": "all"
    },
    "mandala": {
        "positions": [
            "The Self (Inner State)", "Your Relationship with the Physical World",
            "Your Emotional State", "Your Intellectual State", "Your Spiritual State",
            "A Challenge to Integrate", "A Strength to Embrace",
            "Your Connection to the Divine/Universe", "Guidance for a Wholistic Life"
        ],
        "description": "A 9-card spread that explores various aspects of the self for a holistic overview.",
        "reversed": True,
        "cards_used": "all"
    },
    "dream": {
        "positions": [
            "Core Meaning of the Dream", "Subconscious Message",
            "How it Relates to Waking Life", "Action to Take"
        ],
        "description": "A 4-card spread to uncover the messages and meanings hidden within a dream.",
        "reversed": True,
        "cards_used": "all"
    },
    "year": {
        "positions": [
            "January", "February", "March", "April", "May", "June", "July",
            "August", "September", "October", "November", "December",
            "Overall Theme for the Year"
        ],
        "description": "A 13-card spread, one for each month and an overall theme, to forecast the year ahead.",
        "reversed": False,
        "cards_used": "major"
    },
    "chakra": {
        "positions": [
            "Root Chakra (Security, Survival)", "Sacral Chakra (Creativity, Emotion)",
            "Solar Plexus Chakra (Personal Power, Will)", "Heart Chakra (Love, Relationships)",
            "Throat Chakra (Communication, Truth)", "Third Eye Chakra (Intuition, Insight)",
            "Crown Chakra (Spirituality, Connection)"
        ],
        "description": "A 7-card spread to assess the energy and balance of your major chakras.",
        "reversed": False,
        "cards_used": "major"
    }
}


def shuffle_tarot(num_cards=3, reversed_allowed=True, card_type="all"):
    """
    Selects a specified number of tarot cards from a deck.
    """
    if card_type == "major":
        deck = MAJOR_ARCANA
    elif card_type == "minor":
        deck = MINOR_ARCANA
    else:
        deck = MAJOR_ARCANA + MINOR_ARCANA

    # Ensure we don't try to draw more cards than are in the deck
    if num_cards > len(deck):
        raise ValueError("Number of cards requested exceeds the size of the selected deck.")

    selected = random.sample(deck, num_cards)
    output = []

    for card in selected:
        # Determine if the card is reversed
        is_reversed = reversed_allowed and random.choice([True, False])
        reversed_status = "Reversed" if is_reversed else "Upright"
        output.append((card, reversed_status))

    return output


def generate_tarot_reading(request: str):
    """
    Generates a tarot reading based on a requested spread.

    Searches for the spread name in the request string. If no specific
    spread is found, it defaults to the "general" 3-card spread.
    """
    sanitized_request = request.lower().replace("_", " ")
    chosen_spread_key = "general"  # Default spread

    # Find the requested spread, if any
    for spread_name in SPREADS:
        if spread_name in sanitized_request:
            chosen_spread_key = spread_name
            break  # Use the first match found

    spread_details = SPREADS[chosen_spread_key]
    positions = spread_details["positions"]
    num_cards = len(positions)
    allow_reversed = spread_details["reversed"]
    card_type_to_use = spread_details["cards_used"]

    # Get the shuffled cards
    cards = shuffle_tarot(num_cards, allow_reversed, card_type_to_use)

    # Format the output
    output_lines = [spread_details["description"], ""]
    for position, (card, status) in zip(positions, cards):
        output_lines.append(f"{position}: {card} ({status})")

    return "\n".join(output_lines)

# --- Example Usage ---
if __name__ == "__main__":
    print("--- Celtic Cross Reading ---")
    # The string "celtic_cross" contains "celtic", so it will find the correct spread.
    reading1 = generate_tarot_reading("celtic_cross")
    print(reading1)

    print("\n" + "="*30 + "\n")

    print("--- Default/General Reading ---")
    # This request doesn't contain any spread names, so it will fall back to "general".
    reading2 = generate_tarot_reading("Give me a reading for my day.")
    print(reading2)

    print("\n" + "="*30 + "\n")

    print("--- Career Reading ---")
    reading3 = generate_tarot_reading("I need some career advice")
    print(reading3)