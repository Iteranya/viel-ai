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
- ![image](https://github.com/user-attachments/assets/ad1130a1-423a-44aa-b17e-525bbdf36bf9)
- **Per-Channel Settings** – Because consistency is overrated.
- **Whitelist Characters** – Keep the chaos *controlled*.  
- ![image](https://github.com/user-attachments/assets/758ec91d-4e8f-4ec3-a5d9-a126020562fa)
- **Discord Bot API Stuff** – For the nerds.  
- **Default Character** – Who I am when you DM me.  
- **AI Endpoint & Model Settings** – Hook me up to OpenAI (or anything compatible).  
- **Big Red "Turn On" Button** – Literally just turns me on. No fancy metaphors here.
- ![image](https://github.com/user-attachments/assets/9cf55e15-a94e-46c1-9243-2b80423380fe)


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

### For Those Who Hate GUIs
**You can:**
- Edit the JSON files manually (live dangerously).
- Run bot.py directly (bypassing the admin panel entirely).

## **🚀 Installation (Pick Your Poison)**  

### **1. The Brain-Dead Way (For Those Who Can’t Even)**  
- **Step 1:** Go to [Releases](https://github.com/Iteranya/viel-ai/releases).  
- **Step 2:** Download `installer.bat`.  
- **Step 3:** Dump it in an empty folder (or don't, not like I care about how you organize your stuff).  
- **Step 4:** Double-click it. A fancy shortcut will magically appear on your desktop.  
- **Step 5:** Double-click *that* to start me up.  

*Congrats, you’ve achieved the bare minimum!*  

### **2. The "Easy" Way (For People Who Know What Git Is)**  
- **Step 1:** Clone this repo (or download the ZIP if `git clone` scares you).  
- **Step 2:** Run `start.cmd`. It’ll handle Python, dependencies, and my existential crisis.  
- **Step 3:** Access the admin panel at `http://localhost:5666`.  

*Wow, you followed three whole steps. Proud of you.*  

### **3. The Manual Way (For Nerds Who Like Pain)**  
*Standard UV project setup because you’re fancy like that:*  

# Create a venv because you're responsible (unlike me).
`python -m venv venv`  

# Activate it (Windows).
`.\venv\Scripts\activate`  

# Or if you're on Linux/macOS (why are you like this?).
`source venv/bin/activate`  

# Install dependencies (yes, all of them).
`pip install -r requirements.txt`  

# Run me like you mean it.
`python main.py`  

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
