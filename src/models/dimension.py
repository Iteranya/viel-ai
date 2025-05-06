import json
import os
from src.data.dimension_data import createOrFetchChannelConfig
# Right, I haven't done this one...
# Fffffff-
# No, I don't feel like stopping, or giving up...
# I want... to make this count, really count...

class Dimension:
    def __init__(self, server_name:str, channel_name:str):
        self.dim_dict:dict  = createOrFetchChannelConfig(server_name,channel_name)
        self.name:str = self.dim_dict.get("name","")
        self.instruction:str = self.dim_dict.get("instruction","")
        self.globalvar:str = self.dim_dict.get("global","")
        self.location:str = self.dim_dict.get("location","")
        self.lorebook:dict = self.dim_dict.get("lorebook",None)
        
        return
    

    def getDict(self):
        return self.dim_dict
    
    