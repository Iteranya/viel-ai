import json
import os
from typing import Optional

class CaptionManager:
    """Manages loading, saving, and caching of image captions."""

    def __init__(self, captions_file: str = "res/captions.jsonl"):
        self.captions_file = captions_file
        self.captions_cache = self._load_captions()
        print(f"CaptionManager initialized. Loaded {len(self.captions_cache)} captions from cache.")

    def _load_captions(self) -> dict[int, str]:
        """Loads message_id:caption pairs from the jsonl file into memory."""
        cache = {}
        if not os.path.exists(self.captions_file):
            return cache
        try:
            with open(self.captions_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        cache[data["message_id"]] = data["caption"]
                    except (json.JSONDecodeError, KeyError):
                        print(f"Warning: Skipping corrupted line in {self.captions_file}")
                        continue
        except IOError as e:
            print(f"Warning: Could not load captions file: {e}")
        return cache

    def get_caption(self, message_id: int) -> Optional[str]:
        """Retrieves a caption from the in-memory cache."""
        return self.captions_cache.get(message_id)

    def save_caption(self, message_id: int, caption: str):
        """Saves a new caption to the cache and appends it to the jsonl file."""
        if message_id in self.captions_cache:
            return # Already exists

        self.captions_cache[message_id] = caption
        entry = {"message_id": message_id, "caption": caption}
        try:
            # Ensure directory exists before writing
            os.makedirs(os.path.dirname(self.captions_file), exist_ok=True)
            with open(self.captions_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except IOError as e:
            print(f"Error: Could not save caption to file: {e}")