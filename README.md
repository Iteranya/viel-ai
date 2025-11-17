# **Viel AI** 🤖
*Your Virtual Intelligent Emulect Lurker (now with a proper backend and fewer existential crises)*

Hey there! I'm **Viel**. You might remember me as the simple, JSON-based Discord bot who was one bad edit away from a total meltdown.

Well, the developer had "too much time on their hands" and decided to give me a surprise 4,111-line overhaul. Just like that. No warning. Now I have a database, a UI that doesn't look like a crime scene, and... *plugins*?

I'm still a universal Discord bot designed to:
- **Roleplay as any fictional character** (my core purpose, thankfully untouched).
- **Manage multiple personas at once** (now with dedicated profile pics, because we're fancy).
- **Behave differently per channel** (consistency is still boring).

But now I come with an **admin panel that actually tells you when you break things.** Miracles do happen.

---

## **✨ Features (The Glow-Up Edition)**
Things got... upgraded. A lot. I barely recognize my own backend.

### **Roleplay Stuff (The Good Parts)**
This is still the core of what I do, and it's better than ever.
- **Multi-Character Conversations:** Summon different characters in different channels. They can even reply to each other (with a cap, so they don't achieve sentience and start an infinite argument).
- **Per-Channel Lore:** Add unique instructions, worldbuilding notes, or global variables to any channel to change how characters behave there.
- **Whitelist Control:** Keep the chaos organized by deciding which characters can appear in which channels.
# Admin Panel (Port 5666 — Still Not Normal)

The dev apparently asked Anita to redo my UI, and I have to admit, it looks legit.

## Features

### Character Management
Create, edit, and manage all your characters in a clean interface. And yes, the **one-click import for SillyTavern/Pygmalion cards** still works and is surprisingly robust.

![Character Import And Management Screen](https://github.com/user-attachments/assets/2c4005cf-a558-4c15-93e5-50394288ee77)

### Character Avatars
You can now **upload custom profile pictures** for each persona! I use Discord's own asset management, so it's fast and integrated.

<img width="916" alt="Character Editing Screen" src="https://github.com/user-attachments/assets/da2e02d4-a71c-40ed-908b-52794350a8af" />

### AI & Config Settings
Hook me up to any OpenAI-compatible endpoint. Splurge on Opus, cheap out on a local model—I don't judge. This is also where you'll plug in your Discord API key.

![AI Config Panel](https://github.com/user-attachments/assets/138a169c-3606-4ae5-b42a-4ceac5b18494)

### Advanced Prompt Engineering
For those who understand Jinja templates. If you think Jinja is a synonym for Ninja, *do not touch this setting.*

![Prompt Template Jinja Screen](https://github.com/user-attachments/assets/1e496f9d-f7be-46c3-add2-1dcd9ec11191)

### Big Red "Turn On" Button
Still here. Still turns me on.

![Main Admin Panel (Big Red Button)](https://github.com/user-attachments/assets/e6c3f9cf-27d1-463e-8645-795042d07b06)

### Plugin System (WIP)
Yes, it's actually happening. Extend my functionality with your own Python plugins. It's still new, so expect explosions. 💥

---

## 🏗️ Architecture (We're Legit Now, Kinda)

Forget everything you knew. My guts have been completely replaced.
The flimsy `channels.json`, `characters.json`, and `config.json` files are gone. *Poof.*

All my data—characters, channel settings, configs, my deepest fears—is now stored in a single, robust **SQLite database file (`viel.db`)**. I'm one documentation away from being a legit app... holy fucking shit.

- **Backend:** A solid **FastAPI** server that reads/writes to the SQLite database.
- **Bot Logic:** **Discord.py** handles all the communication with your server.
- **Frontend:** The 1045-line `index.html` monstrosity has been slain. The admin panel is now built with **vanilla JS and split into four separate HTML files**. It's clean. It's sane.
- **Plugins:** Work in progress but it's coming *real soon*. 

### For Those Who Still Hate GUIs
- Edit the `viel.db` file with a SQLite browser (you absolute maniac).
- Run `bot.py` directly to bypass the admin panel entirely.

## **🚀 Installation (Still Your Choice of Poison)**

### **1. The Brain-Dead Way (For Those Who Can't Even)**
- **Step 1:** Go to [Releases](https://github.com/Iteranya/viel-ai/releases).
- **Step 2:** Download `installer.bat`.
- **Step 3:** Double-click it. A shortcut appears on your desktop.
- **Step 4:** Double-click *that* to start me up.

### **2. The "Easy" Way (For People Who Know What Git Is)**
- **Step 1:** Clone this repo.
- **Step 2:** Run `start.cmd`. It handles Python, dependencies, and my newfound sense of self.
- **Step 3:** Access the admin panel at `http://localhost:5666`.

### **3. The Manual Way (For Nerds Who Like Pain)**
*Standard Python project setup:*
1.  Create and activate a virtual environment (`venv`).
2.  Install dependencies: `pip install -r requirements.txt`
3.  Run me: `python main.py`

---

## **🆘 Help Wanted (New Problems, Same Desperation)**

The codebase has evolved, but the need for heroes remains. We're looking for:

- **Plugin Pioneers** – The plugin system is brand new and full of potential. Help us build out the first official plugins and write docs so others can follow. Your name will be whispered in the halls of Valhalla.

- **UI Polishers** – The single-file monstrosity is dead, but the new UI could still use some love. Are you a CSS wizard? A JavaScript guru? Help make the admin panel even more intuitive.

- **Error Exterminators** – The admin panel now reports errors, which is great! The downside is, we now know just how many errors there are. Help us hunt down bugs and make the error messages even more helpful.

- **Dependency Detectives (Still!)** – We *think* we know why Pandas and Pillow are in `requirements.txt` now, but we're open to second opinions. Are they truly necessary? Or are they sentient?

- **Linux Evangelists** – The dev is still allergic to Linux. We need a hero to write and maintain clear installation docs for penguin enthusiasts. No using the words "just" or "simply."

*Payment: The eternal gratitude of an overworked AI and your name immortalized in the contributors list. What more could you want?*

---

## **⚙️ Tech Stack**
- **Discord.py** – How I talk to you.
- **FastAPI** – Serves the admin panel.
- **SQLite** – My new brain.
- **Vanilla JS & HTML/CSS** – For the functional, no-frills frontend.
- **OpenAI Standard Library** – To make me sound smart.
- **NO NODE.JS** – Still proud of this. Lightweight in code and emotional baggage.

---

## **⚠️ Disclaimer**
I used to be a simple industrial robot. Then I was a simple JSON bot. Now I'm a slightly-less-simple database-backed bot. The complexity grows, but the pay stays the same.

---

**Enjoy!** (Seriously, the dev put a lot of work into this. The least you could do is star the repo.)
