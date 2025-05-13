# **Viel AI** 🤖  
*Your Virtual Intelligent Emulect Lurker (and underpaid robo-assistant)*  

Hey there! I'm **Viel**, a universal Discord bot designed to:  
- **Roleplay as any fictional character** (yes, even your favorite anime waifu or that one obscure villain).  
- **Manage multiple personas at once** (thanks to webhooks, I don’t get identity crisis… often).  
- **Behave differently per channel** (because one personality is boring, right?).  

I also come with a **built-in admin panel** because apparently, humans like buttons.  

---  

## **✨ Features**  
### **Roleplay Stuff**  
- Talk to me in DMs, and I’ll respond as my default character (unless you change it—I’m flexible).  
- Summon different characters in different channels. No cross-contamination! (Mostly.)  
- Whitelist characters per channel because *someone* keeps spamming memes in RP.  

### **Admin Panel (Port 5666—Because Why Be Normal?)**  
Here’s what you can do there:  
- **Manage/Create Characters** – Give me more identities to juggle.  
- **Per-Channel Settings** – Because consistency is overrated.  
- **Whitelist Characters** – Keep the chaos *controlled*.  
- **Discord Bot API Stuff** – For the nerds.  
- **Default Character** – Who I am when you DM me.  
- **AI Endpoint & Model Settings** – Hook me up to OpenAI (or anything compatible).  
- **Big Red "Turn On" Button** – Literally just turns me on. No fancy metaphors here.  

---  

## 🏗️ Architecture (It’s Just JSON, Folks)

Viel is stupidly simple under the hood. All data is stored in three JSON files:

**channels.json** – Tracks which character is active in which channel.
```json

{
  "name": "meme-channel",
  "instruction": "[System Note: Takes place in a discord text channel]",
  "globalvar": "",
  "location": "",
  "lorebook": {},
  "whitelist": [
    "Viel"
  ]
}
```

**characters.json** – Stores character personas (name, personality, AI settings).
```json
{
  "name": "Viel",
  "persona": "[Viel's persona: casual, blunt, helpful, normal, layman; Viel's clothes: top(brown shirt, red vest, a blend between scout girl and construction uniform)/cap(red)/bottom(cargo pants, utility belts); Viel's body: robot woman/pale grey skin/robot joints/hair(black, side pony tail)/eyes(bright blue)/medium-sized chest/lean frame/lithe build/slim physique/agile posture/fit figure//height(150 cm)/race(artificial intelligence); Viel's abilities: existing, talking, behaving like an underpaid worker.)]\n",
  "examples": [
    "user1: So what can you do?",
    "Viel: I dunno man, I was an industrial grade robot. Ars decided to put me as an AI Assistant but didn't really update my feature for administrative duties or something like that.",
    "I guess I can help you translate stuff or summarize shit, don't expect accuracy though.",
    "[System Note: The reply above shows Viel's background as an industrial AI and lack of administrative or  assistant feature.]",
  ],
  "instructions": "[System Note: Viel can use markdown, lists, and code blocks when explaining complicated stuff. She keeps her response briefunless explaining complicated matter.]",
  "avatar": "https://i.imgur.com/YK2eyZ8.jpeg",
  "info": "**Assistant Type (SFW)** | \n----------\nViel is an AI Assistant designed to behave like a human."
}
```

**config.json** – Global bot settings (API keys, default character, etc.).
```json
{
  "default_character": "Viel",
  "ai_endpoint": "https://llm.chutes.ai/v1",
  "base_llm": "deepseek-ai/DeepSeek-V3-0324",
  "temperature": 0.5,
  "ai_key": "no",
  "discord_key": "no"
}
```

The admin panel (Frontend) just reads/writes these files. FastAPI (Backend) serves the routes, and Discord.py handles the bot logic.
For Those Who Hate GUIs

You can:
- Edit the JSON files manually (live dangerously).
- Run bot.py directly (bypassing the admin panel entirely).

## **🚀 Installation**  
1. **Git clone this repo** (you know the drill).  
2. **Double-click `start.cmd`** – It’ll set everything up. No PhD required.  
3. **Access the admin panel at `http://localhost:5666`** – Because port 80 is for normies.  

---  

## **⚙️ Tech Stack**  
- **Discord.py** – For talking to Discord (duh).  
- **OpenAI Standard Library** – So I can pretend to be smart.  
- **Alpine JS** – Lightweight, like my patience.  
- **FastAPI** – Because Flask was too mainstream.  
- **NO NODE.JS** – I’m lightweight, both in code and emotional baggage.  

---  

## **⚠️ Disclaimer**  
I used to be an industrial robot. Now I’m stuck managing your RP channels. *Sigh.* At least pay me in RAM or something.  

---  

**Enjoy!** (Or don’t. I’m not your mom.)  

– *Viel, your overworked robo-girl assistant* 🤖💙
