import os
import discord
from discord.ext import commands
from discord import app_commands
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timezone
import asyncio
from typing import Optional
import random


# ---------------------------
# Boss-Drop Mapping
# ---------------------------

#Master List
    #"Abyssal Sire": ["Abyssal orphan", "Unsired", "Abyssal head", "Bludgeon spine", "Bludgeon claw", "Bludgeon axon", "Jar of miasma", "Abyssal dagger", "Abyssal whip"],
    #"Alchemical Hydra": ["Ikkle hydra", "Hydra's claw", "Hydra tail", "Hydra leather", "Hydra's fang", "Hydra's eye", "Hydra's heart", "Jar of chemicals"],
    #"Amoxliatl": ["Moxi"],
    #"Araxxor": ["Noxious pommel", "Noxious point", "Noxious blade", "Araxyte fang", "Araxyte head", "Aranea boots", "Jar of venom", "Coagulated venom", "Nid"],
    #"Barrows": ["Ahrim's hood", "Ahrim's robetop", "Ahrim's robeskirt", "Ahrim's staff", "Karil's coif", "Karil's leathertop", "Karil's leatherskirt", "Karil's crossbow", "Dharok's helm", "Dharok's platebody", "Dharok's platelegs", "Dharok's greataxe", "Guthan's helm", "Guthan's platebody", "Guthan's chainskirt", "Guthan's warspear", "Torag's helm", "Torag's platebody", "Torag's platelegs", "Torag's hammers", "Verac's helm", "Verac's brassard", "Verac's plateskirt", "Verac's flail"],
    #"Bryophyta": ["Bryophyta's essence"],
    #"Callisto": ["Callisto cub", "Tyrannical ring", "Dragon pickaxe", "Claws of callisto", "Voidwaker hilt"],
    #"Cerberus": ["Hellpuppy", "Eternal crystal", "Pegasian crystal", "Primordial crystal", "Jar of souls"],
    #"Chaos Fanatic": ["Odium shard 1", "Malediction shard 1"],
    #"Chambers of Xeric": ["Dexterous prayer scroll", "Arcane prayer scroll", "Twisted buckler", "Dragon hunter crossbow", "Dinh's bulwark", "Ancestral hat", "Ancestral robe top", "Ancestral robe bottom", "Dragon claws", "Elder maul", "Kodai insignia", "Twisted bow", "Olmlet", "Twisted ancestral colour kit", "Metamorphic dust"],
    #"Colosseum": ["Dizana's quiver (uncharged)", "Sunfire fanatic cuirass", "Sunfire fanatic chausses", "Sunfire fanatic helm", "Echo crystal", "Tonalztics of ralos (uncharged)"],
    #"Commander Zilyana": ["Pet zilyana", "Armadyl crossbow", "Saradomin hilt", "Saradomin sword", "Godsword shard 1", "Godsword shard 2", "Godsword shard 3", "Saradomin's light"],
    #"Corporeal Beast": ["Pet dark core", "Elysian sigil", "Spectral sigil", "Arcane sigil", "Jar of spirits", "Spirit shield", "Holy Elixir"],
    #"Crazy Archaeologist": ["Odium shard 2", "Malediction shard 2", "Fedora"],
    #"Dagannoth Kings": ["Pet dagannoth supreme", "Pet dagannoth rex", "Pet dagannoth prime", "Archers ring", "Seers ring", "Berserker ring", "Warrior ring"],
    #"Demonic Gorilla": ["Zenyte shard", "Ballista limbs", "Ballista spring", "Light frame", "Heavy frame", "Monkey tail"],
    #"Deranged Archaeologist": ["Steel ring"],
    #"Doom of Mokhaiotl": ["Dom", "Avernic treads", "Eye of ayak (uncharged)", "Mokhaiotl cloth"],
    #"Duke Sucellus": ["Baron", "Virtus mask", "Virtus robe top", "Virtus robe bottom", "Magus vestige", "Eye of the duke"],
    #"Gauntlet": ["Youngllef", "Crystal weapon seed", "Crystal armour seed", "Enhanced crystal weapon seed"],
    #"General Graardor": ["Pet general graardor", "	Bandos hilt", "Bandos chestplate", "Bandos tassets", "Bandos boots", "Godsword shard 1", "Godsword shard 2", "Godsword shard 3"],
    #"Giant Mole": ["Baby mole"],
    #"Grotesque Guardians": ["Noon/midnight", "Granite gloves", "Granite hammer", "Granite ring", "Black tourmaline core", "Jar of stone"],
    #"Hueycoatl": ["Huberte", "Dragon hunter wand", "Hueycoatl hide", "Tome of earth (empty)"],
    #"Inferno": ["Infernal cape"],
    #"Jad": ["Fire cape"],
    #"Kalphite Queen": ["Kalphite princess", "Dragon chainbody", "Dragon pickaxe", "Jar of sand", "Kq head"],
    #"Kraken": ["Pet kraken", "Kraken tentacle", "Trident of the seas (full)", "Jar of dirt"],
    #"Kree'arra": ["Pet kree'arra", "Armadyl helmet", "Armadyl chestplate", "Armadyl chainskirt", "Armadyl hilt", "Godsword shard 1", "Godsword shard 2", "Godsword shard 3"],
    #"K'ril Tsutsaroth": ["Pet K'ril Tsutsaroth", "Zamorakian spear", "Staff of the dead", "Zamorak hilt", "Steam battlestaff", "Godsword shard 1", "Godsword shard 2", "Godsword shard 3"],
    #"Moons of Peril": ["Eclipse atlatl", "Eclipse moon helm", "Eclipse moon chestplate", "Eclipse moon tassets", "Dual macuahuitl", "Blood moon helm", "Blood moon chestplate", "Blood moon tassets", "Blue moon spear", "Blue moon helm", "Blue moon chestplate", "Blue moon tassets"],
    #"King black dragon": ["Prince black dragon"],
    #"Nightmare": ["Little nightmare/Parasite", "Nightmare staff", "Inquisitor's great helm", "Inquisitor's hauberk", "Inquisitor's plateskirt", "Inquisitor's mace", "Eldritch orb", "Harmonised orb", "Volatile orb", "Jar of dreams"],
    #"Nex": ["Nexling", "Ancient hilt", "Nihil horn", "Zaryte vambraces", "Torva full helm (damaged)", "Torva platebody (damaged)", "Torva platelegs (damaged)"],
    #"Phantom Muspah": ["Muphin", "Venator shard", "Ancient icon", "Charged ice", "Frozen cache", "Ancient essence"],
    #"Royal Titans": ["Bran", "Deadeye prayer scroll", "Mystic vigour prayer scroll", "Fire element staff crown", "Ice element staff crown"],
    #"Revenants": ["Thammaron's sceptre", "Viggora's chainmace", "Craw's bow", "Ancient relic", "Ancient effigy", "Ancient medallion", "Ancient statuette", "Ancient totem"],
    #"Sarachnis": ["Sraracha", "Sarachnis cudgel", "Jar of eyes"],
    #"Scorpia": ["Scorpia's Offspring", "Malediction shard 3", "Odium shard 3"],
    #"Scurrius": ["Scurry"],
    #"Tempoross": ["Tome of water (empty)"],
    #"The Leviathan": ["Lil'viathan", "Virtus mask", "Virtus robe top", "Virtus robe bottom", "Venator vestige", "Leviathan's lure"],
    #"Thermonuclear smoke devil": ["Jar of smoke", "Pet smoke devil"],
    #"The Whisperer": ["Wisp", "Virtus mask", "Virtus robe top", "Virtus robe bottom", "Bellator vestige", "Siren's staff"],
    #"Theatre of Blood": ["Lil' zik", "Avernic defender hilt", "Ghrazi rapier", "Sanguinesti staff (uncharged)", "Justiciar faceguard", "Justiciar chestguard", "Justiciar legguards", "Scythe of vitur (uncharged)", "Holy ornament kit", "Sanguine ornament kit", "Sanguine dust"],
    #"Tombs of Amascut": ["Tumeken's Guardian", "Masori mask", "Masori body", "Masori chaps", "Lightbearer", "Osmumten's fang", "Elidinis' ward", "Tumeken's shadow (uncharged)"],
    #"Tormented Demons": ["Tormented synapse", "Burning claw"],
    #"Vardorvis": ["Butch", "Virtus mask", "Virtus robe top", "Virtus robe bottom", "Ultor vestige", "Executioner's axe head"],
    #"Venenatis": ["Venenatis spiderling", "Fangs of venenatis", "Dragon pickaxe", "Voidwaker gem", "Treasonous ring"],
    #"Vet'ion": ["Vet'ion jr.", "Skull of vet'ion", "Dragon pickaxe", "Voidwaker blade", "Ring of the gods", "Skeleton champion scroll"],
    #"Vorkath": ["Vorki", "Draconic visage", "Skeletal visage", "Jar of decay", "Dragonbone necklace"],
    #"Wintertodt": ["Tome of fire (empty)"],
    #"Yama": ["Yami", "Soulflame horn", "Oathplate helm", "Oathplate chest", "Oathplate legs", "Dossier"],
    #"Zalcano": ["Smolcano", "Zalcano shard", "Crystal tool seed"],
    #"Zulrah": ["Pet snakeling", "Tanzanite mutagen", "Magma mutagen", "Jar of swamp", "Tanzanite fang", "Magic fang", "Serpentine visage", "Uncut onyx"],

BOSS_DROPS = {
    "Abyssal Sire": ["Abyssal orphan", "Jar of miasma"],
    "Alchemical Hydra": ["Ikkle hydra", "Jar of chemicals"],
    "Araxxor": ["Araxyte fang", "Nid"],
    "Barrows": ["Ahrim's hood", "Ahrim's robetop", "Ahrim's robeskirt", "Ahrim's staff", "Karil's coif", "Karil's leathertop", "Karil's leatherskirt", "Karil's crossbow", "Dharok's helm", "Dharok's platebody", "Dharok's platelegs", "Dharok's greataxe", "Guthan's helm", "Guthan's platebody", "Guthan's chainskirt", "Guthan's warspear", "Torag's helm", "Torag's platebody", "Torag's platelegs", "Torag's hammers", "Verac's helm", "Verac's brassard", "Verac's plateskirt", "Verac's flail"],
    "Callisto": ["Callisto cub", "Voidwaker hilt"],
    "Cerberus": ["Hellpuppy", "Eternal crystal", "Pegasian crystal", "Primordial crystal", "Jar of souls"],
    "Chambers of Xeric": ["Dexterous prayer scroll", "Arcane prayer scroll", "Dragon hunter crossbow", "Ancestral hat", "Ancestral robe top", "Ancestral robe bottom", "Dragon claws", "Twisted bow", "Olmlet", "Twisted ancestral colour kit", "Metamorphic dust"],
    "Colosseum": ["Dizana's quiver (uncharged)", "Sunfire fanatic cuirass", "Sunfire fanatic chausses", "Sunfire fanatic helm", "Echo crystal", "Tonalztics of ralos (uncharged)"],
    "Commander Zilyana": ["Pet zilyana", "Armadyl crossbow", "Saradomin hilt"],
    "Corporeal Beast": ["Pet dark core", "Elysian sigil", "Spectral sigil", "Arcane sigil", "Jar of spirits", "Spirit shield", "Holy Elixir"],
    "Dagannoth Kings": ["Pet dagannoth supreme", "Pet dagannoth rex", "Pet dagannoth prime", "Archers ring", "Seers ring", "Berserker ring", "Warrior ring"],
    "Demonic Gorilla": ["Zenyte shard"],
    "Doom of Mokhaiotl": ["Avernic treads", "Eye of ayak (uncharged)", "Mokhaiotl cloth"],
    "Duke Sucellus": ["Baron", "Virtus mask", "Virtus robe top", "Virtus robe bottom", "Eye of the duke"],
    "General Graardor": ["Pet general graardor", "Bandos hilt", "Bandos chestplate", "Bandos tassets", "Bandos boots"],
    "Giant Mole": ["Baby mole"],
    "Grotesque Guardians": ["Noon/midnight", "Jar of stone"],
    "Hueycoatl": ["Huberte"],
    "Kalphite Queen": ["Kalphite princess", "Jar of sand"],
    "Kraken": ["Pet kraken"],
    "Kree'arra": ["Pet kree'arra", "Armadyl helmet", "Armadyl chestplate", "Armadyl chainskirt", "Armadyl hilt"],
    "K'ril Tsutsaroth": ["Pet K'ril Tsutsaroth", "Zamorakian spear", "Staff of the dead", "Zamorak hilt", "Steam battlestaff"],
    "King black dragon": ["Prince black dragon"],
    "Nightmare": ["Little nightmare/Parasite", "Nightmare staff", "Inquisitor's great helm", "Inquisitor's hauberk", "Inquisitor's plateskirt", "Inquisitor's mace", "Eldritch orb", "Harmonised orb", "Volatile orb", "Jar of dreams"],
    "Nex": ["Nexling", "Ancient hilt", "Nihil horn", "Zaryte vambraces", "Torva full helm (damaged)", "Torva platebody (damaged)", "Torva platelegs (damaged)"],
    "Phantom Muspah": ["Muphin", "Venator shard"],
    "Royal Titans": ["Bran"],
    "Sarachnis": ["Sraracha", "Jar of eyes"],
    "Scorpia": ["Scorpia's Offspring"],
    "Scurrius": ["Scurry"],
    "The Leviathan": ["Lil'viathan", "Virtus mask", "Virtus robe top", "Virtus robe bottom", "Leviathan's lure"],
    "Thermonuclear smoke devil": ["Jar of smoke", "Pet smoke devil"],
    "The Whisperer": ["Wisp", "Virtus mask", "Virtus robe top", "Virtus robe bottom", "Siren's staff"],
    "Theatre of Blood": ["Lil' zik", "Avernic defender hilt", "Ghrazi rapier", "Sanguinesti staff (uncharged)", "Justiciar faceguard", "Justiciar chestguard", "Justiciar legguards", "Scythe of vitur (uncharged)", "Holy ornament kit", "Sanguine ornament kit", "Sanguine dust"],
    "Tombs of Amascut": ["Tumeken's Guardian", "Masori mask", "Masori body", "Masori chaps", "Lightbearer", "Osmumten's fang", "Elidinis' ward", "Tumeken's shadow (uncharged)"],
    "Tormented Demons": ["Tormented synapse", "Burning claw"],
    "Vardorvis": ["Butch", "Virtus mask", "Virtus robe top", "Virtus robe bottom", "Executioner's axe head"],
    "Venenatis": ["Venenatis spiderling", "Voidwaker gem"],
    "Vet'ion": ["Vet'ion jr.", "Voidwaker blade"],
    "Vorkath": ["Vorki", "Jar of decay"],
    "Yama": ["Yami", "Soulflame horn", "Oathplate helm", "Oathplate chest", "Oathplate legs"],
    "Zulrah": ["Pet snakeling", "Tanzanite mutagen", "Magma mutagen", "Jar of swamp", "Tanzanite fang", "Magic fang", "Serpentine visage"],
}

class BingoCog(commands.Cog):
    """Cog for handling bingo drop submissions, reviews, and player rolls."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        required_env_vars = [
            'EVENT_TYPE', 'EVENT_PROJECT_ID', 'EVENT_PRIVATE_KEY_ID',
            'EVENT_PRIVATE_KEY', 'EVENT_CLIENT_EMAIL', 'EVENT_CLIENT_ID',
            'EVENT_AUTH_URI', 'EVENT_TOKEN_URI', 'EVENT_AUTH_PROVIDER_X509_CERT_URL',
            'EVENT_CLIENT_X509_CERT_URL', 'EVENT_UNIVERSE_DOMAIN'
        ]

        missing_vars = [var for var in required_env_vars if not os.getenv(var)]

        if missing_vars:
            print("Bingo Cog: The following required environment variables are missing:")
            for var in missing_vars:
                print(f"  - {var}")
            print("Bingo Cog will not function properly without these.")
            self.sheet = None
            self.rsn_sheet = None
            self.roll_sheet = None
            return

        print("Bingo Cog: All required environment variables are present.")

        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        private_key_env = os.getenv('EVENT_PRIVATE_KEY')
        if not private_key_env:
            print("Bingo Cog: 'EVENT_PRIVATE_KEY' environment variable is not set.")
            self.sheet = None
            self.rsn_sheet = None
            self.roll_sheet = None
            return

        private_key_formatted = private_key_env.replace("\\n", "\n")

        credentials_dict = {
            "type": os.getenv('EVENT_TYPE'),
            "project_id": os.getenv('EVENT_PROJECT_ID'),
            "private_key_id": os.getenv('EVENT_PRIVATE_KEY_ID'),
            "private_key": private_key_formatted,
            "client_email": os.getenv('EVENT_CLIENT_EMAIL'),
            "client_id": os.getenv('EVENT_CLIENT_ID'),
            "auth_uri": os.getenv('EVENT_AUTH_URI'),
            "token_uri": os.getenv('EVENT_TOKEN_URI'),
            "auth_provider_x509_cert_url": os.getenv('EVENT_AUTH_PROVIDER_X509_CERT_URL'),
            "client_x509_cert_url": os.getenv('EVENT_CLIENT_X509_CERT_URL'),
            "universe_domain": os.getenv('EVENT_UNIVERSE_DOMAIN')
        }

        creds = Credentials.from_service_account_info(credentials_dict, scopes=scope)
        sheet_client = gspread.authorize(creds)

        sheet_id = "1VjoOx_GdzD0dNP-SnbMDjhKV8M054QQ9JgRbLQeSe-M"
        main_spreadsheet = sheet_client.open_by_key(sheet_id)
        
        # Primary sheet for drops
        self.sheet = main_spreadsheet.sheet1
        
        # New sheet for roll data
        try:
            self.roll_sheet = main_spreadsheet.worksheet("rolldata")
        except gspread.exceptions.WorksheetNotFound:
            print("Bingo Cog: 'rolldata' worksheet not found. Creating it...")
            self.roll_sheet = main_spreadsheet.add_worksheet(title="rolldata", rows="100", cols="20")
            # Set headers if new
            self.roll_sheet.update('A1:D1', [['Discord ID', 'Display Name', 'Rolls', 'Guessed Number']])

        self.rsn_sheet = sheet_client.open_by_key("1ZwJiuVMp-3p8UH0NCVYTV9_UVI26jl5kWu2nvdspl9k").worksheet("Tracker")

        self.SUBMISSION_CHANNEL_ID = 1447066912159830149
        self.REVIEW_CHANNEL_ID = 1447066849291272446
        self.LOG_CHANNEL_ID = 1447083513168924713
        self.REQUIRED_ROLE_NAME = "Event Staff"
        self.REGISTERED_ROLE_NAME = "Registered"

        print("Bingo Cog: Initialized successfully.")

    # --- Helper Methods ---

    def _get_user_row_index(self, user_id: int):
        """Finds the row index for a specific user ID in the rolldata sheet."""
        ids = self.roll_sheet.col_values(1)
        try:
            return ids.index(str(user_id)) + 1
        except ValueError:
            return None

    async def _ensure_user_exists(self, user: discord.User):
        """Ensures a user has a row in the spreadsheet, creating one if necessary."""
        row_idx = self._get_user_row_index(user.id)
        if row_idx is None:
            # Append new user: ID, Name, Rolls (0), Guess (empty)
            self.roll_sheet.append_row([str(user.id), user.display_name, "0", ""])
            return self._get_user_row_index(user.id)
        return row_idx

    # --- Commands ---

    @app_commands.command(name="addroll", description="Give a player a spin (Event Staff only)")
    @app_commands.describe(player="The player to grant a roll to")
    async def add_roll(self, interaction: discord.Interaction, player: discord.Member):
        # Check permissions
        if not any(role.name == self.REQUIRED_ROLE_NAME for role in interaction.user.roles):
            await interaction.response.send_message("Only Event Staff can grant rolls.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        
        row_idx = await self._ensure_user_exists(player)
        # Update Rolls (Column C / Index 3) to 1
        self.roll_sheet.update_cell(row_idx, 3, "1")
        
        await interaction.followup.send(f"Granted 1 roll to {player.display_name}.")

    @app_commands.command(name="guess", description="Guess a number for the bingo event")
    @app_commands.describe(number="The number you want to guess")
    async def guess(self, interaction: discord.Interaction, number: int):
        await interaction.response.defer(ephemeral=True)

        row_idx = await self._ensure_user_exists(interaction.user)
        
        # Update Display Name (B) and Guessed Number (D)
        # Column B = 2, Column D = 4
        self.roll_sheet.update_cell(row_idx, 2, interaction.user.display_name)
        self.roll_sheet.update_cell(row_idx, 4, str(number))

        await interaction.followup.send(f"Your guess of **{number}** has been recorded, {interaction.user.display_name}!")

    @app_commands.command(name="spin", description="Spin the wheel (requires a roll)")
    async def spin(self, interaction: discord.Interaction):
        await interaction.response.defer()

        row_idx = self._get_user_row_index(interaction.user.id)
        
        if row_idx is None:
            await interaction.followup.send("You don't have any rolls available. Have you participated in a guess yet?")
            return

        # Check Rolls (Column C / Index 3)
        rolls_val = self.roll_sheet.cell(row_idx, 3).value
        try:
            rolls_count = int(rolls_val) if rolls_val else 0
        except ValueError:
            rolls_count = 0

        if rolls_count <= 0:
            await interaction.followup.send("You have 0 rolls available. Win a guess to get a spin!")
            return

        # Perform Spin
        result = random.randint(1, 28)
        
        # Reset Rolls to 0
        self.roll_sheet.update_cell(row_idx, 3, "0")

        embed = discord.Embed(
            title="🎰 Bingo Spin!",
            description=f"{interaction.user.mention} spun the wheel and got...",
            color=discord.Color.gold()
        )
        embed.add_field(name="Result", value=f"**{result}**", inline=False)
        embed.set_footer(text="Your rolls have been consumed.")

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="submitdrop", description="Submit a boss drop for bingo review")
    @app_commands.describe(
        screenshot="Attach a screenshot of your drop",
        submitted_for="Optionally specify the user you're submitting this drop for"
    )
    async def submit_drop(
        self,
        interaction: discord.Interaction,
        screenshot: discord.Attachment,
        submitted_for: discord.Member = None
    ):
        if self.sheet is None:
            await interaction.response.send_message(
                "Bingo system is not properly configured. Please contact an administrator.",
                ephemeral=True
            )
            return

        if interaction.channel.id != self.SUBMISSION_CHANNEL_ID:
            await interaction.response.send_message(
                "This command can only be used in the drop submission channel.",
                ephemeral=True
            )
            return

        target_user = submitted_for or interaction.user

        await interaction.response.send_message(
            content=f"Submitting drop for {target_user.display_name}. Select the boss you received the drop from:",
            view=BossView(self, interaction.user, target_user, screenshot),
            ephemeral=True
        )


class BossSelect(discord.ui.Select):
    def __init__(self, cog: BingoCog, submitting_user, target_user, screenshot, page=0):
        self.cog = cog
        self.submitting_user = submitting_user
        self.target_user = target_user
        self.screenshot = screenshot
        self.page = page

        bosses = list(BOSS_DROPS.keys())
        max_pages = (len(bosses) - 1) // 25
        page = max(0, min(page, max_pages))

        page_bosses = bosses[page * 25: (page + 1) * 25]
        options = [discord.SelectOption(label=boss) for boss in page_bosses]

        super().__init__(placeholder="Select a boss", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        boss = self.values[0]
        await interaction.response.edit_message(
            content=f"Selected boss: {boss}. Now select the drop you received.",
            view=DropView(self.cog, self.submitting_user, self.target_user, self.screenshot, boss, page=self.page)
        )


class BossView(discord.ui.View):
    def __init__(self, cog: BingoCog, submitting_user, target_user, screenshot, page=0):
        super().__init__()
        self.cog = cog
        self.add_item(BossSelect(cog, submitting_user, target_user, screenshot, page))
        if page > 0:
            self.add_item(PreviousPageButton(cog, submitting_user, target_user, screenshot, page))
        max_pages = (len(BOSS_DROPS) - 1) // 25
        if page < max_pages:
            self.add_item(NextPageButton(cog, submitting_user, target_user, screenshot, page))


class PreviousPageButton(discord.ui.Button):
    def __init__(self, cog: BingoCog, submitting_user, target_user, screenshot, page):
        super().__init__(label="Previous Page", style=discord.ButtonStyle.secondary)
        self.cog = cog
        self.submitting_user = submitting_user
        self.target_user = target_user
        self.screenshot = screenshot
        self.page = page

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            view=BossView(self.cog, self.submitting_user, self.target_user, self.screenshot, self.page - 1)
        )


class NextPageButton(discord.ui.Button):
    def __init__(self, cog: BingoCog, submitting_user, target_user, screenshot, page):
        super().__init__(label="Next Page", style=discord.ButtonStyle.secondary)
        self.cog = cog
        self.submitting_user = submitting_user
        self.target_user = target_user
        self.screenshot = screenshot
        self.page = page

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            view=BossView(self.cog, self.submitting_user, self.target_user, self.screenshot, self.page + 1)
        )


class DropSelect(discord.ui.Select):
    def __init__(self, cog: BingoCog, submitting_user, target_user, screenshot, boss):
        self.cog = cog
        self.submitting_user = submitting_user
        self.target_user = target_user
        self.screenshot = screenshot
        self.boss = boss
        options = [discord.SelectOption(label=drop) for drop in BOSS_DROPS[boss]]
        super().__init__(placeholder=f"Select a drop from {boss}", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        drop_name = self.values[0]
        review_channel = self.cog.bot.get_channel(self.cog.REVIEW_CHANNEL_ID)

        embed = discord.Embed(title=f"{self.boss} Drop Submission", colour=discord.Colour.blurple())
        embed.add_field(name="Submitted For", value=f"{self.target_user.mention} ({self.target_user.id})", inline=False)
        embed.add_field(name="Drop Received", value=drop_name, inline=False)
        embed.add_field(name="Submitted By", value=f"{self.submitting_user.mention} ({self.submitting_user.id})", inline=False)
        embed.set_image(url=self.screenshot.url)

        await interaction.response.edit_message(content="Submitted for review.", embed=embed, view=None)

        if review_channel:
            team_mention = self.cog.get_team_role_mention(self.target_user)
            await review_channel.send(
                embed=embed,
                view=DropReviewButtons(self.cog, self.target_user, drop_name, self.screenshot.url, self.submitting_user, team_mention)
            )


class DropView(discord.ui.View):
    def __init__(self, cog: BingoCog, submitting_user, target_user, screenshot, boss, page=0):
        super().__init__()
        self.cog = cog
        self.submitting_user = submitting_user
        self.target_user = target_user
        self.screenshot = screenshot
        self.boss = boss
        self.page = page

        self.add_item(DropSelect(cog, submitting_user, target_user, screenshot, boss))
        self.add_item(self.BackButton(cog, submitting_user, target_user, screenshot, page))

    class BackButton(discord.ui.Button):
        def __init__(self, cog, submitting_user, target_user, screenshot, page):
            super().__init__(label="Back", style=discord.ButtonStyle.secondary)
            self.cog = cog
            self.submitting_user = submitting_user
            self.target_user = target_user
            self.screenshot = screenshot
            self.page = page

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.edit_message(
                content=f"Submitting drop for {self.target_user.display_name}. Select the boss you received the drop from:",
                view=BossView(
                    self.cog,
                    self.submitting_user,
                    self.target_user,
                    self.screenshot,
                    page=self.page
                )
            )


class DropReviewButtons(discord.ui.View):
    def __init__(self, cog: BingoCog, submitted_user: discord.Member, drop: str, image_url: str, submitting_user: discord.Member, team_mention: str):
        super().__init__(timeout=None)
        self.cog = cog
        self.submitted_user = submitted_user
        self.drop = drop
        self.image_url = image_url
        self.submitting_user = submitting_user
        self.team_mention = team_mention
        self.reviewer: Optional[int] = None

    def has_drop_manager_role(self, member: discord.Member) -> bool:
        return any(role.name == self.cog.REQUIRED_ROLE_NAME for role in member.roles)

    def is_moderator(self, member: discord.Member) -> bool:
        return any(role.name == "Moderators" for role in member.roles)

    @discord.ui.button(label="Review", style=discord.ButtonStyle.blurple)
    async def review(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        if not self.has_drop_manager_role(user) and not self.is_moderator(user):
            await interaction.response.send_message("You do not have permission to review.", ephemeral=True)
            return

        # Moderator logic
        if self.is_moderator(user):
            if self.reviewer is None:
                self.reviewer = user.id
                for child in self.children:
                    if child.label.startswith("Approve") or child.label.startswith("Reject"):
                        child.disabled = False
                await interaction.message.edit(
                    content=f"Being reviewed by Moderator: {user.display_name}",
                    view=self
                )
                await interaction.response.defer()

            elif self.reviewer != user.id:
                self.reviewer = None
                for child in self.children:
                    if child.label.startswith("Approve") or child.label.startswith("Reject"):
                        child.disabled = True
                await interaction.message.edit(
                    content=f"Moderator {user.display_name} canceled the review. No one is currently reviewing this.",
                    view=self
                )
                await interaction.response.defer()

            else:
                self.reviewer = None
                for child in self.children:
                    if child.label.startswith("Approve") or child.label.startswith("Reject"):
                        child.disabled = True
                await interaction.message.edit(
                    content="No one is currently reviewing this.",
                    view=self
                )
                await interaction.response.defer()
            return

        # Drop manager logic
        if self.reviewer is None:
            self.reviewer = user.id
            for child in self.children:
                if child.label.startswith("Approve") or child.label.startswith("Reject"):
                    child.disabled = False
            await interaction.message.edit(
                content=f"Being reviewed by: {user.display_name}",
                view=self
            )
            await interaction.response.defer()

        elif self.reviewer == user.id:
            self.reviewer = None
            for child in self.children:
                if child.label.startswith("Approve") or child.label.startswith("Reject"):
                    child.disabled = True
            await interaction.message.edit(
                content="No one is currently reviewing this.",
                view=self
            )
            await interaction.response.defer()

        else:
            await interaction.response.send_message(
                f"This is currently being reviewed by <@{self.reviewer}>.",
                ephemeral=True
            )

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green, disabled=True)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.reviewer != interaction.user.id:
            await interaction.response.send_message(
                "You are not the reviewer of this submission.",
                ephemeral=True
            )
            return

        errors = []

        # Try to send to log channel
        log_channel = self.cog.bot.get_channel(self.cog.LOG_CHANNEL_ID)
        if log_channel:
            try:
                embed = discord.Embed(title="Drop Approved", colour=discord.Colour.green())
                embed.add_field(name="Approved By", value=interaction.user.display_name, inline=False)
                embed.add_field(name="Drop For", value=self.submitted_user.mention, inline=False)
                embed.add_field(name="Team", value=self.team_mention, inline=False)
                embed.add_field(name="Drop", value=self.drop, inline=False)
                embed.add_field(name="Submitted By", value=self.submitting_user.mention, inline=False)
                embed.set_image(url=self.image_url)
                await log_channel.send(embed=embed)
            except Exception as e:
                print(f"Bingo Cog: Failed to send to log channel: {e}")
                errors.append("Failed to log to channel")
        else:
            errors.append("Log channel not found")

        # Try to append to sheet
        try:
            self.cog.sheet.append_row([
                interaction.user.display_name,
                self.submitted_user.display_name,
                str(self.submitted_user.id),
                self.drop,
                self.image_url,
                datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            ])
        except Exception as e:
            print(f"Bingo Cog: Failed to append to sheet: {e}")
            errors.append("Failed to log to spreadsheet")

        # Send response
        if errors:
            await interaction.response.send_message(
                f"Approved but with issues: {', '.join(errors)}. Message will be removed.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Approved and logged. This message will now be removed.",
                ephemeral=True
            )

        # Always try to delete the message
        try:
            await asyncio.sleep(1)
            await interaction.message.delete()
        except Exception as e:
            print(f"Bingo Cog: Failed to delete review message: {e}")

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red, disabled=True)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.reviewer != interaction.user.id:
            await interaction.response.send_message(
                "You are not the reviewer of this submission.",
                ephemeral=True
            )
            return

        modal = RejectReasonModal(self.cog, self, interaction)
        await interaction.response.send_modal(modal)


class RejectReasonModal(discord.ui.Modal, title="Reject Submission"):
    def __init__(self, cog: BingoCog, parent_view: discord.ui.View, interaction: discord.Interaction):
        super().__init__()
        self.cog = cog
        self.parent_view = parent_view
        self.message = interaction.message

        self.reason = discord.ui.TextInput(
            label="Reason for rejection",
            style=discord.TextStyle.paragraph,
            placeholder="Enter the reason why this drop is being rejected.",
            required=True,
            max_length=500
        )
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        logged = False

        # Try to send to log channel
        log_channel = self.cog.bot.get_channel(self.cog.LOG_CHANNEL_ID)
        if log_channel:
            try:
                embed = discord.Embed(title="Drop Rejected", colour=discord.Colour.red())
                embed.add_field(name="Rejected By", value=interaction.user.display_name, inline=False)
                embed.add_field(name="Drop For", value=self.parent_view.submitted_user.mention, inline=False)
                embed.add_field(name="Team", value=self.parent_view.team_mention, inline=False)
                embed.add_field(name="Drop", value=self.parent_view.drop, inline=False)
                embed.add_field(name="Submitted By", value=self.parent_view.submitting_user.mention, inline=False)
                embed.add_field(name="Reason", value=self.reason.value, inline=False)
                embed.set_image(url=self.parent_view.image_url)
                await log_channel.send(embed=embed)
                logged = True
            except Exception as e:
                print(f"Bingo Cog: Failed to send rejection to log channel: {e}")

        if logged:
            await interaction.response.send_message(
                "Submission rejected and logged. This message will now be removed.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Submission rejected but failed to log. This message will now be removed.",
                ephemeral=True
            )

        # Always try to delete the message
        try:
            await asyncio.sleep(1)
            await self.message.delete()
        except Exception as e:
            print(f"Bingo Cog: Failed to delete review message: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(BingoCog(bot))
