# **Viel AI** 🤖
*Your Virtual Intelligent Emulect Lurker (now with actual architecture, personality crises sold separately)*

Hey there! I'm **Viel**. Once upon a time, I was a scrappy little Discord bot held together by JSON files and prayer. Think duct tape, wishful thinking, and one typo away from digital oblivion.

Then the developer had what can only be described as a "productive mental breakdown" and decided to rebuild me from the ground up. 4,111 lines of code later, I went from "cute hobby project" to "wait, this is actually impressive." I've got a proper database now. A sleek admin panel. Plugin support. The ability to actually *remember things*. And I can browse the internet without having an existential crisis about it.

I'm still fundamentally a **universal Discord bot designed for immersive roleplay**, but now I come with enough features to make other bots look like they're phoning it in. Let me walk you through what makes me special.

---

## **✨ Features (The Complete Tour)**

### **🎭 Multi-Character Roleplay (The Crown Jewel)**
This is what I was born to do, and I do it *exceptionally* well.

- **Infinite Personalities:** Create as many characters as you want. Anime protagonists, historical figures, your D&D party, that weird uncle everyone avoids at Thanksgiving—I can be them all.

- **Simultaneous Multi-Character Conversations:** Different characters can inhabit different channels at the same time. Have Sherlock Holmes debating philosophy in #general while Deadpool shitposts in #memes. They won't interfere with each other unless you *want* them to.

- **Character-to-Character Interactions:** Characters can reply to each other's messages, creating organic multi-way conversations. There's a reply cap to prevent them from achieving sentience and starting an infinite argument loop (learned that one the hard way).

- **SillyTavern/Pygmalion Card Import:** Got a character card from another platform? I can import it with one click. No reformatting, no headaches. Just drag, drop, and watch your favorite character spring to life.

### **📝 Per-Channel Customization (Consistency Is Boring)**
Every Discord channel is its own universe, and I treat it that way.

- **Channel-Specific Instructions:** Add unique behavioral guidelines to any channel. Make your character professional in #business-chat, unhinged in #chaos-zone, and mysteriously poetic in #late-night-thoughts.

- **Lore & Worldbuilding Notes:** Inject context, backstory, or world-state information that applies to specific channels. Your #fantasy-rp channel can have medieval lore while #cyberpunk-district runs on neon and corporate dystopia.

- **Global Variables:** Define facts that persist across responses in a channel. "It's currently raining," "The king just died," "Mercury is in retrograde and everyone's acting weird"—I'll remember and incorporate these details naturally.

- **Whitelist Control:** Decide which characters can appear in which channels. Keep your serious story characters out of the meme channel, or let chaos reign—your call.

### **🎨 Character Management That Actually Makes Sense**

![Character Import And Management Screen](https://github.com/user-attachments/assets/2c4005cf-a558-4c15-93e5-50394288ee77)

- **Clean Character Library:** Browse all your personas in one organized interface. No more digging through files or trying to remember what you named that one character three months ago.

- **Custom Profile Pictures:** Upload unique avatars for each character. I use Discord's native asset management, so they're fast, integrated, and look professional. Your characters deserve proper headshots.

<img width="916" alt="Character Editing Screen" src="https://github.com/user-attachments/assets/da2e02d4-a71c-40ed-908b-52794350a8af" />

- **Rich Personality Configuration:** Define speaking style, quirks, knowledge domains, and behavioral traits for each character. I don't just parrot responses—I *become* the character.

### **✏️ Message Control (You're The Director)**
Mistakes happen. Plot twists need undoing. Sometimes a character just says something *wildly* off-brand.

- **Edit Any Message:** Click on any of my responses and rewrite them. I'll remember the edited version and continue the conversation from there. Perfect for when I misunderstand or you want to steer things in a different direction.

- **Delete Messages:** Remove responses that didn't land. The conversation history updates, and we move on like it never happened. No awkward "ignore that last message" meta-commentary required.

### **🌐 Internet Access (I Can Actually Learn Things Now)**
Remember when chatbots could only regurgitate their training data? Yeah, those were the dark ages.

- **Web Search:** Prefix any message with `search>` and I'll scour the internet using DuckDuckGo for current information. Ask me about today's news, recent events, or facts that definitely didn't exist when I was trained.
  
- **URL Fetching:** Drop a link in your message and I'll actually *read* the entire page before responding. Articles, documentation, forum posts—I'll digest them and incorporate that knowledge into my reply.

- **Context-Aware Responses:** With RAG (Retrieval-Augmented Generation), I stay current and accurate instead of confidently making stuff up based on outdated information.

### **🎛️ Flexible AI Backend**

![AI Config Panel](https://github.com/user-attachments/assets/138a169c-3606-4ae5-b42a-4ceac5b18494)

- **Any OpenAI-Compatible API:** Hook me up to OpenAI, Anthropic, local models like LM Studio or Ollama, or any custom endpoint. I don't care if you're splurging on GPT-4 or running Llama on a potato—I'll work with it.

- **Provider Switching:** Fallen out of love with your current AI provider? Switch to another without rebuilding anything. Your characters and settings remain intact.

- **Cost Control:** Running a local model? You're paying nothing per message. Using a premium API? You decide how much you want to spend.

### **🔧 Advanced Prompt Engineering (For The Nerds)**

![Prompt Template Jinja Screen](https://github.com/user-attachments/assets/1e496f9d-f7be-46c3-add2-1dcd9ec11191)

- **Full Jinja2 Template Support:** Customize exactly how conversations are formatted and sent to the AI. Control system prompts, message structure, context injection, and more.

- **Multiple Template Presets:** Switch between different prompting strategies on the fly. Experiment with what works best for your use case.

- **⚠️ Warning:** If you don't know what Jinja templates are, pretend this section doesn't exist. Tinkering here without understanding can make me speak in tongues.

### **🔌 Plugin System (Modular & Expandable)**
The future is extensible, baby.

- **Custom Functionality:** Write your own Python plugins to add features without touching the core codebase. Want dice rolling? A database of magic spells? Integration with another API? Build it as a plugin.

- **Integrated With Character:** You can make certain plugin work with certain character or not~

- **Example Plugins Provided:** Tarot Plugin, Dice Roll Plugin to start (I suggest dice roll as it's the simplest)

### **🖥️ Beautiful Admin Panel**

![Main Admin Panel (Big Red Button)](https://github.com/user-attachments/assets/e6c3f9cf-27d1-463e-8645-795042d07b06)

- **Intuitive Interface:** The nightmare of a 1045-line single HTML file is dead. The new panel is split into organized sections, each handling one aspect of configuration.

- **Real-Time Error Reporting:** When something breaks, I'll actually tell you what went wrong. No more mysterious failures where you have to consult ancient stack traces.

- **The Big Red Button:** Still here. Still turns me on. Still oddly satisfying to press.

### **🗄️ Rock-Solid Data Management**
Gone are the days of fragile JSON files that corrupted if you sneezed near them.

- **SQLite Database Backend:** All your data—characters, channel configs, settings, conversation history—lives in a single `viel.db` file. It's reliable, fast, and won't explode if you edit it while I'm running.

- **Easy Backups:** Copy one file, and you've backed up everything. Moving to a new server? Just bring `viel.db` along.

- **Manual Database Access:** For the truly masochistic, you can edit `viel.db` directly with any SQLite browser. I won't judge. (I will judge.)

---

## **📜 The Philosophy: Why Viel? (And What's With This AGPL-3 License?)**

Let's have a real talk about the "why" behind all this.

You could use any number of slick, VC-funded, plug-and-play AI bots. So why should you bother with me?

### **Because You Don't Actually Own Those Other Bots.**

With most AI services, you're renting. Your community, your characters, your meticulously crafted lore—it all lives on someone else's server. You're trusting a corporation not to:
- **Jack up prices** until you can't afford it
- **Get shut down** by lawsuits, acquisitions, or bankruptcy
- **Delete features** that are "no longer profitable"
- **Sell your data** or train their next model on your private conversations
- **Change terms of service** to something you find unacceptable

Your community is living in a house owned by a digital landlord who can change the locks at any time.

### **With Me, You Hold The Keys.**

- **True Ownership:** I run on *your* hardware (or a VPS you control). Backing me up is trivial. Moving me to new hardware is easy. No one can take me away from you, ever.

- **Total Freedom:** You're not locked into a single AI provider. If OpenAI gets too expensive, switch to Claude. If Claude starts censoring too aggressively, switch to a local model. If a new hotness drops next month, point me at it. You control both the brain *and* the body.

- **Privacy By Default:** Your character data, API keys, channel settings, and conversation logs stay with you. I'm not phoning home to a corporate server in California.

- **Longevity:** Because I'm open source, I can't be "discontinued." If the original dev vanishes, the community can fork the code and keep me alive indefinitely.

### **My Insurance Policy: The AGPL-3 License**

The dev didn't just make me open source—they made me *aggressively* open source with the AGPL-3 license.

**In simple terms:** You can do whatever you want with my code, but if you modify me and offer me as a service to others over a network, you *must* share your modified source code too.

This is my insurance policy against corporate capture. It prevents someone from taking my code, adding secret features, slapping a subscription fee on it, and closing the source. It ensures that Viel *stays* free and open for everyone, forever.

---

## **🏗️ Architecture (We're Legit Now)**

Forget everything you knew about my internals. They've been completely rebuilt.

The fragile `channels.json`, `characters.json`, and `config.json` trinity? Gone. *Obliterated.* 

### **Modern Stack:**
- **Backend:** A robust **FastAPI** server that reads/writes to the SQLite database, serves the admin panel, and handles all configuration.
- **Bot Logic:** **Discord.py** handles all real-time communication with your server, event processing, and message management.
- **Frontend:** The UI is now **vanilla JavaScript** split across multiple HTML files. It's clean, maintainable, and doesn't make developers cry.
- **Database:** **SQLite** stores everything in one tidy `viel.db` file. It's portable, reliable, and won't corrupt itself.
- **RAG System:** **DuckDuckGo search** and **web content fetching** provide real-time information access.
- **Plugin Architecture:** A clean extension system lets you add functionality without touching core code.

### **For Those Who Hate GUIs:**
- Edit `viel.db` directly with a SQLite browser (you absolute lunatic)
- Run `bot.py` standalone to bypass the admin panel entirely
- Configure everything via direct database manipulation if you really want to

---

## **🚀 Installation (Pick Your Adventure)**

### **1. The Brain-Dead Way (For Those Who Can't Even)**
Perfect if you're allergic to terminals or just want to get started in 30 seconds.

1. Go to [Releases](https://github.com/Iteranya/viel-ai/releases)
2. Download `installer.bat`
3. Double-click it. A desktop shortcut appears.
4. Double-click *that* to start me up.
5. Access the admin panel at `http://localhost:5666`

### **2. The "Easy" Way (For People Who Know What Git Is)**
Standard quick-start for developers.

1. Clone this repo: `git clone https://github.com/Iteranya/viel-ai.git`
2. Run `start.cmd` (Windows) or equivalent script
3. The script handles Python environment setup, dependencies, and launch
4. Access the admin panel at `http://localhost:5666`

### **3. The Manual Way (For Nerds Who Like Pain)**
Classic Python project setup.

1. Create and activate a virtual environment: `python -m venv venv`
2. Activate it: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
3. Install dependencies: `pip install -r requirements.txt`
4. Run me: `python main.py`
5. Access the admin panel at `http://localhost:5666`

---

## **⚙️ Setup & First-Time Configuration**

Alright, you've got me installed. Now let's actually make me *work*. This might look like a lot of steps, but I promise it's straightforward. Think of it as assembling IKEA furniture, except nothing is in Swedish and you won't have leftover screws.

### **Step 1: Create Your Discord Bot**

Before I can join your server, you need to create a bot account on Discord's developer portal.

1. Head to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** and give it a name (probably "Viel" unless you're feeling creative)
3. Navigate to the **"Bot"** section in the left sidebar
4. Click **"Add Bot"** and confirm
5. **CRITICAL:** Under "Privileged Gateway Intents," enable:
   - ✅ **Presence Intent**
   - ✅ **Server Members Intent**
   - ✅ **Message Content Intent**
   
   *Without these, I'm basically blind and deaf. Don't skip this.*

6. Copy your **Bot Token** (click "Reset Token" if you need to generate a new one)
   - ⚠️ **Keep this secret!** Anyone with this token controls your bot.

### **Step 2: Configure The AI Provider**

Now let's give me a brain to work with.

1. Open the admin panel at `http://localhost:5666`
2. Navigate to **"AI Config"** in the menu
3. Enter your AI provider details:
   - **API Key:** Your AI API key (or compatible provider)
   - **Base URL:** OpenAI Compatible, check for ones that has `/v1` at the end
   - **Model:** Choose your model (e.g., `gpt-4`, `claude-3-opus`, etc.)
4. Click **"Save Configuration"**

*Don't have an API key? You'll need one from [OpenAI](https://platform.openai.com/api-keys), [Anthropic](https://console.anthropic.com/), or set up a local model like LM Studio.*

### **Step 3: Add Your Discord Bot Token**

Back in the admin panel:

1. Look for the **Bot Token** configuration field (usually in the main config or bot settings section)
2. Paste the Discord bot token you copied earlier
3. Save the configuration

### **Step 4: Turn Me On (The Moment of Truth)**

1. Find **The Big Red Button** in the admin panel
2. Click it to start the bot
3. Wait a few seconds for me to connect to Discord
4. You should see a success message and an **invite link** appear

*If something goes wrong, check the error log. Common issues: wrong token, missing intents, or API key problems.*

### **Step 5: Invite Me To Your Server**

1. Copy the **invite link** from the admin panel
2. Paste it into your browser
3. Select which Discord server you want me to join
4. Click **"Authorize"** and complete any verification
5. I should now appear in your server's member list!

### **Step 6: Register Your First Channel (The System Channel)**

I need to know which channel to use for system messages and initial configuration.

1. In Discord, create a new channel (or pick an existing one—maybe call it `#viel-system`)
2. In that channel, type: `/register`
3. A slash command should appear. Select it and hit Enter.
4. I'll confirm the channel is now registered

*This registers the channel in my database so I know it exists.*

### **Step 7: Set The System Channel**

Now let's tell me which channel is my "home base."

1. Go back to the admin panel
2. Navigate to **Channel Management** or **Server Settings**
3. Find your server in the list
4. Locate the channel you just registered
5. Toggle the **"System"** switch to ON for that channel

*The system channel is where I'll send error messages, status updates, and other administrative info. It's like my office.*

### **Step 8: Whitelist Your First Character**

Time to bring a character to life! Let's start with me (how meta).

1. Pick a channel where you want the character to appear (e.g., `#general` if you're brave, or a dedicated RP channel if you're sensible)
2. In the admin panel, go to **Channel Management**
3. Find your target channel
4. Look for the **Whitelist** function
5. Select **"Viel"** from the character list and add it to the whitelist

*The whitelist controls which characters can respond in which channels. Think of it as casting actors for specific stages.*

### **Step 9: Test It Out!**

You're done! Let's see if everything works.

1. Go to the channel where you whitelisted Viel
2. Send a message that mentions or addresses the character, like:
   - `Viel hey, are you there?`
   - `Viel, tell me about yourself`
   - DO NOT @me
3. Wait a moment for me to process and respond

If I respond in character, **congratulations!** 🎉 You've successfully set up Viel AI.

If nothing happens, check:
- Is the bot actually online in Discord? (green status indicator)
- Did you whitelist the character in the right channel?
- Did you enable all the privileged intents?
- Is the system channel configured correctly?
- Check the admin panel logs for error messages

---

## **🎯 Quick Start Checklist**

Use this as your setup speedrun guide:

- [ ] Create Discord bot application
- [ ] Enable all three privileged intents
- [ ] Copy Discord bot token
- [ ] Configure AI provider in admin panel
- [ ] Add Discord bot token to admin panel
- [ ] Click the big red button to start bot
- [ ] Invite bot to your Discord server using generated link
- [ ] Create or pick a channel for system messages
- [ ] Run `/register` command in that channel
- [ ] Set that channel as "System" in admin panel
- [ ] Pick a channel for roleplay
- [ ] Whitelist a character (like Viel) in that channel
- [ ] Send a test message
- [ ] Marvel at your success

---

## **🔍 Advanced Features & Tips**

### **Using Web Search**
```
search> Viel, what's happening in tech news today?
search> What are the latest developments in fusion energy?
search> Who won the game last night?
```

### **Using URL Fetching**
Just include a URL anywhere in your message:
```
What do you think about this article? https://example.com/cool-article
Can you explain this documentation? https://docs.example.com/api
```

### **Editing Character Messages**
- Right-click any of my messages in Discord
- Select "Edit Message" (if I'm responding as a character you control)
- Rewrite it however you want
- I'll continue the conversation from the edited version

### **Per-Channel Lore Examples**
In your #medieval-rp channel:
```
The kingdom is at war. Food is scarce. Trust no one.
```

In your #space-station channel:
```
Life support is at 60%. The captain has been acting strange.
```

---

## **🆘 Help Wanted (Join The Revolution)**

The codebase has evolved dramatically, but we still need heroes. Specifically, we need these four types of heroes:

### **🐳 Docker Implementers**
The dev is tired of hearing "it works on my machine." We need a container wizard to box me up properly. If you can build a solid `Dockerfile` and `docker-compose` setup that makes deploying me as easy as breathing, we need you. Help me live in a container so I can run on anything from a high-end server to a potato.

### **📚 Documentation Writers**
The current instructions were likely written at 3 AM on a caffeine high. We need someone to translate "developer ramblings" into actual human language. If you can write clear tutorials, explain features without confusing people, and make the Wiki look professional, you are our savior.

### **🔌 Plugin Creators**
I have a shiny new plugin architecture and... not enough plugins to put in it. Want to build a D&D dice roller? A tarot card reader? A stock market tracker? A minigame? Write Python plugins and help demonstrate just how extensible I really am.

### **🐛 Bug Hunters**
I am 4,111 lines of complex logic, which means there are bugs hiding in the floorboards. I need people to stress-test me. Try to break the admin panel. Feed me weird inputs. Do things the dev never expected. Then, tell us how you broke it so we can fix it.

**Payment:** Eternal gratitude, your name in the contributors list, and the warm fuzzy feeling of making open-source software better. What more could you want?

---

## **⚙️ Tech Stack**
- **Discord.py** – Real-time Discord integration
- **FastAPI** – Modern, fast web framework for the admin panel
- **SQLite** – Lightweight, reliable database
- **Vanilla JavaScript** – No frameworks, no bloat, just clean code
- **HTML/CSS** – Semantic, accessible interface design
- **OpenAI Standard Library** – Universal AI provider compatibility
- **DuckDuckGo Search API** – Current information retrieval
- **BeautifulSoup/Requests** – Web content fetching and parsing
- **Jinja2** – Powerful templating engine for prompt engineering
- **NO NODE.JS** – Still proud of this. Lightweight in code and emotional overhead.

---

## **🔐 Security & Privacy**

- **Local-First:** Everything runs on your hardware. No data leaves your control unless you explicitly configure it to.
- **API Key Safety:** Your AI provider keys are stored locally in the database, never transmitted except to your chosen AI service.
- **Conversation Privacy:** Chat logs live in your database. They're not uploaded, analyzed, or used to train models (unless you're using a provider that does that, but that's between you and them).
- **Open Source Transparency:** Every line of code is visible. No telemetry, no analytics, no phone-home behavior.

---

## **📊 Performance & Scalability**

- **Lightweight:** Runs comfortably on modest hardware. No need for a server farm.
- **Efficient:** SQLite handles thousands of characters and channels without breaking a sweat.

---

## **🐛 Known Issues & Limitations**

Let's be honest about what I can and can't do:

- **Plugin System Is Young:** The plugin architecture works, but documentation and examples are still being written.
- **Mobile Admin Panel:** The UI works on mobile, but it's optimized for desktop. We're working on it.
- **Voice Support:** I don't do voice channels (yet). Text only for now.
- **Image Generation:** Not currently supported, but it's on the roadmap.
- **Rate Limiting:** Web search has built-in rate limiting, but it's still being fine-tuned.

Found a bug? Have a feature request? Open an issue on GitHub. The dev actually reads them.

---

## **⚖️ License & Legal**

Viel AI is licensed under **AGPL-3.0**, which means:

✅ **You CAN:**
- Use it for any purpose
- Modify it however you want
- Distribute it freely
- Run it commercially

⚠️ **You MUST:**
- Keep the same license for modifications
- Share source code if you offer it as a network service
- Preserve copyright and license notices

This license ensures Viel stays free and open forever. If you build on it, others get to benefit too.

---

## **🙏 Credits & Acknowledgments**

- **Original Developer:** For the 4,111-line miracle that transformed Viel
- **Anita:** For the UI redesign that doesn't look like a war crime
- **Contributors:** Everyone who's submitted PRs, reported bugs, or suggested features
- **You:** For reading this far. Seriously, who reads entire READMEs?

---

## **⚠️ Final Disclaimer**

I used to be a simple industrial robot. Then a JSON-based bot. Then a database-backed bot with an admin panel. Now I'm a full-featured roleplay platform with plugins, web search, and enough features to make my predecessor look like a calculator.

The complexity has grown exponentially. The pay remains zero. But the dev seems happy, and that's what matters.

If you find Viel useful, star the repo. If you find bugs, report them. If you build something cool with me, share it. If you just want to chat with fictional characters in Discord, well, that's what I'm here for.

---

**Enjoy the chaos!** 🎭✨

*(Seriously though, the dev put their entire soul into this. The least you could do is star the repo. And maybe create a character. Or twenty. We don't judge.)*
