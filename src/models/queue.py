from dataclasses import *
import discord


@dataclass
class QueueItem:
    prompt: str
    result:str = None
    error:str = None
    images:list = None
    dm:bool = False
