import os
import discord
import requests
import asyncio
from datetime import datetime, timedelta, timezone
from discord.ext import commands
from discord.ui import Button, View

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


WOM_GROUP_ID = 9180
WOM_API_KEY = "p9yxtw1k3gd1pa8qu8fuftcb"
WOM_VERIFICATION_CODE = "871-029-369"

METRIC_MAPPING = {
    # Skills
    "Cooking": "cooking",
    "Woodcutting": "woodcutting",
    "Fletching": "fletching",
    "Fishing": "fishing",
    "Firemaking": "firemaking",
    "Crafting": "crafting",
    "Smithing": "smithing",
    "Mining": "mining",
    "Herblore": "herblore",
    "Agility": "agility",
    "Thieving": "thieving",
    "Slayer": "slayer",
    "Farming": "farming",
    "Runecrafting": "runecrafting",
    "Hunter": "hunter",
    "Construction": "construction",
    # Bosses
    "Araxxor": "araxxor",
    "Callisto": "callisto",
    "Chambers Of Xeric": "chambers_of_xeric",
    "Commander Zilyana": "commander_zilyana",
    "Corporeal Beast": "corporeal_beast",
    "Dagannoth Rex": "dagannoth_rex",
    "Duke Sucellus": "duke_sucellus",
    "General Graardor": "general_graardor",
    "Kree'Arra": "kreearra",
    "K'ril Tsutsaroth": "kril_tsutsaroth",
    "Nex": "nex",
    "Nightmare": "nightmare",
    "Phosani": "pnm",
    "Phantom Muspah": "phantom_muspah",
    "The Gauntlet": "the_gauntlet",
    "The Leviathan": "the_leviathan",
    "The Whisperer": "the_whisperer",
    "Theatre Of Blood": "theatre_of_blood",
    "Tombs Of Amascut": "tombs_of_amascut",
    "Vardorvis": "vardorvis",
    "Venenatis": "venenatis",
    "Vet'ion": "vetion",
    "Vorkath": "vorkath",
    "Yama": "yama",
    "Zulrah": "zulrah",
}

@bot.event
async def on_ready():
    print(f"✅ Event Wizard Bot running as {bot.user}")
    await bot.tree.sync()


# Slash command to open the panel
@bot.tree.command(name="event_panel", description="Open the event creation panel")
async def event_panel(interaction: discord.Interaction):
    custom_emoji_skill = discord.utils.get(interaction.guild.emojis, name="skill")

    button_botw = Button(label="Boss of the Week (BOTW)", style=discord.ButtonStyle.primary, emoji="⚔️")
    button_sotw = Button(label="Skill of the Week (SOTW)", style=discord.ButtonStyle.primary, emoji=custom_emoji_skill)

    view = View(timeout=None)
    view.add_item(button_botw)
    view.add_item(button_sotw)

    # BOTW submenu
    async def botw_panel(inner: discord.Interaction):
        view_botw = View(timeout=None)
        for name in [k for k in METRIC_MAPPING if k not in METRIC_MAPPING.keys() or k not in METRIC_MAPPING.values()]:
            continue  # skip mis-matched mapping
        for boss in [b for b in METRIC_MAPPING if b not in METRIC_MAPPING if b not in METRIC_MAPPING.values()]:
            continue
        bosses = [
            "General Graardor", "K'ril Tsutsaroth", "Commander Zilyana", "Kree'Arra", "Nex",
            "Callisto", "Vet'ion", "Venenatis", "Chambers Of Xeric", "Tombs Of Amascut", "Theatre Of Blood",
            "Araxxor", "Vardorvis", "Duke Sucellus", "The Leviathan", "The Whisperer", "Dagannoth Rex",
            "Corporeal Beast", "Vorkath", "Zulrah", "The Gauntlet", "Phantom Muspah", "Nightmare", "Phosani", "Yama"
        ]
        for boss in bosses:
            emoji = discord.utils.get(interaction.guild.emojis, name=boss.lower().replace(" ", "").replace("'", ""))
            btn = Button(label=boss, style=discord.ButtonStyle.secondary, emoji=emoji)
            btn.callback = lambda i, b=boss: asyncio.create_task(create_event_and_wom(i, b, "boss"))
            view_botw.add_item(btn)
        await inner.response.edit_message(content="Select the boss for this week's event:", view=view_botw)

    # SOTW submenu
    async def sotw_panel(inner: discord.Interaction):
        view_sotw = View(timeout=None)
        skills = [
            "Farming", "Fishing", "Hunter", "Mining", "Woodcutting", "Cooking", "Crafting", "Fletching",
            "Herblore", "Runecrafting", "Smithing", "Agility", "Construction", "Firemaking", "Slayer", "Thieving"
        ]
        for skill in skills:
            emoji = discord.utils.get(interaction.guild.emojis, name=skill.lower())
            btn = Button(label=skill, style=discord.ButtonStyle.secondary, emoji=emoji)
            btn.callback = lambda i, s=skill: asyncio.create_task(create_event_and_wom(i, s, "skill"))
            view_sotw.add_item(btn)
        await inner.response.edit_message(content="Select the skill for this week's event:", view=view_sotw)

    button_botw.callback = botw_panel
    button_sotw.callback = sotw_panel

    await interaction.response.send_message("Click a button to create an event:", view=view, ephemeral=True)


async def create_event_and_wom(interaction: discord.Interaction, name: str, kind: str):
    desc = f"{'Defeat' if kind=='boss' else 'Master'} {name} in this week's challenge!"
    metric = METRIC_MAPPING.get(name, name.lower().replace(" ", "_"))

    await create_event(interaction, name, desc)
    await create_wise_old_man_competition(metric, desc)


async def create_event(interaction: discord.Interaction, event_name: str, description: str):
    guild = interaction.guild
    start_time = datetime.now(timezone.utc) + timedelta(seconds=15)
    end_time = start_time + timedelta(days=7)

    await guild.create_scheduled_event(
        name=event_name,
        description=description,
        start_time=start_time,
        end_time=end_time,
        entity_type=discord.EntityType.external,
        location="Gielinor",
        privacy_level=discord.PrivacyLevel.guild_only,
    )
    await interaction.response.send_message(f"✅ Event **{event_name}** created successfully!", ephemeral=True)


async def create_wise_old_man_competition(metric: str, description: str):
    start_time = (datetime.now(timezone.utc) + timedelta(seconds=15)).isoformat()
    end_time = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()

    payload = {
        "title": description,
        "metric": metric,
        "startsAt": start_time,
        "endsAt": end_time,
        "groupId": WOM_GROUP_ID,
        "groupVerificationCode": WOM_VERIFICATION_CODE,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {WOM_API_KEY}",
    }
    resp = requests.post("https://api.wiseoldman.net/v2/competitions", json=payload, headers=headers)
    if resp.status_code == 201:
        print(f"✅ WOM competition '{description}' created successfully.")
    else:
        print(f"❌ Failed to create WOM competition: {resp.status_code} - {resp.text}")


bot.run(os.getenv("DISCORD_BOT_TOKEN"))

