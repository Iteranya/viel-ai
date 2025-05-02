from dataclasses import *
import discord


@dataclass
class QueueItem:
    prompt: str
    bot:str = None
    user:str = None
    result:str = None
    error:str = None
    images:list = None
    dm:bool = False
    stop:list = None
    prefill:str = None
    
