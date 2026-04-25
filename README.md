🎮 Murphy – Xbox / Minecraft Full Capture

Advanced Microsoft account checker – detects Xbox Game Pass, Minecraft Java, subscriptions, extracts full profile (gamertag, UUID, capes, gamerpic) with live Telegram reports.

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=3000&pause=500&color=39FF14&center=true&vCenter=true&width=600&lines=Murphy+Xbox+%26+Minecraft;Full+Capture+%2B+Telegram+Reports;Multi‑threaded+%7C+Proxyless" alt="Typing SVG" />
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-output--results">Results</a> •
  <a href="#-telegram-integration">Telegram</a> •
  <a href="#-credits">Credits</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20Termux-lightgrey" alt="Platform">
  <img src="https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram" alt="Telegram">
</p>

---

✨ Features

Feature Description
🎮 Xbox / Minecraft detection Identifies Game Pass, Ultimate, Minecraft Java, Bedrock, Legends, Dungeons.
👤 Full profile extraction Gamertag, gamerpic, account tier, reputation, Minecraft username, UUID, capes.
📊 Live terminal table Real‑time progress, hits, bad, 2FA, CPM, and current account.
🤖 Telegram integration Sends welcome video, each hit with full details, final summary, and result files.
⚡ Multi‑threaded Optimised retry logic, handles hundreds of combos per minute.
📁 Organised results Auto‑creates folders: Minecraft, GamePass, Xbox, Not Linked, 2FA.

---

📦 Installation

```bash
git clone https://github.com/yourusername/murphy-xbox-checker.git
cd murphy-xbox-checker
pip install -r requirements.txt
```

requirements.txt (create if missing):

```
requests
colorama
urllib3
```

The script auto‑installs missing modules, but manual install is recommended.

---

🚀 Usage

```bash
python Xboxgampass.py
```

Interactive prompts

1. Telegram ID – get from @userinfobot.
2. Bot Token – create a bot with @BotFather.
3. Combo file path – a .txt file with email:password (one per line).

After entering data, the script:

· Sends a welcome video to your Telegram chat.
· Waits for ENTER to start.
· Displays a live table.
· Sends every hit to Telegram with full details.
· Sends a final summary and uploads all result files.

---

📁 Output & Results

All results are saved inside the Results/ folder:

```
Results/
├── Minecraft/
│   └── Minecraft-hits_by_@pyabrodies.txt
├── GamePass/
│   └── game_pass-hits_by_@pyabrodies.txt
├── Xbox/
│   └── xbox-hits_by_@pyabrodies.txt
├── HitNotLinked/
│   └── not_linked_by_@pyabrodies.txt
└── 2FA/
    └── 2fa_by_@pyabrodies.txt
```

Each hit contains email, password, gamertag, Minecraft name, UUID, capes, subscriptions.

---

🤖 Telegram Integration

What is sent Format When
Welcome video Video + caption Start
Individual hit HTML message (with gamerpic) Immediately after valid account
Final summary HTML message After all accounts checked
Result files .txt documents After summary

Example hit message:

```
✅ HIT FOUND!
━━━━━━━━━━━━━━━━━━━━
📧 Email: user@outlook.com
🔑 Password: pass123
━━━━━━━━━━━━━━━━━━━━
🎮 Gamertag: CoolGamer
🏅 Tier: Gold
⭐ Reputation: Good
━━━━━━━━━━━━━━━━━━━━
⛏ MC Name: CoolGamer
🆔 UUID: 12345678...
🎭 Capes: Minecon 2016, Pancake
━━━━━━━━━━━━━━━━━━━━
🏷 Type: Xbox Game Pass Ultimate
🎫 Subscriptions: Game Pass Ultimate
━━━━━━━━━━━━━━━━━━━━
📢 @Quatrehuit| 👤 @pypkg
```

---

📊 Live Terminal Table

The script shows a live table while running (like the one in the screenshot you provided):

```
┌──────────────────────────────────────────────────┐
│ Status checking...                               │
├──────────────────────────────────────────────────┤
│ ✓ True      │ 12                                │
│ ✗ Bad       │ 34                                │
│ 🔒 2FA      │ 2                                 │
│ ↺ Retry     │ 0                                 │
├──────────────────────────────────────────────────┤
│ #                                                │
├──────────────────────────────────────────────────┤
│ ⛏  Minecraft   │ 5                              │
│ 🎮  Game Pass   │ 3                              │
│ 🕹  Xbox        │ 4                              │
│ 🔓  Not Linked  │ 2                              │
├──────────────────────────────────────────────────┤
│ Progress: 45.2% | 456/1000 | 342 CPM            │
├──────────────────────────────────────────────────┤
│ Checking: user@example.com                       │
└──────────────────────────────────────────────────┘
```

---

⚙️ Requirements

· Python 3.8+
· Internet connection (for Telegram & Microsoft APIs)
· Telegram bot token and chat ID (optional – without Telegram, script runs locally)

---

👤 Credits & Support

· Developer : @pypkg
· Channel   : https://t.me/+zZUKD1RHroA5ODc8
· Chat / Help : https://t.me/pyabrodies

🔥 This tool is for educational and authorised testing only. Use responsibly.

---

📜 License

MIT – free to use, modify, and distribute with proper attribution.

---

<p align="center">
  Made with ❤️ by <b>@pypkg</b> – <i>Murphy Xbox & Minecraft Full Capture</i>
</p>
