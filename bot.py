import os
import requests
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
from threading import Thread

# ── Render Web Service Port Binding Fix (24/7 Hosting) ──
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ==========================================
# TerminalX999 - Standard License Key Discord Bot
# ==========================================
TOKEN    = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

API_URL  = "https://auth.terminalx999.online/api_admin.php"
# Updated API Key automatically assigned
API_KEY  = os.getenv("API_KEY", "TX999_1fc0134c4c418cf9f0817f355ac10cf7e5f73cf899a83bbf4731e4eec3929870")
APP_ID   = os.getenv("APP_ID", "9f087d585fbd666572fc24b7")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    try:
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"Synced {len(synced)} slash commands to Guild ID: {GUILD_ID}")
        else:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} slash commands globally.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# ── Button Click Handler ──
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get("custom_id", "")
        if ":" in custom_id:
            action, key = custom_id.split(":", 1)
            await interaction.response.defer(ephemeral=True)
            try:
                resp = requests.post(API_URL, json={"api_key": API_KEY, "action": action, "key": key}, timeout=10)
                res_data = resp.json()
                if res_data.get("success"):
                    await interaction.followup.send(f"✓ Action **{action}** completed for key: `{key}`", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ Failed: {res_data.get('message')}", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

# ── GENERATE KEY COMMAND ──
@bot.tree.command(name="genkey", description="Generate a license key remotely.")
@app_commands.choices(package=[
    app_commands.Choice(name="BASIC PANEL (v13)", value="e52c1515c53453b85d0d4e87"),
    app_commands.Choice(name="AIMSILENT EXE (v13)", value="affc8da8fd5ace99981ab877"),
    app_commands.Choice(name="UID BYPASS (v13)", value="cb921031dc43197e8ccb6828"),
    app_commands.Choice(name="EXTERNAL PANEL (v13)", value="3d1c6c948b4715fbd2fada2d"),
    app_commands.Choice(name="PVT AIMKILL (v13)", value="d4f0ce93349f236711344cb5"),
    app_commands.Choice(name="VAULT PANEL (v13)", value="154d1edaddd7203fbfd847f4"),
    app_commands.Choice(name="LIB BYPASS (v13)", value="db3b90e8134ec738b94a9b05"),
    app_commands.Choice(name="FPS BOOSTER (v13)", value="FPS_BOOSTER_PACKAGE_ID_HERE") # Panel se FPS Booster ID daal lein
])
@app_commands.describe(
    package="Select the target package",
    days="Number of validity days (0 = lifetime)",
    count="Number of keys to generate (max 100)",
    note="Add a custom note or description"
)
async def genkey(interaction: discord.Interaction, package: app_commands.Choice[str], days: int = 30, count: int = 1, note: str = "No note"):
    await interaction.response.defer(ephemeral=False)
    payload = {
        "api_key": API_KEY, 
        "action": "generate_key", 
        "app_id": APP_ID, 
        "package_id": package.value, 
        "days": days, 
        "count": count,
        "note": note
    }
    try:
        resp = requests.post(API_URL, json=payload, timeout=10)
        data = resp.json()
        if data.get("success"):
            keys = data.get("data", {}).get("keys", [])
            dur = "Lifetime" if days == 0 else f"{days} Days"
            
            embed = discord.Embed(
                title="🔑 Keys Generated", 
                description=f"**Package:** {package.name}\n**Count:** {len(keys)}\n**Duration:** {dur}\n**Note:** {note}", 
                color=0x22c55e
            )
            embed.add_field(name="Keys", value="\n".join([f"`{k}`" for k in keys]), inline=False)
            
            # Fix: View parameter bug fixed
            if len(keys) == 1:
                view = discord.ui.View()
                view.add_item(discord.ui.Button(label="Reset HWID", custom_id=f"reset_hwid:{keys[0]}", style=discord.ButtonStyle.primary))
                view.add_item(discord.ui.Button(label="Ban", custom_id=f"ban_key:{keys[0]}", style=discord.ButtonStyle.danger))
                view.add_item(discord.ui.Button(label="Unban", custom_id=f"unban_key:{keys[0]}", style=discord.ButtonStyle.success))
                view.add_item(discord.ui.Button(label="Pause", custom_id=f"pause_key:{keys[0]}", style=discord.ButtonStyle.secondary))
                view.add_item(discord.ui.Button(label="Unpause", custom_id=f"unpause_key:{keys[0]}", style=discord.ButtonStyle.success))
                await interaction.followup.send(embed=embed, view=view)
            else:
                await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"❌ {data.get('message')}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

# Helper Function
async def execute_key_action(interaction: discord.Interaction, action: str, key: str):
    await interaction.response.defer(ephemeral=True)
    try:
        resp = requests.post(API_URL, json={"api_key": API_KEY, "action": action, "key": key}, timeout=10)
        data = resp.json()
        if data.get("success"):
            await interaction.followup.send(f"✅ Success: Key `{key}` action **{action}** completed.", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Failed: {data.get('message')}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

# ── COMMANDS ──
@bot.tree.command(name="resetkey", description="Reset HWID for a specific key.")
async def resetkey(interaction: discord.Interaction, key: str):
    await execute_key_action(interaction, "reset_hwid", key)

@bot.tree.command(name="bankey", description="Ban a specific key.")
async def bankey(interaction: discord.Interaction, key: str):
    await execute_key_action(interaction, "ban_key", key)

@bot.tree.command(name="unbankey", description="Unban a specific key.")
async def unbankey(interaction: discord.Interaction, key: str):
    await execute_key_action(interaction, "unban_key", key)

@bot.tree.command(name="pausekey", description="Pause a specific key.")
async def pausekey(interaction: discord.Interaction, key: str):
    await execute_key_action(interaction, "pause_key", key)

@bot.tree.command(name="unpausekey", description="Unpause a specific key.")
async def unpausekey(interaction: discord.Interaction, key: str):
    await execute_key_action(interaction, "unpause_key", key)

keep_alive()

if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ ERROR: DISCORD_TOKEN Environment Variable missing!")
