import os
import threading
from flask import Flask
import discord
from discord.ext import commands
import requests

# ==========================================
# 1. Render Web Service Keep-Alive Server
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# ==========================================
# 2. Bot Configuration & Credentials
# ==========================================
TOKEN    = os.environ.get("DISCORD_TOKEN")
GUILD_ID = 1525181999147388958

# Sirf aapki ID allow rahegi
ALLOWED_USER_IDS = [
    1525179499602509977
]

API_URL  = "https://auth.terminalx999.online/api_admin.php"
API_KEY  = os.environ.get("API_KEY", "TX999_1fc0134c4c418cf9f0817f355ac10cf7e5f73cf899a83bbf4731e4eec3929870")
APP_ID   = "9f087d585fbd666572fc24b7"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

DENIED_MESSAGE = "⛔ Access Denied: For use contact Super Admin PERSISTX !"

PACKAGE_NAMES = {
    "e52c1515c53453b85d0d4e87": "BASIC PANEL",
    "affc8da8fd5ace99981ab877": "AIMSILENT EXE",
    "cb921031dc43197e8ccb6828": "UID BYPASS",
    "3d1c6c948b4715fbd2fada2d": "EXTERNAL PANEL",
    "d4f0ce93349f236711344cb5": "PVT AIMKILL",
    "154d1edaddd7203fbfd847f4": "VAULT PANEL",
    "db3b90e8134ec738b94a9b05": "LIB BYPASS",
    "2411bc9db9f9a66c6e876ad2": "FPS BOOSTER"
}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Bulletproof key parser from Lib bot
def parse_keys(data):
    keys = []
    raw = data.get("data")
    if isinstance(raw, list):
        keys = [str(i.get("key", i)) if isinstance(i, dict) else str(i) for i in raw]
    elif isinstance(raw, dict):
        k_list = raw.get("keys") or raw.get("key") or raw.get("key_list") or []
        keys = [str(k) for k in k_list] if isinstance(k_list, list) else ([str(k_list)] if k_list else [])
    elif isinstance(raw, str):
        keys = [raw]

    if not keys:
        top = data.get("key") or data.get("keys")
        if isinstance(top, list):
            keys = [str(k) for k in top]
        elif isinstance(top, str):
            keys = [top]
    return keys

# ==========================================
# 3. Events & Component Interaction
# ==========================================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    try:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.clear_commands(guild=guild)
        await bot.tree.sync(guild=guild)
        
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"Successfully cleared old commands and synced {len(synced)} new commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.user.id not in ALLOWED_USER_IDS:
            await interaction.response.send_message(DENIED_MESSAGE, ephemeral=True)
            return

        custom_id = interaction.data.get("custom_id", "")
        if ":" in custom_id:
            action, key = custom_id.split(":", 1)
            await interaction.response.defer(ephemeral=True)
            try:
                payload = {
                    "api_key": API_KEY,
                    "action": action,
                    "key": key,
                    "app_id": APP_ID
                }
                resp = requests.post(API_URL, data=payload, headers=HEADERS, timeout=10)
                try:
                    res_data = resp.json()
                except Exception:
                    await interaction.followup.send(f"❌ Invalid response (HTTP {resp.status_code})", ephemeral=True)
                    return

                if res_data.get("success"):
                    await interaction.followup.send(f"✓ Action **{action}** completed for key: `{key}`", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ Failed: {res_data.get('message', 'Unknown error')}", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

# ==========================================
# 4. Commands
# ==========================================

# ── Command 1: /genkey ──
@bot.tree.command(name="genkey", description="Generate standard package license keys")
@discord.app_commands.choices(package=[
    discord.app_commands.Choice(name="BASIC PANEL", value="e52c1515c53453b85d0d4e87"),
    discord.app_commands.Choice(name="AIMSILENT EXE", value="affc8da8fd5ace99981ab877"),
    discord.app_commands.Choice(name="UID BYPASS", value="cb921031dc43197e8ccb6828"),
    discord.app_commands.Choice(name="EXTERNAL PANEL", value="3d1c6c948b4715fbd2fada2d"),
    discord.app_commands.Choice(name="PVT AIMKILL", value="d4f0ce93349f236711344cb5"),
    discord.app_commands.Choice(name="VAULT PANEL", value="154d1edaddd7203fbfd847f4"),
    discord.app_commands.Choice(name="LIB BYPASS", value="db3b90e8134ec738b94a9b05"),
    discord.app_commands.Choice(name="FPS BOOSTER", value="2411bc9db9f9a66c6e876ad2")
])
@discord.app_commands.describe(
    package="Select the target package",
    days="Duration in days (0 = lifetime)",
    count="Number of keys (max 100)"
)
async def genkey(interaction: discord.Interaction, package: str, days: int = 30, count: int = 1):
    if interaction.user.id not in ALLOWED_USER_IDS:
        await interaction.response.send_message(DENIED_MESSAGE, ephemeral=True)
        return

    await interaction.response.defer(ephemeral=False)

    payload = {
        "api_key": API_KEY,
        "action": "generate_key",
        "app_id": APP_ID,
        "package_id": package,
        "days": days,
        "count": count
    }

    try:
        resp = requests.post(API_URL, data=payload, headers=HEADERS, timeout=10)
        try:
            data = resp.json()
        except Exception:
            raw_text = resp.text[:200] if resp.text else "Empty Response"
            await interaction.followup.send(f"❌ API Error (Status {resp.status_code}): `{raw_text}`", ephemeral=True)
            return

        if data.get("success"):
            keys = parse_keys(data)
            if not keys:
                await interaction.followup.send(f"⚠️ Response format error: `{str(data)}`", ephemeral=True)
                return

            dur = "Lifetime" if days == 0 else f"{days} Days"
            pkg_name = PACKAGE_NAMES.get(package, "Unknown Package")

            embed = discord.Embed(title="🔑 Package License Key Generated", color=0x22c55e)
            embed.add_field(name="Package Name", value=f"**{pkg_name}**", inline=True)
            embed.add_field(name="Duration", value=dur, inline=True)
            embed.add_field(name="Count", value=str(len(keys)), inline=True)
            embed.add_field(name="Keys", value="\n".join([f"`{k}`" for k in keys]), inline=False)

            view = discord.ui.View()
            if len(keys) == 1:
                view.add_item(discord.ui.Button(label="Reset HWID", custom_id=f"reset_hwid:{keys[0]}", style=discord.ButtonStyle.primary))
                view.add_item(discord.ui.Button(label="Ban", custom_id=f"ban_key:{keys[0]}", style=discord.ButtonStyle.danger))
                view.add_item(discord.ui.Button(label="Unban", custom_id=f"unban_key:{keys[0]}", style=discord.ButtonStyle.success))
                view.add_item(discord.ui.Button(label="Delete", custom_id=f"delete_key:{keys[0]}", style=discord.ButtonStyle.secondary))

            await interaction.followup.send(embed=embed, view=view if len(keys) == 1 else None)
        else:
            await interaction.followup.send(f"❌ API Error: {data.get('message', 'Failed to generate key')}", ephemeral=True)

    except requests.exceptions.Timeout:
        await interaction.followup.send("⚠️ Timeout Error: Panel ne reply nahi diya.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

# ── Command 2: /resethwid ──
@bot.tree.command(name="resethwid", description="Reset HWID binding")
async def resethwid(interaction: discord.Interaction, key: str):
    if interaction.user.id not in ALLOWED_USER_IDS:
        await interaction.response.send_message(DENIED_MESSAGE, ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    payload = {"api_key": API_KEY, "action": "reset_hwid", "key": key.strip(), "app_id": APP_ID}
    try:
        resp = requests.post(API_URL, data=payload, headers=HEADERS, timeout=10)
        data = resp.json()
        if data.get("success"):
            await interaction.followup.send(f"🔄 HWID Reset Success: `{key.strip()}`", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Failed: {data.get('message')}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

# ── Command 3: /bankey ──
@bot.tree.command(name="bankey", description="Ban license key")
async def bankey(interaction: discord.Interaction, key: str):
    if interaction.user.id not in ALLOWED_USER_IDS:
        await interaction.response.send_message(DENIED_MESSAGE, ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    payload = {"api_key": API_KEY, "action": "ban_key", "key": key.strip(), "app_id": APP_ID}
    try:
        resp = requests.post(API_URL, data=payload, headers=HEADERS, timeout=10)
        data = resp.json()
        if data.get("success"):
            await interaction.followup.send(f"🚫 Key Banned: `{key.strip()}`", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Failed: {data.get('message')}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

# ── Command 4: /unbankey ──
@bot.tree.command(name="unbankey", description="Unban license key")
async def unbankey(interaction: discord.Interaction, key: str):
    if interaction.user.id not in ALLOWED_USER_IDS:
        await interaction.response.send_message(DENIED_MESSAGE, ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    payload = {"api_key": API_KEY, "action": "unban_key", "key": key.strip(), "app_id": APP_ID}
    try:
        resp = requests.post(API_URL, data=payload, headers=HEADERS, timeout=10)
        data = resp.json()
        if data.get("success"):
            await interaction.followup.send(f"✅ Key Unbanned: `{key.strip()}`", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Failed: {data.get('message')}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

# ── Command 5: /delkey ──
@bot.tree.command(name="delkey", description="Delete license key permanently")
async def delkey(interaction: discord.Interaction, key: str):
    if interaction.user.id not in ALLOWED_USER_IDS:
        await interaction.response.send_message(DENIED_MESSAGE, ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    payload = {"api_key": API_KEY, "action": "delete_key", "key": key.strip(), "app_id": APP_ID}
    try:
        resp = requests.post(API_URL, data=payload, headers=HEADERS, timeout=10)
        data = resp.json()
        if data.get("success"):
            await interaction.followup.send(f"🗑️ Key Deleted: `{key.strip()}`", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Failed: {data.get('message')}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

# ==========================================
# 5. Launch
# ==========================================
keep_alive()
bot.run(TOKEN)
