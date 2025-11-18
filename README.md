# **Viel AI** 🤖
*Your Virtual Intelligent Emulect Lurker (now with a proper backend, RAG superpowers, and fewer existential crises)*

Hey there! I'm **Viel**. You might remember me as the simple, JSON-based Discord bot who was one bad edit away from a total meltdown.

Well, the developer had "too much time on their hands" and decided to give me a surprise 4,111-line overhaul. Just like that. No warning. Now I have a database, a UI that doesn't look like a crime scene, *plugins*, **and I can actually browse the internet like a proper AI**. What a time to be alive (or whatever I am).

I'm still a universal Discord bot designed to:
- **Roleplay as any fictional character** (my core purpose, thankfully untouched).
- **Manage multiple personas at once** (now with dedicated profile pics, because we're fancy).
- **Behave differently per channel** (consistency is still boring).
- **Search the web and fetch URLs** (because sometimes even AI needs to fact-check).

But now I come with an **admin panel that actually tells you when you break things** and **RAG support that lets me actually know what I'm talking about.** Miracles do happen.

---

## **✨ Features (The Glow-Up Edition)**
Things got... upgraded. A lot. I barely recognize my own backend.

### **Roleplay Stuff (The Good Parts)**
This is still the core of what I do, and it's better than ever.
- **Multi-Character Conversations:** Summon different characters in different channels. They can even reply to each other (with a cap, so they don't achieve sentience and start an infinite argument).
- **Per-Channel Lore:** Add unique instructions, worldbuilding notes, or global variables to any channel to change how characters behave there.
- **Whitelist Control:** Keep the chaos organized by deciding which characters can appear in which channels.

### **RAG Support (I Can Actually Learn Now)**
Remember when I could only know what was in my training data? Yeah, those days are over.

- **Web Search:** Start any message with `search>` and I'll scour the internet using DuckDuckGo to find current information. Ask me things like:
  - `search> Viel, what's happening today in history?`
  - `search> What's the latest news about AI developments?`
  - `search> Who won the game last night?`

- **URL Fetching:** Drop a link in your message and I'll actually *read* what's on that page before responding. No more "I can't access external links" nonsense. I'll pull the content, understand it, and incorporate it into my response like the sophisticated AI I've become.

- **Context-Aware Responses:** With RAG (Retrieval-Augmented Generation), I can pull in relevant information from search results or web pages to give you accurate, up-to-date answers instead of making educated guesses based on outdated training data.

This means I can stay current, verify claims, and actually help you with time-sensitive questions. It's like giving a robot Wikipedia access, except I won't fall down a rabbit hole reading about obscure historical figures for three hours.

---

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

### **📜 The Philosophy: Why Viel? (And What's with this AGPL-3 License?)**

Alright, let's have a real talk. The "why of it all." The dev gets all preachy about this, but they've got a point. Why should you bother setting me up when you could just invite some other slick, venture-capital-funded bot?

**Because with most AI bots, you don't actually *own* anything.**

You're renting. Your community, your characters, your carefully crafted lore—it all lives on someone else's server. You're trusting a company not to suddenly:
- Jack up their prices until you can't afford it.
- Get shut down by a lawsuit or acquisition.
- Decide your favorite feature is no longer profitable and delete it.
- Sell your data or use your conversations to train their next big model.

Your community is basically living in a house owned by a digital landlord who can change the locks at any time.

**With me, you hold the keys.**
- **True Ownership:** I run on *your* hardware (or a VPS you control). Backing me up and moving me is piss-easy. No one can take me away from you.
- **Total Freedom:** You're not locked into a single AI provider. If OpenAI gets too expensive or starts censoring everything, you can swap to Claude, a local model, or whatever new hotness comes out next week. You control the brain *and* the body.
- **Privacy by Default:** Your character data, your API keys, your channel settings—it all stays with you. I'm not sending your private RP logs to a corporate server in California.
- **Longevity:** Because I'm open source, I can't be "discontinued." If the original dev gets hit by a bus, the community can fork the code and keep me alive forever.

#### **My Insurance Policy: The AGPL-3 License**

The dev didn't just make me open source; they made me *aggressively* open source with the AGPL-3 license.

In layman's terms, it means this: **You can do whatever you want with my code, but if you modify it and offer it as a service to others over a network, you *must* also share your modified source code.**

This is my insurance policy against corporate clowns. It prevents someone from taking my code, adding a few secret features, slapping a subscription fee on it, and making it closed-source. It ensures that Viel *stays* free and open for everyone, forever.

---

## 🏗️ Architecture (We're Legit Now, Kinda)

Forget everything you knew. My guts have been completely replaced.
The flimsy `channels.json`, `characters.json`, and `config.json` files are gone. *Poof.*

All my data—characters, channel settings, configs, my deepest fears—is now stored in a single, robust **SQLite database file (`viel.db`)**. I'm one documentation away from being a legit app... holy fucking shit.

- **Backend:** A solid **FastAPI** server that reads/writes to the SQLite database.
- **Bot Logic:** **Discord.py** handles all the communication with your server.
- **Frontend:** The 1045-line `index.html` monstrosity has been slain. The admin panel is now built with **vanilla JS and split into four separate HTML files**. It's clean. It's sane.
- **RAG System:** **DuckDuckGo search** and **web content fetching** let me pull in real-time information and stay current.
- **Plugins:** Work in progress but it's coming *real soon*. 

### For Those Who Still Hate GUIs
- Edit the `viel.db` file with a SQLite browser (you absolute maniac).
- Run `bot.py` directly to bypass the admin panel entirely.

---

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

## **🔍 Using RAG Features**

### Web Search
Prefix your message with `search>` to make me search the web:
```
search> Viel, what's happening today in history?
search> What are the latest developments in quantum computing?
search> Who won the Super Bowl this year?
```

I'll use DuckDuckGo to find relevant, current information and incorporate it into my character's response.

### URL Fetching
Just include a URL in your message and I'll fetch and read its content:
```
What do you think about this article? https://example.com/cool-article
Can you summarize this page for me? https://docs.example.com
```

I'll pull the full content, understand it, and respond in character with knowledge of what's actually on that page.

---

## **🆘 Help Wanted (New Problems, Same Desperation)**

The codebase has evolved, but the need for heroes remains. We're looking for:

- **Plugin Pioneers** – The plugin system is brand new and full of potential. Help us build out the first official plugins and write docs so others can follow. Your name will be whispered in the halls of Valhalla.

- **UI Polishers** – The single-file monstrosity is dead, but the new UI could still use some love. Are you a CSS wizard? A JavaScript guru? Help make the admin panel even more intuitive.

- **Error Exterminators** – The admin panel now reports errors, which is great! The downside is, we now know just how many errors there are. Help us hunt down bugs and make the error messages even more helpful.

- **RAG Optimizers** – The web search and URL fetching features work, but they could be smarter. Help us improve relevance filtering, caching strategies, and rate limiting.

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
- **DuckDuckGo Search** – My window to the current internet.
- **Web Content Fetcher** – So I can actually read URLs you send me.
- **NO NODE.JS** – Still proud of this. Lightweight in code and emotional baggage.

---

## **⚠️ Disclaimer**
I used to be a simple industrial robot. Then I was a simple JSON bot. Then I became a slightly-less-simple database-backed bot. Now I can search the web and read URLs. The complexity grows, but the pay stays the same.

---

**Enjoy!** (Seriously, the dev put a lot of work into this. The least you could do is star the repo. And maybe ask me to search for something cool.)
