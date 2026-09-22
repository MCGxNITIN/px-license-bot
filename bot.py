import os
import discord
from discord.ext import commands
import requests

# ==========================================
# TerminalX999 - Secure Owner-Only License Bot
# ==========================================

# Token seedha hosting panel ke Environment Variables se load hoga
TOKEN    = os.getenv("DISCORD_TOKEN")

GUILD_ID = 1525181999147388958   # Aapka Server ID
OWNER_ID = 1525179499602509977   # Aapka User ID

API_URL  = "https://auth.terminalx999.online/api_admin.php"
API_KEY  = "TX999_1fc0134c4c418cf9f0817f355ac10cf7e5f73cf899a83bbf4731e4eec3929870"
APP_ID   = "9f087d585fbd666572fc24b7"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

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

def call_license_api(action: str, **kwargs):
    payload = {"api_key": API_KEY, "action": action, **kwargs}
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}

@bot.tree.interaction_check
async def is_owner_and_guild(interaction: discord.Interaction) -> bool:
    if interaction.guild_id != GUILD_ID:
        await interaction.response.send_message("❌ Unauthorized Server.", ephemeral=True)
        return False
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("⛔ Access Denied: Sirf Bot Owner use kar sakta hai.", ephemeral=True)
        return False
    return True

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    try:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.guild_id != GUILD_ID or interaction.user.id != OWNER_ID:
            await interaction.response.send_message("⛔ Access Denied.", ephemeral=True)
            return

        custom_id = interaction.data.get("custom_id", "")
        if ":" in custom_id:
            action, key = custom_id.split(":", 1)
            await interaction.response.defer(ephemeral=True)
            data = call_license_api(action=action, key=key)
            if data.get("success"):
                await interaction.followup.send(f"✓ Action **{action}** successfully completed for key: `{key}`", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Failed: {data.get('message')}", ephemeral=True)

@bot.tree.command(name="genkey", description="Generate a license key remotely.")
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
@discord.app_commands.describe(package="Select package", days="Duration (0 = lifetime)", count="Number of keys (max 100)")
async def genkey(interaction: discord.Interaction, package: str, days: int = 30, count: int = 1):
    await interaction.response.defer(ephemeral=False)
    data = call_license_api("generate_key", app_id=APP_ID, package_id=package, days=days, count=count)
    if data.get("success"):
        keys = data.get("data", {}).get("keys", [])
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
        await interaction.followup.send(f"❌ {data.get('message')}", ephemeral=True)

@bot.tree.command(name="resethwid", description="Reset device HWID binding for a license key.")
async def resethwid(interaction: discord.Interaction, key: str):
    await interaction.response.defer(ephemeral=True)
    data = call_license_api("reset_hwid", key=key.strip())
    if data.get("success"):
        await interaction.followup.send(f"🔄 HWID Reset Success for `{key.strip()}`", ephemeral=True)
    else:
        await interaction.followup.send(f"❌ Failed: {data.get('message')}", ephemeral=True)

@bot.tree.command(name="bankey", description="Ban a license key.")
async def bankey(interaction: discord.Interaction, key: str):
    await interaction.response.defer(ephemeral=True)
    data = call_license_api("ban_key", key=key.strip())
    if data.get("success"):
        await interaction.followup.send(f"🚫 Key Banned: `{key.strip()}`", ephemeral=True)
    else:
        await interaction.followup.send(f"❌ Failed: {data.get('message')}", ephemeral=True)

@bot.tree.command(name="unbankey", description="Unban a previously banned license key.")
async def unbankey(interaction: discord.Interaction, key: str):
    await interaction.response.defer(ephemeral=True)
    data = call_license_api("unban_key", key=key.strip())
    if data.get("success"):
        await interaction.followup.send(f"✅ Key Unbanned: `{key.strip()}`", ephemeral=True)
    else:
        await interaction.followup.send(f"❌ Failed: {data.get('message')}", ephemeral=True)

@bot.tree.command(name="delkey", description="Permanently delete a license key from the database.")
async def delkey(interaction: discord.Interaction, key: str):
    await interaction.response.defer(ephemeral=True)
    data = call_license_api("delete_key", key=key.strip())
    if data.get("success"):
        await interaction.followup.send(f"🗑️ Key Deleted: `{key.strip()}`", ephemeral=True)
    else:
        await interaction.followup.send(f"❌ Failed: {data.get('message')}", ephemeral=True)

bot.run(TOKEN)
