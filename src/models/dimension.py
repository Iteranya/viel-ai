import json
import os
class Dimension:
    def __init__(self, context_name:str):
        self.dim_dict:dict  = self.createOrFetchJson(context_name)
        self.name:str = self.dim_dict.get("name","")
        self.instruction:str = self.dim_dict.get("instruction","")
        self.globalvar:str = self.dim_dict.get("global","")
        self.location:str = self.dim_dict.get("location","")
        self.lorebook:dict = self.dim_dict.get("lorebook",None)

        return
    

    def getDict(self):
        return self.dim_dict
    
    
    def createOrFetchJson(self,input_string):
        # File name with .json extension
        file_name = f"channels/{input_string}.json"

        # Check if the file already exists
        if os.path.exists(file_name):
            # Open and fetch the content
            with open(file_name, "r") as json_file:
                data = json.load(json_file)
            print(f"File '{file_name}' already exists. Fetched content: {data}")
            return data
        
        # If it doesn't exist, create the data and save it
        data = {
            "name": input_string,
            "description":"[System Note: Takes place in a discord text channel]",
            "global":"[System Note: Takes place in a discord server]",
            "instruction":"[System Note: Takes place in a discord text channel]"
            }
        with open(file_name, "w") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"File '{file_name}' created with content: {data}")
        return data
    
    
