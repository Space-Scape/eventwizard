import os
import discord
import requests
import asyncio
from discord.ext import commands
from discord.ui import Button, View
from datetime import datetime, timedelta, timezone

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)  # Disable the default help command

# Fetch environment variables
WOM_API_KEY = os.getenv('WOM_API_KEY')
WOM_GROUP_ID = os.getenv('WOM_GROUP_ID')
WOM_VERIFICATION_CODE = os.getenv('WOM_VERIFICATION_CODE')

# Ensure these are available
if not WOM_API_KEY or not WOM_GROUP_ID or not WOM_VERIFICATION_CODE:
    raise ValueError("Wise Old Man API key, group ID, or verification code is missing.")

# Mapping of button labels to Wise Old Man metrics
METRIC_MAPPING = {
    # Skill Metrics
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

    # Boss Metrics
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
    "Zulrah": "zulrah"
}

@bot.event
async def on_ready():
    bot.loop.create_task(update_wom_group())
    print(f'eventwizard.py script is currently running')

# Update Wise Old Man group every 3 hours
async def update_wom_group():
    while True:
        await asyncio.sleep(10800)  # Wait for 3 hours
        url = f"https://api.wiseoldman.net/v2/groups/{WOM_GROUP_ID}/update-all"
        headers = {"Authorization": f"Bearer {WOM_API_KEY}"}
        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            print("Wise Old Man group updated successfully.")
        else:
            print(f"Failed to update WOM group: {response.status_code} - {response.text}")

# Command to show the event panel
@bot.command()
async def event_panel(ctx):
    custom_emoji_skill = discord.utils.get(ctx.guild.emojis, name="skill")
    
    # Define buttons for BOTW and SOTW
    button_botw = Button(label="Boss of the Week (BOTW)", style=discord.ButtonStyle.primary, emoji="⚔️")  # Crossed swords emoji
    button_sotw = Button(label="Skill of the Week (SOTW)", style=discord.ButtonStyle.primary, emoji=custom_emoji_skill)  # Custom skill emoji

    # Define the view and add the initial buttons
    view = View(timeout=None)
    view.add_item(button_botw)
    view.add_item(button_sotw)

    # Callback to show the BOTW event creation panel
    async def botw_panel(interaction):
        # Define buttons for each boss with updated names
        button_graardor = Button(label="General Graardor", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="graardor"))
        button_zammy = Button(label="K'ril Tsutsaroth", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="zammy"))
        button_sara = Button(label="Commander Zilyana", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="sara"))
        button_arma = Button(label="Kree'Arra", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="arma"))
        button_nex = Button(label="Nex", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="nex"))
        button_callisto = Button(label="Callisto", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="callisto"))
        button_vetion = Button(label="Vet'ion", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="vetion"))
        button_venenatis = Button(label="Venenatis", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="venenatis"))
        button_cox = Button(label="Chambers Of Xeric", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="cox"))
        button_toa = Button(label="Tombs Of Amascut", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="toa"))
        button_tob = Button(label="Theatre Of Blood", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="tob"))

        # New bosses with updated names
        button_vardorvis = Button(label="Vardorvis", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="vardorvis"))
        button_duke = Button(label="Duke Sucellus", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="duke"))
        button_leviathan = Button(label="The Leviathan", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="leviathan"))
        button_whisperer = Button(label="The Whisperer", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="whisperer"))
        button_dks = Button(label="Dagannoth Rex", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="dks"))
        button_corp = Button(label="Corporeal Beast", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="corp"))
        button_vorkath = Button(label="Vorkath", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="vorkath"))
        button_zulrah = Button(label="Zulrah", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="zulrah"))
        button_gauntlet = Button(label="The Gauntlet", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="gauntlet"))
        button_muspah = Button(label="Phantom Muspah", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="muspah"))
        button_nightmare = Button(label="Nightmare", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="nightmare"))

        # Define the view and add the boss buttons
        view_botw = View(timeout=None)
        view_botw.add_item(button_graardor)
        view_botw.add_item(button_zammy)
        view_botw.add_item(button_sara)
        view_botw.add_item(button_arma)
        view_botw.add_item(button_nex)
        view_botw.add_item(button_callisto)
        view_botw.add_item(button_vetion)
        view_botw.add_item(button_venenatis)
        view_botw.add_item(button_cox)
        view_botw.add_item(button_toa)
        view_botw.add_item(button_tob)

        # Add new boss buttons
        view_botw.add_item(button_vardorvis)
        view_botw.add_item(button_duke)
        view_botw.add_item(button_leviathan)
        view_botw.add_item(button_whisperer)
        view_botw.add_item(button_dks)
        view_botw.add_item(button_corp)
        view_botw.add_item(button_vorkath)
        view_botw.add_item(button_zulrah)
        view_botw.add_item(button_gauntlet)
        view_botw.add_item(button_muspah)
        view_botw.add_item(button_nightmare)

        # Callback for each boss button
        async def create_botw_event(interaction, button):
            event_name = button.label
            description = f"Defeat {button.label} in this week's challenge!"
            metric = METRIC_MAPPING.get(event_name, event_name.lower().replace(" ", "_"))
            await create_event(interaction, event_name, description)
            await create_wise_old_man_competition(metric, description)

        button_graardor.callback = lambda interaction: asyncio.create_task(create_botw_event(interaction, button_graardor))
        button_zammy.callback = lambda interaction: asyncio.create_task(create_botw_event(interaction, button_zammy))
        button_sara.callback = lambda interaction: asyncio.create_task(create_botw_event(interaction, button_sara))
        button_arma.callback = lambda interaction: asyncio.create_task(create_botw_event(interaction, button_arma))
        button_nex.callback = lambda interaction: asyncio.create_task(create_botw_event(interaction, button_nex))
        button_callisto.callback = lambda interaction: asyncio.create_task(create_botw_event(interaction, button_callisto))
        button_vetion.callback = lambda interaction: asyncio.create_task(create_botw_event(interaction, button_vetion))
        button_venenatis.callback = lambda interaction: asyncio.create_task(create_botw_event(interaction, button_venenatis))
        button_cox.callback = lambda interaction: asyncio.create_task(create_botw_event(interaction, button_cox))
        button_toa.callback = lambda interaction: asyncio.create_task(create_botw_event(interaction, button_toa))
        button_tob.callback = lambda interaction: asyncio.create_task(create_botw_event(interaction, button_tob))

        # Callback for new boss buttons
        button_vardorvis.callback = lambda interaction: asyncio.create_task(create_botw_event(interaction, button_vardorvis))
        button_duke.callback = lambda interaction: asyncio.create_task(create_botw_event(interaction, button_duke))
        button_leviathan.callback = lambda interaction: asyncio.create_task(create_botw_event(interaction, button_leviathan))
        button_whisperer.callback = lambda interaction: asyncio.create_task(create_botw_event(interaction, button_whisperer))
        button_dks.callback = lambda interaction: asyncio.create_task(create_botw_event(interaction, button_dks))
        button_corp.callback = lambda interaction: asyncio.create_task(create_botw_event(interaction, button_corp))
        button_vorkath.callback = lambda interaction: asyncio.create_task(create_botw_event(interaction, button_vorkath))
        button_zulrah.callback = lambda interaction: asyncio.create_task(create_botw_event(interaction, button_zulrah))
        button_gauntlet.callback = lambda interaction: asyncio.create_task(create_botw_event(interaction, button_gauntlet))
        button_muspah.callback = lambda interaction: asyncio.create_task(create_botw_event(interaction, button_muspah))
        button_nightmare.callback = lambda interaction: asyncio.create_task(create_botw_event(interaction, button_nightmare))

        await interaction.response.edit_message(content="Select the boss for this week's event:", view=view_botw)

    # Callback to show the SOTW event creation panel
    async def sotw_panel(interaction):
        # Define buttons for each skill category

        # Gathering Skills
        button_farming = Button(label="Farming", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="farming"))
        button_fishing = Button(label="Fishing", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="fishing"))
        button_hunter = Button(label="Hunter", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="hunter"))
        button_mining = Button(label="Mining", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="mining"))
        button_woodcutting = Button(label="Woodcutting", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="woodcutting"))

        # Production Skills
        button_cooking = Button(label="Cooking", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="cooking"))
        button_crafting = Button(label="Crafting", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="crafting"))
        button_fletching = Button(label="Fletching", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="fletching"))
        button_herblore = Button(label="Herblore", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="herblore"))
        button_runecraft = Button(label="Runecrafting", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="runecrafting"))
        button_smithing = Button(label="Smithing", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="smithing"))

        # Utility Skills
        button_agility = Button(label="Agility", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="agility"))
        button_construction = Button(label="Construction", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="construction"))
        button_firemaking = Button(label="Firemaking", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="firemaking"))
        button_slayer = Button(label="Slayer", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="slayer"))
        button_thieving = Button(label="Thieving", style=discord.ButtonStyle.secondary, emoji=discord.utils.get(interaction.guild.emojis, name="thieving"))

        # Define the view and add the skill buttons
        view_sotw = View(timeout=None)
        view_sotw.add_item(button_farming)
        view_sotw.add_item(button_fishing)
        view_sotw.add_item(button_hunter)
        view_sotw.add_item(button_mining)
        view_sotw.add_item(button_woodcutting)
        view_sotw.add_item(button_cooking)
        view_sotw.add_item(button_crafting)
        view_sotw.add_item(button_fletching)
        view_sotw.add_item(button_herblore)
        view_sotw.add_item(button_runecraft)
        view_sotw.add_item(button_smithing)
        view_sotw.add_item(button_agility)
        view_sotw.add_item(button_construction)
        view_sotw.add_item(button_firemaking)
        view_sotw.add_item(button_slayer)
        view_sotw.add_item(button_thieving)

        # Callback for each skill button
        async def create_sotw_event(interaction, button):
            event_name = button.label
            description = f"Master {button.label} in this week's skill challenge!"
            metric = METRIC_MAPPING.get(event_name, event_name.lower().replace(" ", "_"))
            await create_event(interaction, event_name, description)
            await create_wise_old_man_competition(metric, description)

        button_farming.callback = lambda interaction: asyncio.create_task(create_sotw_event(interaction, button_farming))
        button_fishing.callback = lambda interaction: asyncio.create_task(create_sotw_event(interaction, button_fishing))
        button_hunter.callback = lambda interaction: asyncio.create_task(create_sotw_event(interaction, button_hunter))
        button_mining.callback = lambda interaction: asyncio.create_task(create_sotw_event(interaction, button_mining))
        button_woodcutting.callback = lambda interaction: asyncio.create_task(create_sotw_event(interaction, button_woodcutting))
        button_cooking.callback = lambda interaction: asyncio.create_task(create_sotw_event(interaction, button_cooking))
        button_crafting.callback = lambda interaction: asyncio.create_task(create_sotw_event(interaction, button_crafting))
        button_fletching.callback = lambda interaction: asyncio.create_task(create_sotw_event(interaction, button_fletching))
        button_herblore.callback = lambda interaction: asyncio.create_task(create_sotw_event(interaction, button_herblore))
        button_runecraft.callback = lambda interaction: asyncio.create_task(create_sotw_event(interaction, button_runecraft))
        button_smithing.callback = lambda interaction: asyncio.create_task(create_sotw_event(interaction, button_smithing))
        button_agility.callback = lambda interaction: asyncio.create_task(create_sotw_event(interaction, button_agility))
        button_construction.callback = lambda interaction: asyncio.create_task(create_sotw_event(interaction, button_construction))
        button_firemaking.callback = lambda interaction: asyncio.create_task(create_sotw_event(interaction, button_firemaking))
        button_slayer.callback = lambda interaction: asyncio.create_task(create_sotw_event(interaction, button_slayer))
        button_thieving.callback = lambda interaction: asyncio.create_task(create_sotw_event(interaction, button_thieving))

        await interaction.response.edit_message(content="Select the skill for this week's event:", view=view_sotw)

    # Assign callbacks to the initial buttons
    button_botw.callback = botw_panel
    button_sotw.callback = sotw_panel

    # Send the initial panel message
    await ctx.send("Click a button to create an event:", view=view)

# Function to create the event on Discord
async def create_event(interaction, event_name, description):
    guild = interaction.guild
    start_time = datetime.now(timezone.utc) + timedelta(seconds=15)  # Add 15 seconds to ensure the start time is in the future
    end_time = start_time + timedelta(days=7)  # Set the event duration to 7 days

    # Create the scheduled event as "Somewhere Else" with the location "Gielinor"
    await guild.create_scheduled_event(
        name=event_name,
        description=description,
        start_time=start_time,
        end_time=end_time,
        entity_type=discord.EntityType.external,
        location="Gielinor",
        privacy_level=discord.PrivacyLevel.guild_only  # Set privacy level to guild-only
    )
    await interaction.response.send_message(f"Event '{event_name}' created successfully!", ephemeral=True)

# Function to create a Wise Old Man competition
async def create_wise_old_man_competition(metric, description):
    start_time = (datetime.now(timezone.utc) + timedelta(seconds=15)).isoformat()
    end_time = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()

    # Prepare the payload
    payload = {
        "title": description,
        "metric": metric,  # Metric is mapped from the button name
        "startsAt": start_time,
        "endsAt": end_time,
        "groupId": WOM_GROUP_ID,
        "groupVerificationCode": WOM_VERIFICATION_CODE  # Include the verification code
    }

    # Headers with the API key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {WOM_API_KEY}"
    }

    # Make a POST request to create the competition
    response = requests.post("https://api.wiseoldman.net/v2/competitions", json=payload, headers=headers)

    if response.status_code == 201:
        print(f"WOM competition '{description}' created successfully.")
    else:
        print(f"Failed to create WOM competition: {response.status_code} - {response.text}")

# Run the bot using the token stored in Railway's environment variables
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
