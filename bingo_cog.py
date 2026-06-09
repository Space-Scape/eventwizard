import os
import discord
from discord.ext import commands, tasks
from discord import app_commands
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timezone
import asyncio
from typing import Optional, NamedTuple
import random
import time
import io
import re
import json
import urllib.parse
import urllib.request
import urllib.error

# ---------------------------
# Boss-Drop Mapping
# ---------------------------

#BOSS_DROPS = {
#    "Abyssal Sire": ["Abyssal orphan", "Unsired", "Abyssal head", "Bludgeon spine", "Bludgeon claw", "Bludgeon axon", "Jar of miasma", "Abyssal dagger", "Abyssal whip"],
#    "Alchemical Hydra": ["Ikkle hydra", "Hydra's claw", "Hydra tail", "Hydra leather", "Hydra's fang", "Hydra's eye", "Hydra's heart", "Jar of chemicals"],
#    "Amoxliatl": ["Moxi"],
#    "Araxxor": ["Noxious pommel", "Noxious point", "Noxious blade", "Araxyte fang", "Araxyte head", "Aranea boots", "Jar of venom", "Coagulated venom", "Nid"],
#    "Brutus": ["Beef"],
#    "Callisto": ["Callisto cub", "Tyrannical ring", "Dragon pickaxe", "Claws of callisto", "Voidwaker hilt"],
#    "Cerberus": ["Hellpuppy", "Eternal crystal", "Pegasian crystal", "Primordial crystal", "Smouldering stone", "Jar of souls"],
#    "Chaos Fanatic": ["Odium shard 1", "Malediction shard 1"],
#    "Chambers of Xeric": ["Dexterous prayer scroll", "Arcane prayer scroll", "Twisted buckler", "Dragon hunter crossbow", "Dinh's bulwark", "Ancestral hat", "Ancestral robe top", "Ancestral robe bottom", "Dragon claws", "Elder maul", "Kodai insignia", "Twisted bow", "Olmlet", "Twisted ancestral colour kit", "Metamorphic dust"],
#    "Colosseum": ["Sunfire fanatic cuirass", "Sunfire fanatic chausses", "Sunfire fanatic helm", "Echo crystal", "Tonalztics of ralos (uncharged)"],
#    "Corporeal Beast": ["Pet dark core", "Elysian sigil", "Spectral sigil", "Arcane sigil", "Jar of spirits", "Spirit shield", "Holy Elixir"],
#    "Crazy Archaeologist": ["Odium shard 2", "Malediction shard 2", "Fedora"],
#    "Dagannoth Kings": ["Pet dagannoth supreme", "Pet dagannoth rex", "Pet dagannoth prime", "Archers ring", "Seers ring", "Berserker ring", "Warrior ring"],
#    "Demonic Gorilla": ["Zenyte shard", "Ballista limbs", "Ballista spring", "Light frame", "Heavy frame", "Monkey tail"],
#    "Doom of Mokhaiotl": ["Dom", "Avernic treads", "Eye of ayak (uncharged)", "Mokhaiotl cloth"],
#    "Duke Sucellus": ["Baron", "Virtus mask", "Virtus robe top", "Virtus robe bottom", "Magus vestige", "Eye of the duke"],
#    "Gauntlet": ["Youngllef", "Crystal weapon seed", "Crystal armour seed", "Enhanced crystal weapon seed"],
#    "Giant Mole": ["Baby mole"],
#    "Hueycoatl": ["Huberte", "Dragon hunter wand", "Hueycoatl hide", "Tome of earth (empty)"],
#    "King black dragon": ["Prince black dragon"],
#    "Nightmare": ["Little nightmare/Parasite", "Nightmare staff", "Inquisitor's great helm", "Inquisitor's hauberk", "Inquisitor's plateskirt", "Inquisitor's mace", "Eldritch orb", "Harmonised orb", "Volatile orb", "Jar of dreams"],
#    "Nex": ["Nexling", "Ancient hilt", "Nihil horn", "Zaryte vambraces", "Torva full helm (damaged)", "Torva platebody (damaged)", "Torva platelegs (damaged)"],
#    "Phantom Muspah": ["Muphin", "Venator shard", "Ancient icon", "Charged ice", "Frozen cache", "Ancient essence"],
#    "Royal Titans": ["Bran", "Deadeye prayer scroll", "Mystic vigour prayer scroll", "Fire element staff crown", "Ice element staff crown"],
#    "Revenants": ["Thammaron's sceptre", "Viggora's chainmace", "Craw's bow", "Ancient relic", "Ancient effigy", "Ancient medallion", "Ancient statuette", "Ancient totem"],
#    "Scorpia": ["Scorpia's Offspring", "Malediction shard 3", "Odium shard 3"],
#    "Scurrius": ["Scurry"],
#    "The Leviathan": ["Lil'viathan", "Virtus mask", "Virtus robe top", "Virtus robe bottom", "Venator vestige", "Leviathan's lure"],
#    "The Whisperer": ["Wisp", "Virtus mask", "Virtus robe top", "Virtus robe bottom", "Bellator vestige", "Siren's staff"],
#    "Theatre of Blood": ["Lil' zik", "Avernic defender hilt", "Ghrazi rapier", "Sanguinesti staff (uncharged)", "Justiciar faceguard", "Justiciar chestguard", "Justiciar legguards", "Scythe of vitur (uncharged)", "Holy ornament kit", "Sanguine ornament kit", "Sanguine dust"],
#    "Tombs of Amascut": ["Tumeken's Guardian", "Masori mask", "Masori body", "Masori chaps", "Lightbearer", "Osmumten's fang", "Elidinis' ward", "Tumeken's shadow (uncharged)"],
#    "Tormented Demons": ["Tormented synapse", "Burning claw"],
#    "Vardorvis": ["Butch", "Virtus mask", "Virtus robe top", "Virtus robe bottom", "Ultor vestige", "Executioner's axe head"],
#    "Venenatis": ["Venenatis spiderling", "Fangs of venenatis", "Dragon pickaxe", "Voidwaker gem", "Treasonous ring"],
#    "Vet'ion": ["Vet'ion jr.", "Skull of vet'ion", "Dragon pickaxe", "Voidwaker blade", "Ring of the gods", "Skeleton champion scroll"],
#    "Vorkath": ["Vorki", "Draconic visage", "Skeletal visage", "Jar of decay", "Dragonbone necklace"],
#    "Yama": ["Yami", "Soulflame horn", "Oathplate helm", "Oathplate chest", "Oathplate legs", "Dossier"],
#    "Zulrah": ["Pet snakeling", "Tanzanite mutagen", "Magma mutagen", "Jar of swamp", "Tanzanite fang", "Magic fang", "Serpentine visage", "Uncut onyx"],
#    "Pets/Misc": ["Gull", "Kalphite princess", "Noon/Midnight", "Pet General Graardor", "Pet K'ril Tsutsaroth", "Pet Kraken", "Pet Kree'Arra", "Pet smoke devil", "Pet Zilyana", "Smolcano", "Sraracha"]
#}

class MessageImageSource(NamedTuple):
    attachment: Optional[discord.Attachment]
    image_url: str

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

        self.sheet = main_spreadsheet.sheet1

        signup_sheet_id = os.getenv("BINGO_SIGNUP_SHEET_ID", sheet_id)
        signup_worksheet_name = os.getenv("BINGO_SIGNUP_WORKSHEET", "Buy ins")
        signup_spreadsheet = None
        try:
            signup_spreadsheet = sheet_client.open_by_key(signup_sheet_id)
            self.signup_sheet = signup_spreadsheet.worksheet(signup_worksheet_name)
            print(f"Bingo Cog: Signup spreadsheet loaded: {signup_spreadsheet.title} ({signup_sheet_id})")
            print(f"Bingo Cog: Signup worksheet loaded: {signup_worksheet_name}")
        except Exception as e:
            print(f"Bingo Cog: Could not load signup spreadsheet/tab '{signup_sheet_id}' / '{signup_worksheet_name}': {e}")
            self.signup_sheet = None

        self.backups_sheet = None
        self.BACKUP_LIST_CHANNEL_ID = int(os.getenv("BINGO_BACKUP_LIST_CHANNEL_ID", "1504316523571839156"))
        self.BACKUP_LIST_WORKSHEET = os.getenv("BINGO_BACKUP_LIST_WORKSHEET", "Backups")
        self.BACKUP_LIST_POLL_SECONDS = int(os.getenv("BINGO_BACKUP_LIST_POLL_SECONDS", "30"))
        self.backup_list_message_id = int(os.getenv("BINGO_BACKUP_LIST_MESSAGE_ID", "0") or "0")
        self._backup_list_last_signature = None

        self.SIGNUPS_CHANNEL_ID = int(os.getenv("BINGO_SIGNUPS_CHANNEL_ID", "1504323734222147604") or "1504323734222147604")
        self.SIGNUPS_POLL_SECONDS = int(os.getenv("BINGO_SIGNUPS_POLL_SECONDS", "30"))
        self.signups_message_id = int(os.getenv("BINGO_SIGNUPS_MESSAGE_ID", "0") or "0")
        self._signups_last_signature = None

        try:
            backup_spreadsheet = signup_spreadsheet or main_spreadsheet
            self.backups_sheet = backup_spreadsheet.worksheet(self.BACKUP_LIST_WORKSHEET)
            print(f"Bingo Cog: Backups worksheet loaded: {backup_spreadsheet.title} / {self.BACKUP_LIST_WORKSHEET}")
        except Exception as e:
            print(f"Bingo Cog: Could not load Backups worksheet '{self.BACKUP_LIST_WORKSHEET}': {e}")
            self.backups_sheet = None
        
        self.rsn_sheet = sheet_client.open_by_key("1ZwJiuVMp-3p8UH0NCVYTV9_UVI26jl5kWu2nvdspl9k").worksheet("Tracker")
        self._rsn_lookup_cache = None
        self.signup_panel_jump_url = None

        self.SIGNUP_SPREADSHEET_URL = os.getenv(
            "BINGO_SIGNUP_SPREADSHEET_URL",
            "https://docs.google.com/spreadsheets/d/1xrcTgwaq5UqsoJRI7wtj3RKBCcR7pVeyu1g6NGIESA0/edit?gid=0#gid=0"
        ).strip()
        self.SIGNUP_CHANNEL_ID = int(os.getenv("BINGO_SIGNUP_CHANNEL_ID", "1504323734222147604") or "1504323734222147604")
        self.SIGNUP_ANNOUNCEMENT_THREAD_ID = int(os.getenv("BINGO_SIGNUP_ANNOUNCEMENT_THREAD_ID", "1505020794491764846") or "1505020794491764846")
        self._pending_signup_screenshot_user_ids = set()
        self._signup_dm_sent_keys = set()
        self._dm_send_lock = asyncio.Lock()

        self.WOM_API_KEY = os.getenv("WOM_API_KEY", "").strip()
        self.WOM_GROUP_ID = os.getenv("WOM_GROUP_ID", "").strip()
        self.WOM_CODE = os.getenv("WOM_CODE", "").strip()
        self.WOM_BASE_URL = os.getenv("WOM_BASE_URL", "https://api.wiseoldman.net/v2").rstrip("/")
        self._wom_rank_cache = {}

        self.BANNED_EVENT_DISCORD_IDS = {
            " ",
            " ",
        }
        self.BANNED_EVENT_RSNS = {""}

        self.SUBMISSION_CHANNEL_ID = 1447066912159830149
        self.REVIEW_CHANNEL_ID = 1504315926017867847
        self.LOG_CHANNEL_ID = 1504315879431864372
        self.REQUIRED_ROLE_NAME = "Event Staff"
        self.REGISTERED_ROLE_NAME = "Registered"
        self.BINGO_PLAYER_ROLE_ID = 1464304452059267208
        self.CAPTAIN_SIGNUP_ROLE_NAMES = {"Event Staff", "Clan Staff", "Senior Staff", "Event Captains"}

        self.GUILD_ID = 1272629330115297330
        self.DROP_DETECTION_CHANNEL_ID = 1272875477555482666
        self.TEAM_ROLE_IDS = {
            1: 1464306125582241954,
            2: 1464306197531328552,
            3: 1464306160202154075,
            4: 1464306263868309564,
            5: 1464306051049328832,
            6: 1464306298513395855,
        }
        self.TEAM_CHANNEL_IDS = {
            1: 1504315482587660459,
            2: 1504315751274909848,
            3: 1504315637898674279,
            4: 1504315822292861108,
            5: 1504315384797462649,
            6: 1504315537814065415,
        }
        self._auto_drop_prompted_message_ids: set[int] = set()
        self._auto_drop_review_submitted_message_ids: set[int] = set()
        self._auto_drop_prompt_lock = asyncio.Lock()

        self._drop_duplicate_lock = asyncio.Lock()
        self._pending_auto_drop_keys: set[str] = set()
        self._recent_drop_submission_keys: dict[str, float] = {}
        self.DROP_DUPLICATE_BLOCK_SECONDS = int(os.getenv("BINGO_DROP_DUPLICATE_BLOCK_SECONDS", "600"))

        self._auto_drop_recent_prompt_keys: dict[str, float] = {}
        self._auto_drop_recent_open_notice_keys: dict[str, float] = {}
        self._open_drop_submission_keys: set[str] = set()
        self.AUTO_DROP_PROMPT_COOLDOWN_SECONDS = 60
        self.AUTO_DROP_OPEN_NOTICE_COOLDOWN_SECONDS = 60

        self.CAPTAIN_SIGNUP_START_ROW = int(os.getenv("BINGO_CAPTAIN_SIGNUP_START_ROW", "3"))
        self.CAPTAIN_SIGNUP_END_ROW = int(os.getenv("BINGO_CAPTAIN_SIGNUP_END_ROW", "16"))
        self.SOLO_SIGNUP_START_ROW = int(os.getenv("BINGO_SOLO_SIGNUP_START_ROW", "18"))
        self.SOLO_SIGNUP_END_ROW = int(os.getenv("BINGO_SOLO_SIGNUP_END_ROW", "130"))
        self.DUO_SIGNUP_START_ROW = int(os.getenv("BINGO_DUO_SIGNUP_START_ROW", "132"))
        self.DUO_SIGNUP_END_ROW = int(os.getenv("BINGO_DUO_SIGNUP_END_ROW", "232"))

        self.bot.add_view(BingoSignupPanelView(self))
        self.bot.add_view(BackupListView(self))

        if self.backups_sheet is not None and not self.backup_list_updater.is_running():
            self.backup_list_updater.change_interval(seconds=self.BACKUP_LIST_POLL_SECONDS)
            self.backup_list_updater.start()

        if self.signup_sheet is not None and not self.signups_updater.is_running():
            self.signups_updater.change_interval(seconds=self.SIGNUPS_POLL_SECONDS)
            self.signups_updater.start()

        if not getattr(self.bot.intents, "message_content", False):
            print(
                "Bingo Cog WARNING: message_content intent is disabled. "
                "Screenshot signup capture will not work until Message Content Intent is enabled "
                "in both the Discord Developer Portal and the bot startup intents."
            )
        
        print("Bingo Cog: Initialized successfully.")

    def cog_unload(self):
        if hasattr(self, "backup_list_updater") and self.backup_list_updater.is_running():
            self.backup_list_updater.cancel()
        if hasattr(self, "signups_updater") and self.signups_updater.is_running():
            self.signups_updater.cancel()

    @tasks.loop(seconds=30)
    async def backup_list_updater(self):
        """Mirror the Backups worksheet into a single edited Discord embed."""
        if self.backups_sheet is None:
            return

        try:
            names = await asyncio.to_thread(self.read_backup_names_from_sheet)
            signature = "\n".join(names)
            if signature == self._backup_list_last_signature:
                return

            await self.post_or_update_backup_list(names)
            self._backup_list_last_signature = signature
        except Exception as e:
            print(f"Bingo Cog: Backup list update failed: {e}")

    @backup_list_updater.before_loop
    async def before_backup_list_updater(self):
        await self.bot.wait_until_ready()

    def read_backup_names_from_sheet(self) -> list[str]:
        """Read backup display names starting at row 2.

        The backup signup sheet uses the same basic columns as solo signups, so
        the player's public name is normally the RSN in column C. For older or
        manual entries, column A is used as a fallback.
        """
        if self.backups_sheet is None:
            return []

        values = self.backups_sheet.get("A2:H")
        names = []
        for row in values:
            rsn = str(row[2] if len(row) > 2 else "").strip()
            discord_name = str(row[0] if len(row) > 0 else "").strip()
            name = rsn or discord_name
            if name:
                names.append(name)
        return names

    def build_backup_list_embed(self, names: list[str]) -> discord.Embed:
        if names:
            description = "\n".join(f"**{index}.** {name}" for index, name in enumerate(names, start=1))
        else:
            description = "No backups are currently listed."

        embed = discord.Embed(
            title="Bingo Backup List",
            description=description,
            colour=discord.Colour.gold(),
            timestamp=datetime.now(timezone.utc),
        )
        embed.set_footer(text="Automatically updates from the Backups worksheet.")
        return embed

    async def find_existing_backup_list_message(self, channel: discord.TextChannel) -> Optional[discord.Message]:
        if self.backup_list_message_id:
            try:
                return await channel.fetch_message(self.backup_list_message_id)
            except Exception:
                self.backup_list_message_id = 0

        try:
            async for message in channel.history(limit=50):
                if message.author.id != self.bot.user.id:
                    continue
                for embed in message.embeds:
                    if embed.title == "Bingo Backup List":
                        self.backup_list_message_id = message.id
                        return message
        except Exception as e:
            print(f"Bingo Cog: Could not search for existing backup list message: {e}")

        return None

    async def post_or_update_backup_list(self, names: list[str]) -> None:
        channel = self.bot.get_channel(self.BACKUP_LIST_CHANNEL_ID)
        if channel is None:
            try:
                channel = await self.bot.fetch_channel(self.BACKUP_LIST_CHANNEL_ID)
            except Exception as e:
                print(f"Bingo Cog: Backup list channel not found ({self.BACKUP_LIST_CHANNEL_ID}): {e}")
                return

        embed = self.build_backup_list_embed(names)
        message = await self.find_existing_backup_list_message(channel)

        view = BackupListView(self)

        if message is not None:
            await message.edit(embed=embed, view=view)
            return

        message = await channel.send(embed=embed, view=view)
        self.backup_list_message_id = message.id
        print(f"Bingo Cog: Posted backup list message {message.id} in channel {self.BACKUP_LIST_CHANNEL_ID}.")


    @tasks.loop(seconds=30)
    async def signups_updater(self):
        """Mirror signup totals into a single edited Discord embed."""
        if self.signup_sheet is None:
            return

        try:
            counts = await asyncio.to_thread(self.get_signup_counts)
            signature = f"{counts['solo_count']}|{counts['duo_count']}|{counts['captain_count']}|{counts['total_count']}"
            if signature == self._signups_last_signature:
                return

            await self.post_or_update_signups(counts)
            self._signups_last_signature = signature
        except Exception as e:
            print(f"Bingo Cog: Signups update failed: {e}")

    @signups_updater.before_loop
    async def before_signups_updater(self):
        await self.bot.wait_until_ready()

    def build_signups_embed(self, counts: dict[str, int]) -> discord.Embed:
        embed = discord.Embed(
            title="Current Bingo Signup Totals",
            colour=discord.Colour.gold(),
            timestamp=datetime.now(timezone.utc),
        )
        embed.add_field(name="Solo Signups", value=str(counts["solo_count"]), inline=True)
        embed.add_field(name="Duo Signups", value=str(counts["duo_count"]), inline=True)
        embed.add_field(name="Total Signups", value=str(counts["total_count"]), inline=True)
        embed.add_field(name="Captains", value=str(counts["captain_count"]), inline=False)
        embed.set_footer(text="Automatically updates from the signup worksheet.")
        return embed

    async def find_existing_signups_message(self, channel: discord.TextChannel) -> Optional[discord.Message]:
        if self.signups_message_id:
            try:
                return await channel.fetch_message(self.signups_message_id)
            except Exception:
                self.signups_message_id = 0

        try:
            async for message in channel.history(limit=50):
                if message.author.id != self.bot.user.id:
                    continue
                for embed in message.embeds:
                    if embed.title == "Current Bingo Signup Totals":
                        self.signups_message_id = message.id
                        return message
        except Exception as e:
            print(f"Bingo Cog: Could not search for existing signups message: {e}")

        return None

    async def post_or_update_signups(self, counts: dict[str, int]) -> None:
        channel = self.bot.get_channel(self.SIGNUPS_CHANNEL_ID)
        if channel is None:
            try:
                channel = await self.bot.fetch_channel(self.SIGNUPS_CHANNEL_ID)
            except Exception as e:
                print(f"Bingo Cog: Signups channel not found ({self.SIGNUPS_CHANNEL_ID}): {e}")
                return

        embed = self.build_signups_embed(counts)
        message = await self.find_existing_signups_message(channel)

        if message is not None:
            await message.edit(embed=embed)
            return

        message = await channel.send(embed=embed)
        self.signups_message_id = message.id
        print(f"Bingo Cog: Posted signups message {message.id} in channel {self.SIGNUPS_CHANNEL_ID}.")

    def get_team_role_mention(self, member: discord.Member) -> str:
        """Get the team role mention for a member."""
        for role in member.roles:
            if role.name.startswith("Team "):
                return role.mention
        return "*No team*"

    def has_captain_signup_access(self, member: discord.Member) -> bool:
        """Return True if a member may use the Captain Signup button."""
        return any(role.name in self.CAPTAIN_SIGNUP_ROLE_NAMES for role in getattr(member, "roles", []))

    def update_captain_co_captain(self, row: int, co_captain: str) -> None:
        """Write the optional co-captain value into column I for a captain signup row."""
        if not row or not co_captain:
            return
        current_values = self.get_signup_row_values(row)
        if not str(current_values[8]).strip():
            self.signup_sheet.update_cell(row, 9, co_captain)
            self.format_signup_row(row)

    def get_member_signup_name(self, member: Optional[discord.Member]) -> str:
        """Return the member's server nickname for signup display/storage."""
        if member is None:
            return ""
        return getattr(member, "nick", None) or getattr(member, "display_name", None) or getattr(member, "name", "")

    async def resolve_guild_member(self, channel: discord.abc.Messageable, member: discord.abc.User) -> discord.abc.User:
        """Best effort to convert a User into a guild Member so server nicknames are available."""
        guild = getattr(channel, "guild", None)
        if guild is None:
            return member

        cached_member = guild.get_member(member.id)
        if cached_member is not None:
            return cached_member

        try:
            return await guild.fetch_member(member.id)
        except Exception:
            return member

    def get_member_rank_name(self, member: discord.Member) -> str:
        """Legacy helper kept for compatibility. Signup rank now comes from WOM when available."""
        return ""

    def normalize_signup_value(self, value) -> str:
        """Normalize values for matching signup rows."""
        return str(value or "").strip().casefold()

    def normalize_rsn_for_lookup(self, value) -> str:
        """Normalize RSNs so "Joe | Mama" style cells can be matched reliably."""
        return re.sub(r"[^a-z0-9]", "", str(value or "").casefold())

    def split_possible_rsns(self, value) -> list[str]:
        """Split a cell that may contain multiple registered names like "Main | Alt"."""
        text = str(value or "")
        parts = re.split(r"[|,/;\n\r]+", text)
        return [self.normalize_rsn_for_lookup(part) for part in parts if self.normalize_rsn_for_lookup(part)]

    def get_cell_by_possible_headers(self, row: list[str], headers: list[str], wanted_headers: list[str]) -> str:
        """Return a row cell using several possible Google Sheet header names."""
        normalized_headers = [str(header or "").strip().casefold().replace(" ", "_") for header in headers]
        wanted = {str(header or "").strip().casefold().replace(" ", "_") for header in wanted_headers}
        for index, header in enumerate(normalized_headers):
            if header in wanted and index < len(row):
                return str(row[index]).strip()
        for index, header in enumerate(normalized_headers):
            if any(wanted_header in header for wanted_header in wanted) and index < len(row):
                return str(row[index]).strip()
        return ""

    def build_rsn_lookup_cache(self) -> dict[str, dict]:
        """Build an RSN -> Discord info lookup from the RSN Tracker sheet.

        Expected Tracker headers from your sheet:
        A: Discord Username
        B: Discord ID
        C: Old RSN
        D: New RSN

        The lookup still supports alternate header names and cells with multiple
        names separated by |, /, commas, semicolons, or new lines.
        """
        lookup: dict[str, dict] = {}
        if self.rsn_sheet is None:
            return lookup

        try:
            values = self.rsn_sheet.get_all_values()
        except Exception as e:
            print(f"Bingo Cog: Failed to read RSN tracker sheet: {e}")
            return lookup

        if not values:
            print("Bingo Cog: RSN tracker sheet is empty.")
            return lookup

        headers = [str(header or "").strip() for header in values[0]]
        normalized_headers = [header.casefold().replace(" ", "_") for header in headers]
        data_rows = values[1:]

        def find_header_index(possible_names: list[str], fallback_index: Optional[int] = None) -> Optional[int]:
            wanted = {name.casefold().replace(" ", "_") for name in possible_names}
            for index, header in enumerate(normalized_headers):
                if header in wanted:
                    return index
            for index, header in enumerate(normalized_headers):
                if any(name in header for name in wanted):
                    return index
            return fallback_index

        username_index = find_header_index([
            "discord_username", "discord username", "discord_nickname", "discord nickname",
            "discord_name", "discord name", "username", "nickname", "name"
        ], 0)
        discord_id_index = find_header_index([
            "discord_id", "discord id", "user_id", "user id", "id"
        ], 1)

        rsn_indexes = []
        for possible_names, fallback in (
            (["old_rsn", "old rsn", "previous_rsn", "previous rsn"], 2),
            (["new_rsn", "new rsn", "current_rsn", "current rsn", "rsn"], 3),
        ):
            index = find_header_index(possible_names, fallback)
            if index is not None and index not in rsn_indexes:
                rsn_indexes.append(index)

        for index, header in enumerate(normalized_headers):
            if any(token in header for token in ("rsn", "runescape", "main", "iron")) and index not in rsn_indexes:
                rsn_indexes.append(index)

        for row_number, row in enumerate(data_rows, start=2):
            discord_name = str(row[username_index]).strip() if username_index is not None and username_index < len(row) else ""
            discord_id = str(row[discord_id_index]).strip() if discord_id_index is not None and discord_id_index < len(row) else ""

            if not discord_id:
                for candidate in row:
                    candidate_text = str(candidate or "").strip()
                    if re.fullmatch(r"\d{15,22}", candidate_text):
                        discord_id = candidate_text
                        break

            rsn_values = []
            for index in rsn_indexes:
                if index < len(row):
                    rsn_values.append(row[index])

            for cell in rsn_values:
                for normalized_rsn in self.split_possible_rsns(cell):
                    if not normalized_rsn:
                        continue
                    lookup[normalized_rsn] = {
                        "discord_id": discord_id,
                        "discord_name": discord_name,
                        "tracker_row": row_number,
                    }

        print(f"Bingo Cog: Loaded {len(lookup)} RSN lookup entries from Tracker.")
        return lookup

    def find_registered_rsn_info(self, rsn: str) -> Optional[dict]:
        """Find Discord info for an RSN from the RSN Tracker sheet.

        The tracker cache is refreshed once on a miss. This matters when an RSN
        was just added to Old RSN / New RSN while the bot is already running.
        """
        normalized = self.normalize_rsn_for_lookup(rsn)
        if not normalized:
            return None

        if self._rsn_lookup_cache is None:
            self._rsn_lookup_cache = self.build_rsn_lookup_cache()

        info = self._rsn_lookup_cache.get(normalized)
        if info is not None:
            return info

        self._rsn_lookup_cache = self.build_rsn_lookup_cache()
        return self._rsn_lookup_cache.get(normalized)

    async def enrich_registered_info_for_guild(self, channel: discord.abc.Messageable, info: Optional[dict]) -> Optional[dict]:
        """Use the Discord ID from Tracker to get the member's current server nickname when possible."""
        if not info:
            return info

        enriched = dict(info)
        guild = getattr(channel, "guild", None)
        discord_id = str(enriched.get("discord_id", "")).strip()
        if not guild or not discord_id.isdigit():
            return enriched

        try:
            member = guild.get_member(int(discord_id)) or await guild.fetch_member(int(discord_id))
            if member is not None:
                enriched["discord_name"] = self.get_member_signup_name(member)
        except Exception as e:
            print(f"Bingo Cog: Could not fetch Tracker member {discord_id}: {e}")

        return enriched

    def registered_rsn_error_message(self, rsn: str) -> str:
        return (
            f'Username not found for **{rsn}**. Make sure the player with that RSN has registered via `/register` '
            'with their main, their iron, or both names with a separator in-between, such as "Joe | Mama".'
        )

    def banned_signup_error_message(self) -> str:
        return "This player can not participate. Please select another partner or sign up solo."

    def is_banned_event_participant(
        self,
        rsn: str = "",
        discord_id: str = "",
        registered_info: Optional[dict] = None,
    ) -> bool:
        """Return True if this RSN / Discord ID is banned from this event."""
        normalized_rsn = self.normalize_rsn_for_lookup(rsn)
        if normalized_rsn and normalized_rsn in self.BANNED_EVENT_RSNS:
            return True

        discord_id = str(discord_id or "").strip()
        if discord_id and discord_id in self.BANNED_EVENT_DISCORD_IDS:
            return True

        if registered_info:
            tracker_id = str(registered_info.get("discord_id", "")).strip()
            if tracker_id and tracker_id in self.BANNED_EVENT_DISCORD_IDS:
                return True

            tracker_name = self.normalize_rsn_for_lookup(registered_info.get("discord_name", ""))
            if tracker_name and tracker_name in self.BANNED_EVENT_RSNS:
                return True

        return False

    async def validate_signup_rsns(self, channel: discord.abc.Messageable, data: dict) -> tuple[bool, str]:
        """Validate that signup RSNs exist in the RSN Tracker and are allowed to participate."""
        submitter_rsn = str(data.get("RSN", "")).strip()
        submitter_info = self.find_registered_rsn_info(submitter_rsn)

        submitter_discord_id = str(data.get("_submitter_discord_id", "")).strip()
        if self.is_banned_event_participant(submitter_rsn, submitter_discord_id, submitter_info):
            return False, self.banned_signup_error_message()

        if data.get("signup_type") == "Duo":
            partner_rsn = str(data.get("Duo Partner", "")).strip()
            if partner_rsn:
                partner_info = self.find_registered_rsn_info(partner_rsn)
                if not partner_info:
                    print(f"Bingo Cog: Duo partner RSN not found in Tracker; using submitter fallback if row is created: {partner_rsn}")
                if self.is_banned_event_participant(partner_rsn, "", partner_info):
                    return False, self.banned_signup_error_message()

        return True, ""

    def xp_for_level(self, level: int) -> int:
        """Return the OSRS cumulative XP required for a level."""
        points = 0
        for lvl in range(1, level):
            points += int(lvl + 300 * (2 ** (lvl / 7.0)))
        return points // 4

    def wom_headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "RancourBingoSignupBot/1.0",
        }
        if self.WOM_API_KEY:
            headers["Authorization"] = f"Bearer {self.WOM_API_KEY}"
            headers["x-api-key"] = self.WOM_API_KEY
        if self.WOM_GROUP_ID:
            headers["x-wom-group-id"] = self.WOM_GROUP_ID
        if self.WOM_CODE:
            headers["x-wom-code"] = self.WOM_CODE
        return headers

    def wom_request_blocking(self, method: str, path: str, payload: Optional[dict] = None) -> Optional[dict | list]:
        """Blocking WOM HTTP helper, called through asyncio.to_thread."""
        url = f"{self.WOM_BASE_URL}{path}"
        body = None
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(url, data=body, method=method.upper(), headers=self.wom_headers())
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            if e.code not in (404, 429):
                try:
                    detail = e.read().decode("utf-8")[:300]
                except Exception:
                    detail = ""
                print(f"Bingo Cog: WOM HTTP {e.code} for {url}: {detail}")
            return None
        except Exception as e:
            print(f"Bingo Cog: WOM request failed for {url}: {e}")
            return None

    async def fetch_wom_player_details(self, rsn: str) -> Optional[dict]:
        """Fetch a player's WOM details. POST updates when possible, GET/search as fallback."""
        rsn = str(rsn or "").strip()
        if not rsn:
            return None

        cache_key = self.normalize_rsn_for_lookup(rsn)
        if cache_key in self._wom_rank_cache:
            return self._wom_rank_cache[cache_key]

        encoded = urllib.parse.quote(rsn, safe="")
        details = await asyncio.to_thread(self.wom_request_blocking, "POST", f"/players/{encoded}")
        if not isinstance(details, dict):
            details = await asyncio.to_thread(self.wom_request_blocking, "GET", f"/players/{encoded}")

        if not isinstance(details, dict):
            query = urllib.parse.urlencode({"username": rsn, "limit": 5})
            results = await asyncio.to_thread(self.wom_request_blocking, "GET", f"/players/search?{query}")
            if isinstance(results, list) and results:
                wanted = self.normalize_rsn_for_lookup(rsn)
                best = None
                for candidate in results:
                    candidate_name = candidate.get("displayName") or candidate.get("username") or ""
                    if self.normalize_rsn_for_lookup(candidate_name) == wanted:
                        best = candidate
                        break
                best = best or results[0]
                best_name = best.get("displayName") or best.get("username") or rsn
                encoded_best = urllib.parse.quote(str(best_name), safe="")
                details = await asyncio.to_thread(self.wom_request_blocking, "GET", f"/players/{encoded_best}")

        if isinstance(details, dict):
            self._wom_rank_cache[cache_key] = details
            return details

        self._wom_rank_cache[cache_key] = None
        return None

    def wom_latest_data(self, details: Optional[dict]) -> dict:
        if not isinstance(details, dict):
            return {}
        snapshot = details.get("latestSnapshot") or details.get("latest_snapshot") or {}
        data = snapshot.get("data") if isinstance(snapshot, dict) else None
        if isinstance(data, dict):
            return data
        if any(key in details for key in ("skills", "bosses", "activities", "computed")):
            return details
        return {}

    def wom_skill_level(self, data: dict, metric: str) -> int:
        skill = ((data.get("skills") or {}).get(metric) or {}) if isinstance(data, dict) else {}
        level = skill.get("level")
        if isinstance(level, (int, float)) and level > 0:
            return int(level)
        xp = skill.get("experience")
        if not isinstance(xp, (int, float)) or xp < 0:
            return 0
        current = 1
        for lvl in range(2, 127):
            if xp >= self.xp_for_level(lvl):
                current = lvl
            else:
                break
        return min(current, 126)

    def wom_combat_level(self, details: Optional[dict], data: dict) -> int:
        """Return combat level from WOM, falling back to OSRS combat calculation.

        WOM responses can expose combat level in a few different shapes depending
        on endpoint/update state. If we miss it, do not let the classifier treat
        the account like a normal C-rank account; calculate from skills instead.
        """

        def extract_from_source(source) -> int:
            if not isinstance(source, dict):
                return 0
            for key in ("combatLevel", "combat_level", "combat"):
                value = source.get(key)
                if isinstance(value, dict):
                    value = value.get("value") or value.get("level") or value.get("score")
                if isinstance(value, (int, float)) and value > 0:
                    return int(value)
            return 0

        sources = [details or {}, data.get("computed") or {}]
        if isinstance(details, dict):
            for key in ("player", "profile", "latestSnapshot", "latest_snapshot"):
                value = details.get(key)
                if isinstance(value, dict):
                    sources.append(value)
                    if isinstance(value.get("data"), dict):
                        sources.append(value.get("data"))
                    if isinstance(value.get("computed"), dict):
                        sources.append(value.get("computed"))

        for source in sources:
            combat = extract_from_source(source)
            if combat:
                return combat
        attack = self.wom_skill_level(data, "attack")
        strength = self.wom_skill_level(data, "strength")
        defence = self.wom_skill_level(data, "defence")
        hitpoints = self.wom_skill_level(data, "hitpoints")
        ranged = self.wom_skill_level(data, "ranged")
        magic = self.wom_skill_level(data, "magic")
        prayer = self.wom_skill_level(data, "prayer")

        if min(attack, strength, defence, hitpoints, ranged, magic, prayer) <= 0:
            return 0

        base = 0.25 * (defence + hitpoints + (prayer // 2))
        melee = 0.325 * (attack + strength)
        range_based = 0.325 * ((3 * ranged) // 2)
        mage_based = 0.325 * ((3 * magic) // 2)
        return int(base + max(melee, range_based, mage_based))

    def wom_boss_kc(self, data: dict, metric: str) -> int:
        boss = ((data.get("bosses") or {}).get(metric) or {}) if isinstance(data, dict) else {}
        value = boss.get("kills")
        if not isinstance(value, (int, float)) or value < 0:
            return 0
        return int(value)

    def wom_player_build_or_type(self, details: Optional[dict]) -> str:
        if not isinstance(details, dict):
            return ""
        parts = []
        for key in ("type", "build", "status"):
            value = details.get(key)
            if value:
                parts.append(str(value))
        player = details.get("player")
        if isinstance(player, dict):
            for key in ("type", "build", "status"):
                value = player.get(key)
                if value:
                    parts.append(str(value))
        return " ".join(parts).casefold()

    def classify_wom_rank(self, details: Optional[dict], submitted_ironman: str = "") -> str:
        """Return A/B/C, or blank for Wild Card / uncertain cases."""
        data = self.wom_latest_data(details)
        if not data:
            return ""

        slayer = self.wom_skill_level(data, "slayer")
        combat = self.wom_combat_level(details, data)

        hmt = self.wom_boss_kc(data, "theatre_of_blood_hard_mode")
        tob = self.wom_boss_kc(data, "theatre_of_blood")
        cm = self.wom_boss_kc(data, "chambers_of_xeric_challenge_mode")
        cox = self.wom_boss_kc(data, "chambers_of_xeric")
        toa_expert = self.wom_boss_kc(data, "tombs_of_amascut_expert")
        toa = self.wom_boss_kc(data, "tombs_of_amascut")

        sol = self.wom_boss_kc(data, "sol_heredit")
        zuk = self.wom_boss_kc(data, "tzkal_zuk")
        hydra = self.wom_boss_kc(data, "alchemical_hydra")
        araxxor = self.wom_boss_kc(data, "araxxor")
        cerb = self.wom_boss_kc(data, "cerberus")

        raids_total = hmt + tob + cm + cox + toa_expert + toa
        normal_low_count = sum(1 for kc in (cox, tob, toa) if kc < 10)
        slayer_boss_low_count = sum(1 for kc in (hydra, araxxor, cerb) if kc < 25)
        all_boss_total = sum(
            max(0, int((boss or {}).get("kills", 0)))
            for boss in (data.get("bosses") or {}).values()
            if isinstance(boss, dict) and isinstance(boss.get("kills"), (int, float))
        )

        if not combat or combat < 115:
            return ""

        if slayer and slayer < 92:
            return "C"

        if slayer and slayer < 80:
            return ""

        a_raid_ready = hmt >= 48 and cm >= 48 and toa_expert >= 98
        if slayer >= 95 and combat >= 125 and sol >= 1 and zuk >= 1 and a_raid_ready:
            return "A"

        if slayer >= 93 and combat >= 120 and (hmt >= 25 or cm >= 25 or raids_total >= 280):
            return "B"
            
        if slayer >= 92:
            if slayer_boss_low_count >= 2:
                return ""
            raid_kcs = [cox, tob, toa, cm, hmt, toa_expert]
            if max(raid_kcs) >= 100 and sum(1 for kc in raid_kcs if kc < 25) >= 4:
                return ""
            if max(hydra, araxxor, cerb, cox, tob, toa, cm, hmt, toa_expert) >= 300 and sum(1 for kc in (hydra, araxxor, cerb, cox, tob, toa) if kc < 25) >= 3:
                return ""

        if normal_low_count >= 2 or raids_total < 50 or all_boss_total < 500:
            return "C"

        return ""

    async def get_auto_rank_for_rsn(self, rsn: str, submitted_ironman: str = "") -> str:
        details = await self.fetch_wom_player_details(rsn)
        rank = self.classify_wom_rank(details, submitted_ironman=submitted_ironman)
        try:
            data = self.wom_latest_data(details)
            combat = self.wom_combat_level(details, data)
            slayer = self.wom_skill_level(data, "slayer")
            print(f"Bingo Cog: WOM rank for {rsn}: {rank or 'Wild Card/blank'} (combat={combat or 'unknown'}, slayer={slayer or 'unknown'})")
        except Exception:
            print(f"Bingo Cog: WOM rank for {rsn}: {rank or 'Wild Card/blank'}")
        return rank

    async def add_auto_rank_to_signup_data(self, data: dict, rsn_key: str = "RSN", rank_key: str = "Rank", iron_key: str = "Ironman") -> None:
        """Add Rank to data in-place if WOM can confidently classify the account."""
        if data.get(rank_key):
            return
        rsn = str(data.get(rsn_key, "")).strip()
        if not rsn:
            return
        try:
            data[rank_key] = await self.get_auto_rank_for_rsn(rsn, data.get(iron_key, ""))
        except Exception as e:
            print(f"Bingo Cog: WOM auto-rank failed for {rsn}: {e}")
            data[rank_key] = ""

    def get_signup_bounds(self, signup_type: str) -> tuple[int, int]:
        """Return the configured row range for Captain, Solo, or Duo signups."""
        if signup_type == "Captain":
            return self.CAPTAIN_SIGNUP_START_ROW, self.CAPTAIN_SIGNUP_END_ROW
        if signup_type == "Duo":
            return self.DUO_SIGNUP_START_ROW, self.DUO_SIGNUP_END_ROW
        return self.SOLO_SIGNUP_START_ROW, self.SOLO_SIGNUP_END_ROW

    def get_signup_row_values(self, row: int) -> list[str]:
        """Read columns A-L for a signup row and pad missing cells."""
        values = self.signup_sheet.get(f"A{row}:L{row}")
        row_values = values[0] if values else []
        while len(row_values) < 12:
            row_values.append("")
        return row_values[:12]

    async def add_bingo_player_role_for_signup(
        self,
        submitting_member: discord.Member,
        data: dict,
        partner_row: Optional[int] = None,
        partner_info: Optional[dict] = None,
    ) -> None:
        """Add Bingo Player role to the signup member and duo partner."""
        guild = submitting_member.guild
        if guild is None:
            return

        bingo_role = guild.get_role(self.BINGO_PLAYER_ROLE_ID)
        if bingo_role is None:
            print(f"Bingo Cog: Bingo player role {self.BINGO_PLAYER_ROLE_ID} not found in guild {guild.id}.")
            return

        target_ids = {submitting_member.id}
        if str(data.get("signup_type", "")).strip() == "Duo":
            partner_discord_id = str((partner_info or {}).get("discord_id", "")).strip()
            if partner_discord_id.isdigit():
                target_ids.add(int(partner_discord_id))
            if partner_row is not None:
                row_values = self.get_signup_row_values(partner_row)
                partner_id_from_sheet = str(row_values[1] if len(row_values) > 1 else "").strip()
                if partner_id_from_sheet.isdigit():
                    target_ids.add(int(partner_id_from_sheet))

        for target_id in target_ids:
            member = guild.get_member(target_id)
            if member is None or bingo_role in member.roles:
                continue
            try:
                await member.add_roles(bingo_role, reason="Bingo signup")
            except discord.Forbidden:
                print(f"Bingo Cog: Missing permission to add bingo role for {target_id}.")
            except Exception as e:
                print(f"Bingo Cog: Failed to add bingo role for {target_id}: {e}")

    def format_signup_row(self, row: int) -> None:
        """Leave signup row formatting alone; the sheet template controls visibility/style."""
        return


    def count_signup_rows(self, signup_type: str) -> int:
        """Count signed-up rows in the selected signup section."""
        start_row, end_row = self.get_signup_bounds(signup_type)

        try:
            values = self.signup_sheet.get(f"A{start_row}:L{end_row}")
        except Exception:
            values = []

        count = 0
        for offset in range(end_row - start_row + 1):
            row_values = values[offset] if offset < len(values) else []
            row_discord_id = str(row_values[1]).strip() if len(row_values) > 1 else ""
            row_rsn = str(row_values[2]).strip() if len(row_values) > 2 else ""
            if row_discord_id or row_rsn:
                count += 1

        return count

    def get_signup_counts(self) -> dict[str, int]:
        """Return signup totals for solo, duo, captain, and combined participants."""
        solo_count = self.count_signup_rows("Solo")
        duo_count = self.count_signup_rows("Duo")
        captain_count = self.count_signup_rows("Captain")
        total_count = solo_count + duo_count + captain_count
        return {
            "solo_count": solo_count,
            "duo_count": duo_count,
            "captain_count": captain_count,
            "total_count": total_count,
        }
    def find_next_signup_row(self, signup_type: str) -> int:
        """Find the next open row in the correct signup section of the signup sheet."""
        start_row, end_row = self.get_signup_bounds(signup_type)

        try:
            values = self.signup_sheet.get(f"A{start_row}:L{end_row}")
        except Exception:
            values = []

        for offset in range(end_row - start_row + 1):
            row_values = values[offset] if offset < len(values) else []
            has_content = any(str(cell).strip() for cell in row_values[:11])
            if not has_content:
                return start_row + offset

        raise RuntimeError(f"No open {signup_type.lower()} signup rows are available between rows {start_row} and {end_row}.")

    def find_signup_row_by_discord_id(self, discord_id: int, signup_type: str) -> Optional[int]:
        """Find an existing signup row by Discord ID in the selected section."""
        start_row, end_row = self.get_signup_bounds(signup_type)
        wanted_id = str(discord_id)

        try:
            values = self.signup_sheet.get(f"A{start_row}:L{end_row}")
        except Exception:
            return None

        for offset, row_values in enumerate(values):
            row_discord_id = str(row_values[1]).strip() if len(row_values) > 1 else ""
            if row_discord_id == wanted_id:
                return start_row + offset
        return None

    def find_signup_row_by_rsn(self, rsn: str, signup_type: str) -> Optional[int]:
        """Find an existing signup row by RSN in the selected section."""
        start_row, end_row = self.get_signup_bounds(signup_type)
        wanted_rsn = self.normalize_signup_value(rsn)
        if not wanted_rsn:
            return None

        try:
            values = self.signup_sheet.get(f"A{start_row}:L{end_row}")
        except Exception:
            return None

        for offset, row_values in enumerate(values):
            row_rsn = self.normalize_signup_value(row_values[2] if len(row_values) > 2 else "")
            if row_rsn == wanted_rsn:
                return start_row + offset
        return None

    def find_existing_signup_row(self, member: discord.Member, data: dict, registered_info: Optional[dict] = None) -> Optional[int]:
        """Find the row this signup should update, prioritizing the submitted RSN's tracker ID, then RSN, then submitter ID.

        This prevents a user who signs up someone else from overwriting or creating
        rows under their own Discord nickname/ID when the submitted RSN is already
        registered to another Discord account.
        """
        signup_type = data.get("signup_type", "Solo")

        tracker_id = str((registered_info or {}).get("discord_id", "")).strip()
        if tracker_id.isdigit():
            row = self.find_signup_row_by_discord_id(int(tracker_id), signup_type)
            if row:
                return row

        row = self.find_signup_row_by_rsn(data.get("RSN", ""), signup_type)
        if row:
            return row

        if member is not None:
            row = self.find_signup_row_by_discord_id(member.id, signup_type)
            if row:
                return row

        return None

    def merge_blank_signup_fields(self, row: int, new_values: list[str]) -> None:
        """Fill only blank cells in A-L, except Discord nickname may refresh and screenshot cells may be filled when empty."""
        current_values = self.get_signup_row_values(row)
        merged = []

        for index, new_value in enumerate(new_values):
            current_value = str(current_values[index]).strip() if index < len(current_values) else ""
            new_value = str(new_value or "").strip()

            if index == 11:
                merged.append(new_value if not current_value and new_value else current_value)
                continue

            if index == 0 and new_value:
                merged.append(new_value)
                continue
                
            if not current_value and new_value:
                merged.append(new_value)
            else:
                merged.append(current_value)

        self.signup_sheet.update(f"A{row}:L{row}", [merged])
        self.format_signup_row(row)

    def build_signup_row_values(
        self,
        member: Optional[discord.Member],
        data: dict,
        buyin_screenshot: str = "",
        registered_info: Optional[dict] = None,
    ) -> list[str]:
        """Build columns A-L for a signup row.

        Sheet columns: A Discord Nickname, B Discord ID, C RSN, D Playtime,
        E Timezone/Location, F Buy In Screenshot, G Comments, H Duo,
        I Duo Partner, J Duo Buy In Screenshot, K Ironman, L Rank.
        Rank is auto-filled from WOM when the player clearly fits A/B/C. Ambiguous wild cards stay blank.
        """
        signup_type = data.get("signup_type", "Solo")
        is_duo = signup_type == "Duo"
        is_captain = signup_type == "Captain"

        discord_name = ""
        discord_id = ""

        if registered_info and (registered_info.get("discord_name") or registered_info.get("discord_id")):
            discord_name = registered_info.get("discord_name", "")
            discord_id = registered_info.get("discord_id", "")
        elif member is not None:
            discord_name = self.get_member_signup_name(member)
            discord_id = str(member.id)
        else:
            discord_name = data.get("Discord Nickname", "")
            discord_id = data.get("Discord ID", "")

        return [
            discord_name,
            discord_id,
            data.get("RSN", ""),
            data.get("Playtime", ""),
            data.get("Timezone/Location", ""),
            buyin_screenshot or data.get("Buy In Screenshot", ""),
            data.get("Comments", ""),
            "" if is_captain else ("Yes" if is_duo else "No"),
            data.get("Co-Captain", "") if is_captain else (data.get("Duo Partner", "") if is_duo else ""),
            data.get("Duo Buy In Screenshot", "") if is_duo else "",
            data.get("Ironman", ""),
            "" if is_captain else data.get("Rank", ""),
        ]

    def write_or_update_signup_to_sheet(self, member: discord.Member, data: dict, buyin_screenshot: str, registered_info: Optional[dict] = None) -> int:
        """Create a new signup row or fill blanks in an existing row.

        registered_info should be the RSN Tracker record for data["RSN"]. When
        present, it controls Discord Nickname/ID so signing up another player
        records that player's identity rather than the submitter's.
        """
        if self.signup_sheet is None:
            raise RuntimeError("Signup sheet is not configured.")

        row = self.find_existing_signup_row(member, data, registered_info=registered_info)
        if row is None:
            row = self.find_next_signup_row(data.get("signup_type", "Solo"))

        row_values = self.build_signup_row_values(member, data, buyin_screenshot, registered_info=registered_info)
        self.merge_blank_signup_fields(row, row_values)
        return row

    def ensure_duo_partner_row(self, submitting_member: discord.Member, data: dict, buyin_screenshot: str, partner_info: Optional[dict]) -> int:
        """Make sure the duo partner has their own row in the Duo section.

        The partner row should be created even if the first screenshot arrives
        before the optional partner modal has fully settled. RSN tracker data is
        used when available, but the row still gets created from the submitted
        partner fields so captains do not lose the signup.
        """
        partner_rsn = str(data.get("Duo Partner", "")).strip()
        if not partner_rsn:
            raise RuntimeError("Duo partner RSN is missing.")

        tracker_partner_info = partner_info or self.find_registered_rsn_info(partner_rsn)
        identity_info = tracker_partner_info
        if identity_info is None and submitting_member is not None:
            identity_info = {
                "discord_id": str(submitting_member.id),
                "discord_name": self.get_member_signup_name(submitting_member),
                "tracker_row": "fallback_submitter",
            }

        partner_row = None
        partner_discord_id = str((tracker_partner_info or {}).get("discord_id", "")).strip()
        if partner_discord_id.isdigit():
            partner_row = self.find_signup_row_by_discord_id(int(partner_discord_id), "Duo")
        if partner_row is None:
            partner_row = self.find_signup_row_by_rsn(partner_rsn, "Duo")
        if partner_row is None:
            partner_row = self.find_next_signup_row("Duo")

        partner_info = identity_info or {}

        placeholder_data = {
            "signup_type": "Duo",
            "RSN": partner_rsn,
            "Playtime": data.get("Duo Playtime", ""),
            "Timezone/Location": data.get("Duo Timezone/Location", ""),
            "Buy In Screenshot": buyin_screenshot,
            "Comments": "",
            "Duo Partner": data.get("RSN", ""),
            "Duo Buy In Screenshot": data.get("Duo Buy In Screenshot", ""),
            "Ironman": data.get("Duo Ironman", ""),
            "Discord Nickname": str((partner_info or {}).get("discord_name", "")).strip(),
            "Discord ID": partner_discord_id,
            "Rank": data.get("Duo Rank", ""),
        }

        self.merge_blank_signup_fields(
            partner_row,
            self.build_signup_row_values(None, placeholder_data, buyin_screenshot=buyin_screenshot, registered_info=partner_info),
        )
        return partner_row

    def update_duo_second_screenshot(self, submitter_row: int, partner_row: Optional[int], screenshot_url: str) -> None:
        """Put the optional second screenshot into Duo Buy In Screenshot for both duo rows."""
        if not screenshot_url:
            return

        for row in {submitter_row, partner_row}:
            if not row:
                continue
            current_values = self.get_signup_row_values(row)
            if not str(current_values[9]).strip():
                self.signup_sheet.update_cell(row, 10, screenshot_url)
                self.format_signup_row(row)


    def find_next_drop_log_row(self) -> int:
        """Find the next blank drop-log row, starting at row 2.

        This is intentionally separate from signup rows. Signup rows start at 18/132,
        but drop approvals should log directly under the drop-log headers.
        """
        if self.sheet is None:
            raise RuntimeError("Drop log sheet is not configured.")

        start_row = int(os.getenv("BINGO_DROP_LOG_START_ROW", "2"))
        end_row = int(os.getenv("BINGO_DROP_LOG_END_ROW", "2000"))

        try:
            values = self.sheet.get(f"A{start_row}:F{end_row}")
        except Exception:
            values = []

        for offset in range(end_row - start_row + 1):
            row_values = values[offset] if offset < len(values) else []
            if not any(str(cell).strip() for cell in row_values[:6]):
                return start_row + offset

        raise RuntimeError(f"No open drop-log rows are available between rows {start_row} and {end_row}.")

    def log_approved_drop_to_sheet(
        self,
        reviewer_name: str,
        submitted_user_name: str,
        submitted_user_id: int,
        drop: str,
        image_url: str,
    ) -> int:
        """Write an approved drop to the drop-log sheet beginning at row 2."""
        row = self.find_next_drop_log_row()
        values = [[
            reviewer_name,
            submitted_user_name,
            str(submitted_user_id),
            drop,
            image_url,
            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        ]]
        self.sheet.update(f"A{row}:F{row}", values)
        return row


    def get_backup_row_values(self, row: int) -> list[str]:
        """Read columns A-H for a backup row and pad missing cells."""
        values = self.backups_sheet.get(f"A{row}:H{row}")
        row_values = values[0] if values else []
        while len(row_values) < 8:
            row_values.append("")
        return row_values[:8]

    def find_next_backup_row(self) -> int:
        """Find the next open row in the Backups worksheet, starting at row 2."""
        if self.backups_sheet is None:
            raise RuntimeError("Backups worksheet is not configured.")

        start_row = int(os.getenv("BINGO_BACKUP_START_ROW", "2"))
        end_row = int(os.getenv("BINGO_BACKUP_END_ROW", "1000"))

        try:
            values = self.backups_sheet.get(f"A{start_row}:H{end_row}")
        except Exception:
            values = []

        for offset in range(end_row - start_row + 1):
            row_values = values[offset] if offset < len(values) else []
            has_content = any(str(cell).strip() for cell in row_values[:8])
            if not has_content:
                return start_row + offset

        raise RuntimeError(f"No open backup rows are available between rows {start_row} and {end_row}.")

    def find_backup_row_by_discord_id(self, discord_id: int) -> Optional[int]:
        """Find an existing backup row by Discord ID."""
        if self.backups_sheet is None:
            return None

        start_row = int(os.getenv("BINGO_BACKUP_START_ROW", "2"))
        end_row = int(os.getenv("BINGO_BACKUP_END_ROW", "1000"))
        wanted_id = str(discord_id)

        try:
            values = self.backups_sheet.get(f"A{start_row}:H{end_row}")
        except Exception:
            return None

        for offset, row_values in enumerate(values):
            row_discord_id = str(row_values[1]).strip() if len(row_values) > 1 else ""
            if row_discord_id == wanted_id:
                return start_row + offset
        return None

    def find_backup_row_by_rsn(self, rsn: str) -> Optional[int]:
        """Find an existing backup row by RSN in column C."""
        if self.backups_sheet is None:
            return None

        start_row = int(os.getenv("BINGO_BACKUP_START_ROW", "2"))
        end_row = int(os.getenv("BINGO_BACKUP_END_ROW", "1000"))
        wanted_rsn = self.normalize_signup_value(rsn)
        if not wanted_rsn:
            return None

        try:
            values = self.backups_sheet.get(f"A{start_row}:H{end_row}")
        except Exception:
            return None

        for offset, row_values in enumerate(values):
            row_rsn = self.normalize_signup_value(row_values[2] if len(row_values) > 2 else "")
            if row_rsn == wanted_rsn:
                return start_row + offset
        return None

    def find_existing_backup_row(self, member: discord.Member, data: dict, registered_info: Optional[dict] = None) -> Optional[int]:
        """Find the backup row to update, prioritizing the submitted RSN identity."""
        tracker_id = str((registered_info or {}).get("discord_id", "")).strip()
        if tracker_id.isdigit():
            row = self.find_backup_row_by_discord_id(int(tracker_id))
            if row:
                return row

        row = self.find_backup_row_by_rsn(data.get("RSN", ""))
        if row:
            return row

        if member is not None:
            row = self.find_backup_row_by_discord_id(member.id)
            if row:
                return row

        return None

    def build_backup_row_values(
        self,
        member: Optional[discord.Member],
        data: dict,
        registered_info: Optional[dict] = None,
    ) -> list[str]:
        """Build columns A-H for a backup row.

        Backups columns: A Discord Nickname, B Discord ID, C RSN, D Playtime,
        E Timezone/Location, F Comments, G Ironman, H Rank.
        """
        if registered_info and (registered_info.get("discord_name") or registered_info.get("discord_id")):
            discord_name = registered_info.get("discord_name", "")
            discord_id = registered_info.get("discord_id", "")
        elif member is not None:
            discord_name = self.get_member_signup_name(member)
            discord_id = str(member.id)
        else:
            discord_name = data.get("Discord Nickname", "")
            discord_id = data.get("Discord ID", "")

        return [
            discord_name,
            discord_id,
            data.get("RSN", ""),
            data.get("Playtime", ""),
            data.get("Timezone/Location", ""),
            data.get("Comments", ""),
            data.get("Ironman", ""),
            data.get("Rank", ""),
        ]

    def merge_blank_backup_fields(self, row: int, new_values: list[str]) -> None:
        """Fill only blank backup cells, refreshing the visible Discord nickname."""
        current_values = self.get_backup_row_values(row)
        merged = []

        for index, new_value in enumerate(new_values):
            current_value = str(current_values[index]).strip() if index < len(current_values) else ""
            new_value = str(new_value or "").strip()

            if index == 7:
                merged.append(new_value if not current_value and new_value else current_value)
                continue

            if index == 0 and new_value:
                merged.append(new_value)
                continue

            if not current_value and new_value:
                merged.append(new_value)
            else:
                merged.append(current_value)

        self.backups_sheet.update(f"A{row}:H{row}", [merged])

    def write_or_update_backup_to_sheet(self, member: discord.Member, data: dict, registered_info: Optional[dict] = None) -> int:
        """Create a new backup row or fill blanks in an existing row."""
        if self.backups_sheet is None:
            raise RuntimeError("Backups worksheet is not configured.")

        row = self.find_existing_backup_row(member, data, registered_info=registered_info)
        if row is None:
            row = self.find_next_backup_row()

        row_values = self.build_backup_row_values(member, data, registered_info=registered_info)
        self.merge_blank_backup_fields(row, row_values)
        return row

    def build_backup_signup_embed(self, member: discord.Member, data: dict) -> discord.Embed:
        """Build the public embed after a backup signup is saved."""
        backup_name = str(data.get("RSN", "")).strip() or self.get_member_signup_name(member)
        embed = discord.Embed(
            title=f"New Backup! {backup_name} has signed up as a backup!",
            description=member.mention,
            colour=discord.Colour.gold(),
        )
        return embed

    def get_signup_link_text(self) -> str:
        """Return a clickable signup-panel jump link when known."""
        if self.signup_panel_jump_url:
            return f"[Click here]({self.signup_panel_jump_url})"
        return "Scroll to the signup panel above"

    def get_signup_followup_message(self) -> str:
        """Return the large public signup prompt shown after each new-signup embed."""
        if self.signup_panel_jump_url:
            return f"# Want to sign up? [Click here]({self.signup_panel_jump_url})!"
        return "# Want to sign up? Please scroll to the signup panel above or ask staff to repost it."

    def build_signup_embeds(self, member: discord.Member, data: dict, image_urls: list[str]) -> list[discord.Embed]:
        """Build the public New Signup embed or embeds."""
        signup_type = data.get("signup_type")
        is_duo = signup_type == "Duo"
        is_captain = signup_type == "Captain"
        colour = discord.Colour.blue() if is_duo else (discord.Colour.gold() if is_captain else discord.Colour.green())

        signup_name = data.get("RSN", "").strip() or self.get_member_signup_name(member)

        if is_captain:
            co_captain = str(data.get("Co-Captain", "")).strip()
            if co_captain:
                title = f"New Signup! {signup_name} has signed up as a captain with {co_captain}!"
            else:
                title = f"New Signup! {signup_name} has signed up as a captain!"
        elif is_duo:
            partner_text = str(data.get("Duo Partner", "")).strip()
            if partner_text:
                title = f"New Signup! {signup_name} has signed up as a duo with {partner_text}!"
            else:
                title = f"New Signup! {signup_name} has signed up as a duo!"
        else:
            title = f"New Signup! {signup_name} has signed up solo!"

        embeds = []
        first_embed = discord.Embed(title=title, colour=colour)
        first_embed.description = member.mention
        if image_urls:
            first_embed.set_image(url=image_urls[0])
        embeds.append(first_embed)

        if len(image_urls) > 1:
            second_embed = discord.Embed(title="Partner Buy-In Screenshot", colour=colour)
            second_embed.set_image(url=image_urls[1])
            embeds.append(second_embed)

        return embeds

    def build_duo_partner_signup_embed(self, data: dict, partner_info: Optional[dict], image_url: str) -> discord.Embed:
        """Build the public New Signup embed for the duo partner row.

        When one player signs up both members of a duo, the partner also gets
        their own visible New Signup post. The same first buy-in screenshot is
        used because one screenshot may show both buy-ins.
        """
        submitter_rsn = str(data.get("RSN", "")).strip()
        partner_rsn = str(data.get("Duo Partner", "")).strip()

        partner_display = partner_rsn or str((partner_info or {}).get("discord_name", "")).strip() or "Duo Partner"
        partner_title = f"New Signup! {partner_display} has signed up as a duo"
        if submitter_rsn:
            partner_title += f" with {submitter_rsn}"
        partner_title += "!"

        embed = discord.Embed(
            title=partner_title,
            colour=discord.Colour.blue(),
        )

        partner_id = str((partner_info or {}).get("discord_id", "")).strip()
        if partner_id.isdigit():
            embed.description = f"<@{partner_id}>"

        if image_url:
            embed.set_image(url=image_url)

        return embed

    async def safe_delete_message(self, message: discord.Message) -> None:
        try:
            await message.delete()
        except discord.Forbidden:
            print("Bingo Cog: Missing permission to delete signup screenshot message.")
        except discord.NotFound:
            return
        except discord.HTTPException as e:
            if getattr(e, "code", None) == 10008:
                return
            print(f"Bingo Cog: Failed to delete signup screenshot message: {e}")

    async def attachment_to_discord_file(self, attachment: discord.Attachment, fallback_name: str) -> tuple[discord.File, str]:
        """Download an uploaded screenshot and re-attach it to the public embed.

        This avoids broken embed images after the bot deletes the user's original
        screenshot message. The spreadsheet still stores the original attachment URL.
        """
        raw = await attachment.read()
        original_name = attachment.filename or fallback_name
        safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", original_name)
        if "." not in safe_name:
            safe_name += ".png"
        return discord.File(io.BytesIO(raw), filename=safe_name), safe_name

    async def get_signup_announcement_channel(self) -> Optional[discord.abc.Messageable]:
        """Return the thread where public New Signup messages should be posted."""
        channel = self.bot.get_channel(self.SIGNUP_ANNOUNCEMENT_THREAD_ID)
        if channel is not None:
            return channel
        try:
            return await self.bot.fetch_channel(self.SIGNUP_ANNOUNCEMENT_THREAD_ID)
        except Exception as e:
            print(f"Bingo Cog: Signup announcement thread not found ({self.SIGNUP_ANNOUNCEMENT_THREAD_ID}): {e}")
            return None

    async def send_signup_announcement(self, *, embed: Optional[discord.Embed] = None, file: Optional[discord.File] = None, content: Optional[str] = None) -> Optional[discord.Message]:
        """Send public signup announcements to the configured thread only."""
        announcement_channel = await self.get_signup_announcement_channel()
        if announcement_channel is None:
            return None
        try:
            if file is not None:
                return await announcement_channel.send(content=content, embed=embed, file=file)
            return await announcement_channel.send(content=content, embed=embed)
        except Exception as e:
            print(f"Bingo Cog: Failed to send signup announcement to thread {self.SIGNUP_ANNOUNCEMENT_THREAD_ID}: {e}")
            return None

    async def send_signup_image_post(
        self,
        *,
        image_url: str,
        file: Optional[discord.File] = None,
        filename: Optional[str] = None,
        colour: Optional[discord.Colour] = None,
    ) -> Optional[discord.Message]:
        """Post only the buy-in image to the signup announcement thread.

        This intentionally has no "New Signup" title/text. The public thread
        gets the proof image only; the spreadsheet row and completion DM are the
        actual signup confirmation.
        """
        embed = discord.Embed(colour=colour or discord.Colour.gold())
        if file is not None and filename:
            embed.set_image(url=f"attachment://{filename}")
            return await self.send_signup_announcement(embed=embed, file=file)
        if image_url:
            embed.set_image(url=image_url)
            return await self.send_signup_announcement(embed=embed)
        return None

    async def send_signup_completed_dm(self, user: discord.abc.User, row: int, signup_type: str, rsn: str = "") -> None:
        """DM a player after their signup is saved. Throttled to avoid Discord DM rate limits."""
        if user is None or not row:
            return

        user_id = getattr(user, "id", None)
        dm_key = (str(user_id), int(row), str(signup_type).casefold())
        if dm_key in self._signup_dm_sent_keys:
            return

        display_rsn = str(rsn or "your account").strip()
        message = (
            f"Your {signup_type.lower()} signup for **{display_rsn}** is complete.\n"
            f"You were saved to row **{row}** on the signup spreadsheet:\n"
            f"{self.SIGNUP_SPREADSHEET_URL}"
        )

        async with self._dm_send_lock:
            for attempt in range(2):
                try:
                    await asyncio.sleep(1.5 if attempt == 0 else 6.0)
                    await user.send(message)
                    self._signup_dm_sent_keys.add(dm_key)
                    return
                except discord.Forbidden:
                    print(f"Bingo Cog: Could not DM signup completion to {getattr(user, 'id', 'unknown')} because DMs are closed.")
                    return
                except discord.HTTPException as e:
                    if getattr(e, "code", None) == 40003 and attempt == 0:
                        print(f"Bingo Cog: DM rate limited for {getattr(user, 'id', 'unknown')}; retrying once.")
                        continue
                    print(f"Bingo Cog: Failed to DM signup completion to {getattr(user, 'id', 'unknown')}: {e}")
                    return
                except Exception as e:
                    print(f"Bingo Cog: Failed to DM signup completion to {getattr(user, 'id', 'unknown')}: {e}")
                    return

    async def send_signup_completed_dm_by_registered_info(self, guild: Optional[discord.Guild], registered_info: Optional[dict], row: int, signup_type: str, rsn: str = "") -> None:
        """DM a signup completion message to a tracker user when possible."""
        discord_id = str((registered_info or {}).get("discord_id", "")).strip()
        if not discord_id.isdigit():
            return

        user = None
        if guild is not None:
            user = guild.get_member(int(discord_id))
        if user is None:
            try:
                user = await self.bot.fetch_user(int(discord_id))
            except Exception as e:
                print(f"Bingo Cog: Could not fetch user {discord_id} for signup completion DM: {e}")
                return

        await self.send_signup_completed_dm(user, row, signup_type, rsn)

    async def send_incorrect_signup_image_dm(self, user: discord.abc.User) -> None:
        """DM users who post a screenshot without first starting a signup."""
        message = (
            "You posted a buy-in image in the signup channel, but I do not have an active signup form waiting for you.\n\n"
            "To sign up correctly:\n"
            "1. Go to the signup panel.\n"
            "2. Click **Solo Signup**, **Duo Signup**, or **Captain Signup** if you are staff.\n"
            "3. Fill out the form.\n"
            "4. Only post your buy-in screenshot after the bot asks you to post it.\n\n"
            "Please start from the signup panel and try again."
        )
        try:
            await user.send(message)
        except discord.Forbidden:
            print(f"Bingo Cog: Could not DM incorrect signup-image instructions to {getattr(user, 'id', 'unknown')} because DMs are closed.")
        except Exception as e:
            print(f"Bingo Cog: Failed to DM incorrect signup-image instructions to {getattr(user, 'id', 'unknown')}: {e}")



    async def get_channel_by_id(self, channel_id: int) -> Optional[discord.abc.Messageable]:
        """Return a cached/fetched channel by ID."""
        if not channel_id:
            return None
        channel = self.bot.get_channel(channel_id)
        if channel is not None:
            return channel
        try:
            return await self.bot.fetch_channel(channel_id)
        except Exception as e:
            print(f"Bingo Cog: Could not fetch channel {channel_id}: {e}")
            return None

    def flatten_message_text(self, message: discord.Message) -> str:
        """Collect content/embed text from a message for drop detection."""
        parts = [message.content or ""]
        for embed in message.embeds:
            for value in (
                getattr(embed, "title", None),
                getattr(embed, "description", None),
            ):
                if value:
                    parts.append(str(value))
            for field in getattr(embed, "fields", []) or []:
                if getattr(field, "name", None):
                    parts.append(str(field.name))
                if getattr(field, "value", None):
                    parts.append(str(field.value))
            footer = getattr(embed, "footer", None)
            footer_text = getattr(footer, "text", None) if footer else None
            if footer_text:
                parts.append(str(footer_text))
            author = getattr(embed, "author", None)
            author_name = getattr(author, "name", None) if author else None
            if author_name:
                parts.append(str(author_name))
        return "\n".join(parts)

    def find_drop_name_in_text(self, text: str) -> Optional[str]:
        """Find the longest configured drop name present in a text blob."""
        normalized_text = re.sub(r"\s+", " ", str(text or "")).casefold()
        matches = []
        for drops in BOSS_DROPS.values():
            for drop in drops:
                normalized_drop = re.sub(r"\s+", " ", str(drop or "")).casefold()
                if normalized_drop and normalized_drop in normalized_text:
                    matches.append(drop)
        if not matches:
            return None
        return max(matches, key=len)

    def get_boss_for_drop(self, drop_name: str) -> str:
        for boss, drops in BOSS_DROPS.items():
            if drop_name in drops:
                return boss
        return ""

    def get_member_team_number(self, member: discord.Member) -> Optional[int]:
        member_role_ids = {role.id for role in getattr(member, "roles", [])}
        for team_number, role_id in self.TEAM_ROLE_IDS.items():
            if role_id in member_role_ids:
                return team_number
        return None

    def normalize_auto_drop_key_value(self, value: str) -> str:
        """Normalize player/drop pieces for duplicate-open-submission tracking."""
        return re.sub(r"[^a-z0-9]+", "", str(value or "").casefold())

    def get_open_drop_submission_key(self, member: discord.Member, drop_name: str) -> str:
        """Return a stable key for one player's one drop currently in review."""
        member_id = str(getattr(member, "id", "") or "")
        normalized_drop = self.normalize_auto_drop_key_value(drop_name)
        return f"{member_id}:{normalized_drop}" if member_id and normalized_drop else ""

    def has_open_drop_submission(self, member: discord.Member, drop_name: str) -> bool:
        key = self.get_open_drop_submission_key(member, drop_name)
        return bool(key and key in self._open_drop_submission_keys)

    def cleanup_recent_drop_keys(self) -> None:
        now = time.monotonic()
        expired_keys = [
            key for key, expires_at in self._recent_drop_submission_keys.items()
            if expires_at <= now
        ]
        for key in expired_keys:
            self._recent_drop_submission_keys.pop(key, None)

    def duplicate_drop_message(self, member: discord.Member, drop_name: str, reason: str = "recent") -> str:
        display_name = getattr(member, "display_name", "This player")
        if reason == "open":
            return (
                f"{display_name} already has **{drop_name}** open in Drop Verification. "
                "Please check Drop Verification before submitting again. Exact duplicate submissions create extra work and may be rejected."
            )
        if reason == "pending":
            return (
                f"{display_name} already has an auto-submit prompt open for **{drop_name}** in their team channel. "
                "Please use that prompt, or check Drop Verification before submitting again."
            )
        return (
            f"{display_name} recently submitted **{drop_name}**. "
            "Please check Drop Verification before submitting again. Exact duplicate submissions create extra work and may be rejected."
        )

    async def reserve_auto_drop_prompt(self, member: discord.Member, drop_name: str) -> tuple[bool, str]:
        """Reserve an auto-submit prompt before it is posted in a team channel.

        This blocks /submitdrop from submitting the same player/drop while the
        auto prompt is waiting.
        """
        key = self.get_open_drop_submission_key(member, drop_name)
        if not key:
            return True, ""

        async with self._drop_duplicate_lock:
            self.cleanup_recent_drop_keys()

            if key in self._open_drop_submission_keys:
                return False, self.duplicate_drop_message(member, drop_name, "open")
            if key in self._pending_auto_drop_keys:
                return False, self.duplicate_drop_message(member, drop_name, "pending")
            if key in self._recent_drop_submission_keys:
                return False, self.duplicate_drop_message(member, drop_name, "recent")

            self._pending_auto_drop_keys.add(key)
            return True, ""

    async def reserve_open_drop_submission(
        self,
        member: discord.Member,
        drop_name: str,
        *,
        allow_pending: bool = False,
    ) -> tuple[bool, str]:
        """Reserve a player/drop as being sent to Drop Verification.

        Blocks exact duplicates across auto-submit and /submitdrop using the
        same Discord user + same normalized drop name.
        """
        key = self.get_open_drop_submission_key(member, drop_name)
        if not key:
            return True, ""

        async with self._drop_duplicate_lock:
            self.cleanup_recent_drop_keys()

            if key in self._open_drop_submission_keys:
                return False, self.duplicate_drop_message(member, drop_name, "open")
            if key in self._recent_drop_submission_keys:
                return False, self.duplicate_drop_message(member, drop_name, "recent")
            if key in self._pending_auto_drop_keys and not allow_pending:
                return False, self.duplicate_drop_message(member, drop_name, "pending")

            self._pending_auto_drop_keys.discard(key)
            self._open_drop_submission_keys.add(key)
            self._recent_drop_submission_keys[key] = time.monotonic() + self.DROP_DUPLICATE_BLOCK_SECONDS
            return True, ""

    def clear_pending_auto_drop_prompt(self, member: discord.Member, drop_name: str) -> None:
        key = self.get_open_drop_submission_key(member, drop_name)
        if key:
            self._pending_auto_drop_keys.discard(key)

    def clear_open_drop_submission(self, member: discord.Member, drop_name: str) -> None:
        """Clear a player/drop once the review is no longer open.

        The recent-submission cooldown intentionally remains, so rapid exact
        duplicates stay blocked even right after approval/rejection.
        """
        key = self.get_open_drop_submission_key(member, drop_name)
        if key:
            self._open_drop_submission_keys.discard(key)
            self._pending_auto_drop_keys.discard(key)

    def should_skip_duplicate_auto_drop_prompt(self, target_user: discord.Member, drop_name: str) -> bool:
        """Return True if this player/drop already created a team prompt recently."""
        now = time.monotonic()

        expired_keys = [
            key for key, timestamp in self._auto_drop_recent_prompt_keys.items()
            if now - timestamp > self.AUTO_DROP_PROMPT_COOLDOWN_SECONDS
        ]
        for key in expired_keys:
            self._auto_drop_recent_prompt_keys.pop(key, None)

        key = self.get_open_drop_submission_key(target_user, drop_name)
        if not key:
            return False

        last_prompt_time = self._auto_drop_recent_prompt_keys.get(key)
        if last_prompt_time is not None and now - last_prompt_time <= self.AUTO_DROP_PROMPT_COOLDOWN_SECONDS:
            return True

        self._auto_drop_recent_prompt_keys[key] = now
        return False

    def should_skip_duplicate_open_notice(self, target_user: discord.Member, drop_name: str) -> bool:
        """Rate-limit 'already open' notices in team channels."""
        now = time.monotonic()

        expired_keys = [
            key for key, timestamp in self._auto_drop_recent_open_notice_keys.items()
            if now - timestamp > self.AUTO_DROP_OPEN_NOTICE_COOLDOWN_SECONDS
        ]
        for key in expired_keys:
            self._auto_drop_recent_open_notice_keys.pop(key, None)

        key = self.get_open_drop_submission_key(target_user, drop_name)
        if not key:
            return False

        last_notice_time = self._auto_drop_recent_open_notice_keys.get(key)
        if last_notice_time is not None and now - last_notice_time <= self.AUTO_DROP_OPEN_NOTICE_COOLDOWN_SECONDS:
            return True

        self._auto_drop_recent_open_notice_keys[key] = now
        return False

    def parse_player_name_from_drop_text(self, text: str) -> str:
        """Extract the RSN/player name from a detected Clan Chat drop message."""
        text = self.flatten_message_text(text) if not isinstance(text, str) else text
        text = text.replace("\\:", ":").replace("\\(", "(").replace("\\)", ")").strip()

        patterns = [
            r"^(?:<a?:[^:]+:\d+>\s*)?(?P<player>.+?)\s+received a drop:",
            r"^(?:<a?:[^:]+:\d+>\s*)?(?P<player>.+?)\s+received a new collection log item:",
            r"^(?P<player>.+?)\s+has a funny feeling like\s+",
            r"^(?:\[.*?\]\s*)?(?:<a?:[^:]+:\d+>\s*|[^\w\s]+\s*)?(?P<player>.+?)\s+received special loot from a raid:",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                player = str(match.group("player") or "").strip()
                player = re.sub(r"<a?:[^:]+:\d+>", "", player).strip()
                bold_match = re.search(r"\*\*(.+?)\*\*", player)
                if bold_match:
                    player = bold_match.group(1).strip()
                return player.replace("*", "").strip()

        return ""

    async def resolve_detected_drop_member(self, message: discord.Message, text: str) -> Optional[discord.Member]:
        """Resolve the Clan Chat RSN to a Discord member.

        Priority:
        1. RSN Tracker exact lookup.
        2. Exact normalized nickname/display-name segment match.
        3. Mentions/IDs fallback.
        """
        guild = message.guild
        if guild is None:
            return None

        player_rsn = self.parse_player_name_from_drop_text(text)
        normalized_player = self.normalize_rsn_for_lookup(player_rsn)

        if normalized_player:
            registered_info = self.find_registered_rsn_info(player_rsn)
            discord_id = str((registered_info or {}).get("discord_id", "")).strip()

            if discord_id.isdigit():
                try:
                    member = guild.get_member(int(discord_id)) or await guild.fetch_member(int(discord_id))
                    if member is not None:
                        print(
                            f"Bingo Cog: Resolved detected drop RSN '{player_rsn}' "
                            f"to Discord member {member.id} through RSN Tracker."
                        )
                        return member
                except Exception as e:
                    print(f"Bingo Cog: Could not fetch member for RSN '{player_rsn}' / Discord ID {discord_id}: {e}")

            # Fallback: exact match against nickname/name/global name pieces.
            # This handles names like "Hikizato | Hikis Donger".
            for member in getattr(guild, "members", []):
                if member.bot:
                    continue

                possible_names = {
                    str(getattr(member, "display_name", "") or ""),
                    str(getattr(member, "name", "") or ""),
                    str(getattr(member, "global_name", "") or ""),
                }

                expanded_parts = set()
                for name in possible_names:
                    expanded_parts.add(name)
                    expanded_parts.update(re.split(r"[|,/;\n\r]+", name))

                normalized_parts = {
                    self.normalize_rsn_for_lookup(part)
                    for part in expanded_parts
                    if self.normalize_rsn_for_lookup(part)
                }

                if normalized_player in normalized_parts:
                    print(
                        f"Bingo Cog: Resolved detected drop RSN '{player_rsn}' "
                        f"to Discord member {member.id} through exact name match."
                    )
                    return member

        for mentioned in message.mentions:
            if isinstance(mentioned, discord.Member) and not mentioned.bot:
                return mentioned

        id_match = re.search(r"<@!?(\d{15,22})>", text) or re.search(r"\b(\d{15,22})\b", text)
        if id_match:
            try:
                return guild.get_member(int(id_match.group(1))) or await guild.fetch_member(int(id_match.group(1)))
            except Exception:
                pass

        return None

    async def handle_detected_drop_message(self, message: discord.Message):
        if self.bot.user and message.author.id == self.bot.user.id:
            return

        async with self._auto_drop_prompt_lock:
            if message.id in self._auto_drop_prompted_message_ids:
                return
            self._auto_drop_prompted_message_ids.add(message.id)
            if len(self._auto_drop_prompted_message_ids) > 500:
                self._auto_drop_prompted_message_ids = set(list(self._auto_drop_prompted_message_ids)[-250:])

        text = self.flatten_message_text(message)
        drop_name = self.find_drop_name_in_text(text)
        if not drop_name:
            return

        target_user = await self.resolve_detected_drop_member(message, text)
        if target_user is None:
            print(f"Bingo Cog: Detected drop '{drop_name}' but could not resolve the player from message {message.id}.")
            return

        team_number = self.get_member_team_number(target_user)
        if team_number is None:
            print(
                f"Bingo Cog: Detected drop '{drop_name}' for "
                f"{target_user.display_name} ({target_user.id}), "
                "but they do not have a configured team role. "
                f"Roles: {[f'{role.name}:{role.id}' for role in getattr(target_user, 'roles', [])]}"
            )
            return

        team_channel_id = self.TEAM_CHANNEL_IDS.get(team_number)
        team_channel = await self.get_channel_by_id(team_channel_id) if team_channel_id else None
        if team_channel is None:
            return

        team_role_mention = f"<@&{self.TEAM_ROLE_IDS[team_number]}>"
        source_message_url = getattr(message, "jump_url", None) or f"https://discord.com/channels/{self.GUILD_ID}/{message.channel.id}/{message.id}"

        ok, duplicate_message = await self.reserve_auto_drop_prompt(target_user, drop_name)
        if not ok:
            if not self.should_skip_duplicate_open_notice(target_user, drop_name):
                await team_channel.send(
                    content=(
                        f"{team_role_mention}\n\n"
                        f"{target_user.mention}, {duplicate_message}\n\n"
                        f"*Chat submission link:* [Open message]({source_message_url})"
                    ),
                    allowed_mentions=discord.AllowedMentions(users=True, roles=True, everyone=False),
                )
            return

        if self.should_skip_duplicate_auto_drop_prompt(target_user, drop_name):
            self.clear_pending_auto_drop_prompt(target_user, drop_name)
            print(
                f"Bingo Cog: Skipped duplicate auto-drop prompt for "
                f"{target_user.display_name} / {drop_name} within "
                f"{self.AUTO_DROP_PROMPT_COOLDOWN_SECONDS}s."
            )
            return

        image_source = self.extract_image_url_from_message(message)
        image_url = image_source.image_url if image_source else ""
        boss_name = self.get_boss_for_drop(drop_name)

        print(
            "Bingo Cog: AUTO DROP PROMPT ONLY - "
            f"message={message.id}, team={team_number}, drop={drop_name}. "
            "No drop verification message was sent."
        )

        try:
            await team_channel.send(
                content=(
                    f"{team_role_mention}\n\n"
                    "**Drop Received!**\n\n"
                    f"{drop_name} for {target_user.mention}\n\n"
                    f"*Chat submission link:* [Open message]({source_message_url})\n\n"
                    "Select **Send Drop** below if you want to send this to Drop Verification.\n"
                    "Before pressing it, check Drop Verification to make sure this same drop is not already there.\n"
                    "Exact duplicate submissions create extra work and may be rejected."
                ),
                view=AutoDetectedDropConfirmView(
                cog=self,
                team_number=team_number,
                target_user=target_user,
                drop_name=drop_name,
                boss_name=boss_name,
                image_url=image_url,
                source_message_url=source_message_url,
                source_message_id=message.id,
                ),
                allowed_mentions=discord.AllowedMentions(users=True, roles=True, everyone=False),
            )
        except Exception as e:
            self.clear_pending_auto_drop_prompt(target_user, drop_name)
            print(f"Bingo Cog: Failed to send auto-drop team prompt: {e}")
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handle signup screenshots and auto-detected drop prompts."""
        if self.bot.user and message.author.id == self.bot.user.id:
            return

        channel_id = getattr(message.channel, "id", None)

        if channel_id == self.DROP_DETECTION_CHANNEL_ID:
            await self.handle_detected_drop_message(message)
            return

        if message.author.bot:
            return
        if channel_id != self.SIGNUP_CHANNEL_ID:
            return
        if message.author.id in self._pending_signup_screenshot_user_ids:
            return
        if self.extract_image_url_from_message(message) is None:
            return

        await self.send_incorrect_signup_image_dm(message.author)
        await self.safe_delete_message(message)

    def extract_image_url_from_message(self, message: discord.Message) -> Optional[MessageImageSource]:
        """Extract an image source from a message attachment or embed preview."""
        if message.attachments:
            attachment = message.attachments[0]
            if attachment.url:
                return MessageImageSource(attachment=attachment, image_url=attachment.url)

        for embed in message.embeds:
            embed_image = getattr(embed, "image", None)
            image_url = getattr(embed_image, "url", None) if embed_image else None
            if image_url:
                return MessageImageSource(attachment=None, image_url=image_url)

            embed_thumbnail = getattr(embed, "thumbnail", None)
            thumbnail_url = getattr(embed_thumbnail, "url", None) if embed_thumbnail else None
            if thumbnail_url:
                return MessageImageSource(attachment=None, image_url=thumbnail_url)

        return None

    def can_capture_signup_screenshots(self) -> bool:
        """Discord only sends attachment data to bots with Message Content Intent enabled."""
        return bool(getattr(self.bot.intents, "message_content", False))

    async def save_backup_signup(self, channel: discord.abc.Messageable, member: discord.Member, data: dict) -> None:
        """Save a backup signup immediately. Backups do not require buy-in screenshots."""
        member = await self.resolve_guild_member(channel, member)

        registered_info = self.find_registered_rsn_info(data.get("RSN", ""))
        if registered_info is None:
            print(f"Bingo Cog: Backup RSN not found in Tracker; using submitter identity: {data.get('RSN', '')}")

        if self.is_banned_event_participant(data.get("RSN", ""), str(member.id), registered_info):
            try:
                await channel.send(f"{member.mention}, {self.banned_signup_error_message()}", delete_after=45)
            except Exception:
                pass
            return

        registered_info = await self.enrich_registered_info_for_guild(channel, registered_info) if registered_info else None

        try:
            await self.add_auto_rank_to_signup_data(data, "RSN", "Rank", "Ironman")
            row = self.write_or_update_backup_to_sheet(member, data, registered_info=registered_info)
            await self.add_bingo_player_role_for_signup(member, data)
            await self.send_signup_completed_dm(member, row, "Backup", data.get("RSN", ""))

            names = await asyncio.to_thread(self.read_backup_names_from_sheet)
            self._backup_list_last_signature = "\n".join(names)
            await self.post_or_update_backup_list(names)

        except Exception as e:
            print(f"Bingo Cog: Failed while saving backup signup: {e}")
            try:
                await channel.send(
                    f"{member.mention}, something went wrong while saving your backup signup. Please contact an administrator.",
                    delete_after=25,
                )
            except Exception:
                pass

    async def collect_signup_screenshots(self, channel: discord.abc.Messageable, member: discord.Member, data: dict) -> None:
        """Wait for one required screenshot, then optionally a second duo screenshot."""
        member = await self.resolve_guild_member(channel, member)

        if not self.can_capture_signup_screenshots():
            try:
                await channel.send(
                    f"{member.mention}, I cannot detect screenshot uploads yet because the bot is missing Message Content Intent. "
                    "An administrator needs to enable it in the Discord Developer Portal and in the bot startup code.",
                    delete_after=30
                )
            except Exception:
                pass
            return

        signup_type = data.get("signup_type", "Solo")
        is_duo = signup_type == "Duo"
        is_captain = signup_type == "Captain"

        submitter_info = self.find_registered_rsn_info(data.get("RSN", ""))
        if submitter_info is None:
            print(f"Bingo Cog: RSN not found in Tracker for submitter; using submitter identity: {data.get('RSN', '')}")

        if self.is_banned_event_participant(data.get("RSN", ""), str(member.id), submitter_info):
            try:
                await channel.send(f"{member.mention}, {self.banned_signup_error_message()}", delete_after=45)
            except Exception:
                pass
            return

        submitter_info = await self.enrich_registered_info_for_guild(channel, submitter_info) if submitter_info else None

        def check(message: discord.Message) -> bool:
            return (
                message.author.id == member.id
                and message.channel.id == channel.id
                and self.extract_image_url_from_message(message) is not None
            )

        self._pending_signup_screenshot_user_ids.add(member.id)

        try:
            first_message = await self.bot.wait_for("message", check=check, timeout=600)
            first_source = self.extract_image_url_from_message(first_message)
            if first_source is None:
                raise ValueError("No valid image source found for first screenshot message.")
            first_url = first_source.image_url
            first_file = None
            first_filename = None
            if first_source.attachment is not None:
                first_file, first_filename = await self.attachment_to_discord_file(first_source.attachment, "buy_in.png")

            if not is_captain:
                await self.add_auto_rank_to_signup_data(data, "RSN", "Rank", "Ironman")
            submitter_row = self.write_or_update_signup_to_sheet(member, data, first_url, registered_info=submitter_info)
            data["_submitter_row"] = submitter_row
            data["_buyin_screenshot"] = first_url
            await self.send_signup_completed_dm(member, submitter_row, signup_type, data.get("RSN", ""))

            partner_info = None
            partner_row = None
            partner_file = None
            partner_filename = None

            if is_duo and str(data.get("Duo Partner", "")).strip():
                partner_info = self.find_registered_rsn_info(data.get("Duo Partner", ""))
                if partner_info is not None:
                    if self.is_banned_event_participant(data.get("Duo Partner", ""), "", partner_info):
                        try:
                            await channel.send(f"{member.mention}, {self.banned_signup_error_message()}", delete_after=45)
                        except Exception:
                            pass
                        return
                    partner_info = await self.enrich_registered_info_for_guild(channel, partner_info)
                else:
                    print(f"Bingo Cog: Duo partner RSN was not found in tracker while saving row: {data.get('Duo Partner', '')}")

                await self.add_auto_rank_to_signup_data(data, "Duo Partner", "Duo Rank", "Duo Ironman")
                partner_row = self.ensure_duo_partner_row(member, data, first_url, partner_info)
                data["_partner_row"] = partner_row
                await self.send_signup_completed_dm_by_registered_info(
                    getattr(channel, "guild", None),
                    partner_info,
                    partner_row,
                    "Duo",
                    data.get("Duo Partner", ""),
                )
                if first_source.attachment is not None:
                    partner_file, partner_filename = await self.attachment_to_discord_file(first_source.attachment, "partner_buy_in.png")

            await self.add_bingo_player_role_for_signup(
                member,
                data,
                partner_row=partner_row,
                partner_info=partner_info,
            )

            await self.send_signup_image_post(
                image_url=first_url,
                file=first_file,
                filename=first_filename,
                colour=discord.Colour.blue() if is_duo else (discord.Colour.gold() if is_captain else discord.Colour.green()),
            )

            await self.safe_delete_message(first_message)

            if not is_duo:
                return

            try:
                second_message = await self.bot.wait_for("message", check=check, timeout=20)
            except asyncio.TimeoutError:
                return

            second_source = self.extract_image_url_from_message(second_message)
            if second_source is None:
                raise ValueError("No valid image source found for second screenshot message.")
            second_url = second_source.image_url
            second_file = None
            second_filename = None
            if second_source.attachment is not None:
                second_file, second_filename = await self.attachment_to_discord_file(second_source.attachment, "partner_buy_in.png")
            self.update_duo_second_screenshot(submitter_row, partner_row, second_url)

            await self.send_signup_image_post(
                image_url=second_url,
                file=second_file,
                filename=second_filename,
                colour=discord.Colour.blue(),
            )

            partner_target = None
            partner_discord_id = str((partner_info or {}).get("discord_id", "")).strip()
            if partner_discord_id.isdigit():
                partner_target = f"<@{partner_discord_id}>"
            else:
                partner_rsn = str(data.get("Duo Partner", "")).strip()
                partner_target = partner_rsn or member.mention

            await self.safe_delete_message(second_message)

        except asyncio.TimeoutError:
            try:
                await channel.send(
                    f"{member.mention}, your signup timed out because no image upload or image link was posted.",
                    delete_after=20
                )
            except Exception:
                pass
        except Exception as e:
            print(f"Bingo Cog: Failed while collecting signup screenshots: {e}")
            try:
                await channel.send(
                    f"{member.mention}, something went wrong while saving your signup. Please contact an administrator.",
                    delete_after=25
                )
            except Exception:
                pass
        finally:
            self._pending_signup_screenshot_user_ids.discard(member.id)

    @app_commands.command(name="signup_panel", description="Post the bingo signup panel in this channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def signup_panel(self, interaction: discord.Interaction):
        if self.signup_sheet is None:
            await interaction.response.send_message(
                "Bingo signup system is not properly configured. Please contact an administrator.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="Bingo Signups",
            description=(
                "Press one of the buttons below to sign up for the Spring Bingo.\n\n"
                "**Solo Signup** - Sign up by yourself.\n"
                "**Duo Signup** - Sign up with a duo partner. Duo buy-ins must be matched to a duo partner to pair you.\n\n"
                "You may submit both buy-ins for yourself and your duo partner. "
                "Please make sure your RSN, playtime, timezone/location, and buy-in proof are accurate."
                "\n\n*note: Some players are banned from signing up if they were problematic in 2 or more events. If you planned on signing up with a banned player as a duo partner, you can still sign up solo or choose a different partner*"
            ),
            colour=discord.Colour.gold()
        )

        panel_message = await interaction.channel.send(embed=embed, view=BingoSignupPanelView(self))
        self.signup_panel_jump_url = panel_message.jump_url
        await interaction.response.send_message("Signup panel posted.", ephemeral=True)

    @signup_panel.error
    async def signup_panel_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "You need Administrator permission to post the signup panel.",
                ephemeral=True
            )
        else:
            raise error

    @app_commands.command(name="signup", description="Open the bingo signup buttons")
    async def signup(self, interaction: discord.Interaction):
        """Let users open signup buttons without scrolling back to the original panel."""
        if self.signup_sheet is None:
            await interaction.response.send_message(
                "Bingo signup system is not properly configured. Please contact an administrator.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "Choose a signup type below.",
            view=BingoSignupPanelView(self),
            ephemeral=True
        )


    @app_commands.command(name="signups", description="Show current signup totals")
    async def signups(self, interaction: discord.Interaction):
        if self.signup_sheet is None:
            await interaction.response.send_message(
                "Bingo signup system is not properly configured. Please contact an administrator.",
                ephemeral=True
            )
            return

        counts = await asyncio.to_thread(self.get_signup_counts)

        embed = self.build_signups_embed(counts)
        embed = discord.Embed(
            title="Current Bingo Signup Totals",
            colour=discord.Colour.gold()
        )
        embed.add_field(name="Solo Signups", value=str(counts["solo_count"]), inline=True)
        embed.add_field(name="Duo Signups", value=str(counts["duo_count"]), inline=True)
        embed.add_field(name="Total Signups", value=str(counts["total_count"]), inline=True)
        embed.add_field(name="Captains", value=str(counts["captain_count"]), inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=False)

    @app_commands.command(name="backup_list", description="Post or refresh the bingo backup list embed")
    @app_commands.checks.has_permissions(administrator=True)
    async def backup_list(self, interaction: discord.Interaction):
        if self.backups_sheet is None:
            await interaction.response.send_message(
                "Backups worksheet is not configured or could not be loaded.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)
        names = await asyncio.to_thread(self.read_backup_names_from_sheet)
        self._backup_list_last_signature = None

        await self.post_or_update_backup_list(names)
        self._backup_list_last_signature = "\n".join(names)
        await interaction.followup.send("Backup list posted/refreshed.", ephemeral=True)

    @backup_list.error
    async def backup_list_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "You need Administrator permission to refresh the backup list.",
                ephemeral=True
            )
        else:
            raise error

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


class BackupListView(discord.ui.View):
    def __init__(self, cog: BingoCog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(
        label="Sign Up as Backup",
        style=discord.ButtonStyle.green,
        custom_id="bingo_backup_signup:open",
    )
    async def backup_signup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.cog.backups_sheet is None:
            await interaction.response.send_message(
                "The backup signup sheet is not configured. Please contact an administrator.",
                ephemeral=True,
            )
            return

        if self.cog.is_banned_event_participant(discord_id=str(interaction.user.id)):
            await interaction.response.send_message(self.cog.banned_signup_error_message(), ephemeral=True)
            return

        await interaction.response.send_modal(BackupSignupModal(self.cog))


class BackupSignupModal(discord.ui.Modal, title="Backup Signup"):
    def __init__(self, cog: BingoCog):
        super().__init__()
        self.cog = cog

        self.rsn = discord.ui.TextInput(
            label="RSN",
            placeholder="The account you are signing up on.",
            required=True,
            max_length=50,
        )
        self.playtime = discord.ui.TextInput(
            label="Playtime",
            placeholder="Estimated playtime for the event duration. Please be accurate.",
            required=True,
            max_length=100,
        )
        self.timezone = discord.ui.TextInput(
            label="Timezone/Location",
            placeholder="Example: GMT, CST, AUS, South America, active hours, etc.",
            required=True,
            max_length=100,
        )
        self.comments = discord.ui.TextInput(
            label="Comments",
            placeholder="Anything you would like captains to know.",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=500,
        )
        self.ironman = discord.ui.TextInput(
            label="Ironman?",
            placeholder="Yes or No",
            required=True,
            max_length=25,
        )

        self.add_item(self.rsn)
        self.add_item(self.playtime)
        self.add_item(self.timezone)
        self.add_item(self.comments)
        self.add_item(self.ironman)

    async def on_submit(self, interaction: discord.Interaction):
        data = {
            "signup_type": "Backup",
            "RSN": str(self.rsn.value).strip(),
            "Playtime": str(self.playtime.value).strip(),
            "Timezone/Location": str(self.timezone.value).strip(),
            "Comments": str(self.comments.value).strip(),
            "Ironman": str(self.ironman.value).strip(),
            "_submitter_discord_id": str(interaction.user.id),
        }

        await interaction.response.defer(ephemeral=True, thinking=True)

        valid, error_message = await self.cog.validate_signup_rsns(interaction.channel, data)
        if not valid:
            await interaction.followup.send(error_message, ephemeral=True)
            return

        try:
            await self.cog.save_backup_signup(interaction.channel, interaction.user, data)
            await interaction.followup.send(
                "Your backup signup has been submitted.",
                ephemeral=True,
            )
        except Exception as e:
            print(f"Bingo Cog: Backup signup modal failed: {e}")
            await interaction.followup.send(
                "Something went wrong while saving your backup signup. Please contact an administrator.",
                ephemeral=True,
            )


class BingoSignupPanelView(discord.ui.View):
    def __init__(self, cog: BingoCog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(
        label="Solo Signup",
        style=discord.ButtonStyle.green,
        custom_id="bingo_signup:solo"
    )
    async def solo_signup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.cog.signup_panel_jump_url:
            self.cog.signup_panel_jump_url = interaction.message.jump_url
        if self.cog.is_banned_event_participant(discord_id=str(interaction.user.id)):
            await interaction.response.send_message(self.cog.banned_signup_error_message(), ephemeral=True)
            return
        await interaction.response.send_modal(SoloSignupModal(self.cog))

    @discord.ui.button(
        label="Duo Signup",
        style=discord.ButtonStyle.blurple,
        custom_id="bingo_signup:duo"
    )
    async def duo_signup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.cog.signup_panel_jump_url:
            self.cog.signup_panel_jump_url = interaction.message.jump_url
        if self.cog.is_banned_event_participant(discord_id=str(interaction.user.id)):
            await interaction.response.send_message(self.cog.banned_signup_error_message(), ephemeral=True)
            return
        await interaction.response.send_modal(DuoSignupPageOneModal(self.cog))

    @discord.ui.button(
        label="Captain Signup",
        style=discord.ButtonStyle.secondary,
        custom_id="bingo_signup:captain"
    )
    async def captain_signup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.cog.signup_panel_jump_url:
            self.cog.signup_panel_jump_url = interaction.message.jump_url
        if not self.cog.has_captain_signup_access(interaction.user):
            await interaction.response.send_message(
                "Only Event Staff, Clan Staff, Senior Staff, or Event Captains can use Captain Signup.",
                ephemeral=True,
            )
            return
        if self.cog.is_banned_event_participant(discord_id=str(interaction.user.id)):
            await interaction.response.send_message(self.cog.banned_signup_error_message(), ephemeral=True)
            return
        await interaction.response.send_modal(CaptainSignupModal(self.cog))


class CaptainSignupModal(discord.ui.Modal, title="Captain Signup - Step 1 of 2"):
    def __init__(self, cog: BingoCog):
        super().__init__()
        self.cog = cog

        self.rsn = discord.ui.TextInput(
            label="RSN",
            placeholder="The account you are signing up on.",
            required=True,
            max_length=50
        )
        self.playtime = discord.ui.TextInput(
            label="Playtime",
            placeholder="Estimated playtime for the event duration. Please be accurate.",
            required=True,
            max_length=100
        )
        self.timezone = discord.ui.TextInput(
            label="Timezone/Location",
            placeholder="Example: GMT, CST, AUS, South America, active hours, etc.",
            required=True,
            max_length=100
        )
        self.comments = discord.ui.TextInput(
            label="Comments",
            placeholder="Anything you would like captains to know.",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=500
        )
        self.ironman = discord.ui.TextInput(
            label="Ironman?",
            placeholder="Yes or No",
            required=True,
            max_length=25
        )

        self.add_item(self.rsn)
        self.add_item(self.playtime)
        self.add_item(self.timezone)
        self.add_item(self.comments)
        self.add_item(self.ironman)

    async def on_submit(self, interaction: discord.Interaction):
        if not self.cog.has_captain_signup_access(interaction.user):
            await interaction.response.send_message(
                "Only Event Staff, Clan Staff, Senior Staff, or Event Captains can use Captain Signup.",
                ephemeral=True,
            )
            return

        data = {
            "signup_type": "Captain",
            "RSN": str(self.rsn.value).strip(),
            "Playtime": str(self.playtime.value).strip(),
            "Timezone/Location": str(self.timezone.value).strip(),
            "Comments": str(self.comments.value).strip(),
            "Ironman": str(self.ironman.value).strip(),
            "Rank": "",
            "_submitter_discord_id": str(interaction.user.id),
        }

        await interaction.response.defer(ephemeral=True, thinking=True)

        valid, error_message = await self.cog.validate_signup_rsns(interaction.channel, data)
        if not valid:
            await interaction.followup.send(error_message, ephemeral=True)
            return

        if not self.cog.can_capture_signup_screenshots():
            await interaction.followup.send(
                "I saved your form information, but I cannot detect uploaded screenshots yet. "
                "The bot needs **Message Content Intent** enabled in the Discord Developer Portal and in the bot startup code. "
                "After that is enabled, run the signup again and post the screenshot after the prompt.",
                ephemeral=True
            )
            return

        await interaction.followup.send(
            "**Step 2/2: Post Buy In Screenshot**\n"
            "Post your buy-in screenshot in this channel now. "
            "If you want to link a co-captain, press **Optional: Enter Co-Captain ➔** before posting your screenshot.",
            view=CaptainCoCaptainView(self.cog, data),
            ephemeral=True
        )
        self.cog._pending_signup_screenshot_user_ids.add(interaction.user.id)
        asyncio.create_task(self.cog.collect_signup_screenshots(interaction.channel, interaction.user, data))


class CaptainCoCaptainView(discord.ui.View):
    def __init__(self, cog: BingoCog, data: dict):
        super().__init__(timeout=600)
        self.cog = cog
        self.data = data

    @discord.ui.button(label="Optional: Enter Co-Captain ➔", style=discord.ButtonStyle.secondary)
    async def enter_co_captain(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CaptainCoCaptainModal(self.cog, self.data))


class CaptainCoCaptainModal(discord.ui.Modal, title="Captain Signup - Co-Captain"):
    def __init__(self, cog: BingoCog, data: dict):
        super().__init__()
        self.cog = cog
        self.data = data

        self.co_captain = discord.ui.TextInput(
            label="Co-Captain",
            placeholder="Enter the co-captain name to link with this signup.",
            required=True,
            max_length=100,
        )
        self.add_item(self.co_captain)

    async def on_submit(self, interaction: discord.Interaction):
        co_captain = str(self.co_captain.value).strip()
        self.data["Co-Captain"] = co_captain

        await interaction.response.defer(ephemeral=True, thinking=True)

        row = self.data.get("_submitter_row")
        if row:
            try:
                self.cog.update_captain_co_captain(int(row), co_captain)
            except Exception as e:
                print(f"Bingo Cog: Failed to update captain co-captain field: {e}")

        await interaction.followup.send(
            f"Co-captain saved as **{co_captain}**. Post your buy-in screenshot when ready.",
            ephemeral=True,
        )


class SoloSignupModal(discord.ui.Modal, title="Solo Signup - Step 1 of 2"):
    def __init__(self, cog: BingoCog):
        super().__init__()
        self.cog = cog

        self.rsn = discord.ui.TextInput(
            label="RSN",
            placeholder="The account you are signing up on.",
            required=True,
            max_length=50
        )
        self.playtime = discord.ui.TextInput(
            label="Playtime",
            placeholder="Estimated playtime for the event duration. Please be accurate.",
            required=True,
            max_length=100
        )
        self.timezone = discord.ui.TextInput(
            label="Timezone/Location",
            placeholder="Example: GMT, CST, AUS, South America, active hours, etc.",
            required=True,
            max_length=100
        )
        self.comments = discord.ui.TextInput(
            label="Comments",
            placeholder="Anything you would like captains to know.",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=500
        )
        self.ironman = discord.ui.TextInput(
            label="Ironman?",
            placeholder="Yes or No",
            required=True,
            max_length=25
        )

        self.add_item(self.rsn)
        self.add_item(self.playtime)
        self.add_item(self.timezone)
        self.add_item(self.comments)
        self.add_item(self.ironman)

    async def on_submit(self, interaction: discord.Interaction):
        data = {
            "signup_type": "Solo",
            "RSN": str(self.rsn.value).strip(),
            "Playtime": str(self.playtime.value).strip(),
            "Timezone/Location": str(self.timezone.value).strip(),
            "Comments": str(self.comments.value).strip(),
            "Ironman": str(self.ironman.value).strip(),
            "_submitter_discord_id": str(interaction.user.id),
        }

        await interaction.response.defer(ephemeral=True, thinking=True)

        valid, error_message = await self.cog.validate_signup_rsns(interaction.channel, data)
        if not valid:
            await interaction.followup.send(error_message, ephemeral=True)
            return

        if not self.cog.can_capture_signup_screenshots():
            await interaction.followup.send(
                "I saved your form information, but I cannot detect uploaded screenshots yet. "
                "The bot needs **Message Content Intent** enabled in the Discord Developer Portal and in the bot startup code. "
                "After that is enabled, run the signup again and post the screenshot after the prompt.",
                ephemeral=True
            )
            return

        await interaction.followup.send(
            "**Step 2/2: Post Buy In Screenshot**\n"
            "Post your buy-in screenshot in this channel now. "
            "I will save it, delete your screenshot message, and DM you when your signup is complete.",
            ephemeral=True
        )
        self.cog._pending_signup_screenshot_user_ids.add(interaction.user.id)
        asyncio.create_task(self.cog.collect_signup_screenshots(interaction.channel, interaction.user, data))


class DuoSignupPageOneModal(discord.ui.Modal, title="Duo Signup - Page 1 of 2"):
    def __init__(self, cog: BingoCog):
        super().__init__()
        self.cog = cog

        self.rsn = discord.ui.TextInput(
            label="RSN",
            placeholder="The account you are signing up on.",
            required=True,
            max_length=50
        )
        self.playtime = discord.ui.TextInput(
            label="Playtime",
            placeholder="Your estimated playtime for the event duration.",
            required=True,
            max_length=100
        )
        self.timezone = discord.ui.TextInput(
            label="Timezone/Location",
            placeholder="Example: GMT, CST, AUS, South America, active hours, etc.",
            required=True,
            max_length=100
        )
        self.comments = discord.ui.TextInput(
            label="Comments",
            placeholder="Anything you would like captains to know.",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=500
        )
        self.ironman = discord.ui.TextInput(
            label="Ironman?",
            placeholder="Yes or No",
            required=True,
            max_length=25
        )

        self.add_item(self.rsn)
        self.add_item(self.playtime)
        self.add_item(self.timezone)
        self.add_item(self.comments)
        self.add_item(self.ironman)

    async def on_submit(self, interaction: discord.Interaction):
        data = {
            "signup_type": "Duo",
            "RSN": str(self.rsn.value).strip(),
            "Playtime": str(self.playtime.value).strip(),
            "Timezone/Location": str(self.timezone.value).strip(),
            "Comments": str(self.comments.value).strip(),
            "Ironman": str(self.ironman.value).strip(),
            "_submitter_discord_id": str(interaction.user.id),
        }

        await interaction.response.defer(ephemeral=True, thinking=True)

        valid, error_message = await self.cog.validate_signup_rsns(interaction.channel, data)
        if not valid:
            await interaction.followup.send(error_message, ephemeral=True)
            return

        if not self.cog.can_capture_signup_screenshots():
            await interaction.followup.send(
                "I saved your form information, but I cannot detect uploaded screenshots yet. "
                "The bot needs **Message Content Intent** enabled in the Discord Developer Portal and in the bot startup code. "
                "After that is enabled, run the signup again and post the screenshot after the prompt.",
                ephemeral=True
            )
            return

        await interaction.followup.send(
            "**Step 2/2: Post Buy In Screenshot**\n"
            "Post an image of your buy-in in this channel now to complete your signup. "
            "If you are also signing up your duo partner, press **Optional: Page 2 ➜** before posting your screenshot.",
            view=DuoContinueSignupView(self.cog, data),
            ephemeral=True
        )
        self.cog._pending_signup_screenshot_user_ids.add(interaction.user.id)
        asyncio.create_task(self.cog.collect_signup_screenshots(interaction.channel, interaction.user, data))


class DuoContinueSignupView(discord.ui.View):
    def __init__(self, cog: BingoCog, data: dict):
        super().__init__(timeout=600)
        self.cog = cog
        self.data = data

    @discord.ui.button(label="Optional: Page 2 ➜", style=discord.ButtonStyle.blurple)
    async def continue_to_page_two(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DuoSignupPageTwoModal(self.cog, self.data))


class DuoSignupPageTwoModal(discord.ui.Modal, title="Duo Signup - Page 2 of 2"):
    def __init__(self, cog: BingoCog, data: dict):
        super().__init__()
        self.cog = cog
        self.data = data

        self.duo_partner = discord.ui.TextInput(
            label="Duo RSN",
            placeholder="The RSN of your duo partner.",
            required=True,
            max_length=50
        )
        self.duo_playtime = discord.ui.TextInput(
            label="Duo Playtime",
            placeholder="Your partner's estimated playtime for the event duration.",
            required=True,
            max_length=100
        )
        self.duo_timezone = discord.ui.TextInput(
            label="Duo Timezone",
            placeholder="Your partner's timezone/location or active hours.",
            required=True,
            max_length=100
        )
        self.duo_ironman = discord.ui.TextInput(
            label="Duo Ironman Status",
            placeholder="Yes or No",
            required=True,
            max_length=25
        )

        self.add_item(self.duo_partner)
        self.add_item(self.duo_playtime)
        self.add_item(self.duo_timezone)
        self.add_item(self.duo_ironman)

    async def on_submit(self, interaction: discord.Interaction):
        self.data.update({
            "Duo Partner": str(self.duo_partner.value).strip(),
            "Duo Playtime": str(self.duo_playtime.value).strip(),
            "Duo Timezone/Location": str(self.duo_timezone.value).strip(),
            "Duo Ironman": str(self.duo_ironman.value).strip(),
        })

        await interaction.response.defer(ephemeral=True, thinking=True)

        valid, error_message = await self.cog.validate_signup_rsns(interaction.channel, self.data)
        if not valid:
            await interaction.followup.send(error_message, ephemeral=True)
            return

        buyin_screenshot = str(self.data.get("_buyin_screenshot", "")).strip()
        if buyin_screenshot:
            try:
                partner_info = self.cog.find_registered_rsn_info(self.data.get("Duo Partner", ""))
                if partner_info is not None:
                    partner_info = await self.cog.enrich_registered_info_for_guild(interaction.channel, partner_info)
                await self.cog.add_auto_rank_to_signup_data(self.data, "RSN", "Rank", "Ironman")
                await self.cog.add_auto_rank_to_signup_data(self.data, "Duo Partner", "Duo Rank", "Duo Ironman")
                submitter_info = self.cog.find_registered_rsn_info(self.data.get("RSN", ""))
                if submitter_info is not None:
                    submitter_info = await self.cog.enrich_registered_info_for_guild(interaction.channel, submitter_info)
                submitter_row = self.cog.write_or_update_signup_to_sheet(interaction.user, self.data, buyin_screenshot, registered_info=submitter_info)
                partner_row = self.cog.ensure_duo_partner_row(interaction.user, self.data, buyin_screenshot, partner_info)
                guild_member = await self.cog.resolve_guild_member(interaction.channel, interaction.user)
                await self.cog.add_bingo_player_role_for_signup(
                    guild_member,
                    self.data,
                    partner_row=partner_row,
                    partner_info=partner_info,
                )
                self.data["_submitter_row"] = submitter_row
                self.data["_partner_row"] = partner_row
                await interaction.followup.send(
                    f"Partner details saved and added to signup row {partner_row}.",
                    ephemeral=True
                )
            except Exception as e:
                print(f"Bingo Cog: Failed to update optional duo partner details: {e}")
                await interaction.followup.send(
                    "Partner details were saved, but I could not update the sheet. Please contact an administrator.",
                    ephemeral=True
                )
            return

        await interaction.followup.send(
            "Partner details saved. Now post an image of your buy-in in this channel to complete the signup. "
            "One screenshot is fine if it shows both buy-ins.",
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


class AutoDetectedDropConfirmView(discord.ui.View):
    def __init__(
        self,
        cog: BingoCog,
        team_number: int,
        target_user: discord.Member,
        drop_name: str,
        boss_name: str,
        image_url: str,
        source_message_url: str,
        source_message_id: int = 0,
    ):
        super().__init__(timeout=86400)
        self.cog = cog
        self.team_number = team_number
        self.target_user = target_user
        self.drop_name = drop_name
        self.boss_name = boss_name
        self.image_url = image_url
        self.source_message_url = source_message_url
        self.source_message_id = int(source_message_id or 0)
        self.completed = False

    def is_team_member(self, member: discord.Member) -> bool:
        return any(role.id == self.cog.TEAM_ROLE_IDS.get(self.team_number) for role in getattr(member, "roles", []))

    async def guard_team_member(self, interaction: discord.Interaction) -> bool:
        if self.is_team_member(interaction.user):
            return True
        await interaction.response.send_message(
            "Only a member of this team can answer this drop prompt.",
            ephemeral=True,
        )
        return False

    def disable_buttons(self) -> None:
        for child in self.children:
            child.disabled = True

    def build_review_embed(self, submitting_user: discord.abc.User) -> discord.Embed:
        title = f"{self.boss_name} Drop Submission" if self.boss_name else "Drop Submission"
        embed = discord.Embed(title=title, colour=discord.Colour.blurple())
        embed.add_field(name="Submitted For", value=f"{self.target_user.mention} ({self.target_user.id})", inline=False)
        embed.add_field(name="Drop Received", value=self.drop_name, inline=False)
        embed.add_field(name="Submitted By", value=f"{submitting_user.mention} ({submitting_user.id})", inline=False)
        embed.add_field(name="Source Message", value=f"[Open drop message]({self.source_message_url})", inline=False)
        if self.image_url:
            embed.set_image(url=self.image_url)
        return embed

    @discord.ui.button(label="Send Drop", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.guard_team_member(interaction):
            return
        if self.completed:
            await interaction.response.send_message("This drop prompt has already been answered.", ephemeral=True)
            return

        ok, duplicate_message = await self.cog.reserve_open_drop_submission(
            self.target_user,
            self.drop_name,
            allow_pending=True,
        )
        if not ok:
            await interaction.response.send_message(duplicate_message, ephemeral=True)
            return

        if self.source_message_id and self.source_message_id in self.cog._auto_drop_review_submitted_message_ids:
            self.cog.clear_open_drop_submission(self.target_user, self.drop_name)
            await interaction.response.send_message(
                "This detected drop has already been submitted to drop verification.",
                ephemeral=True,
            )
            return

        if self.source_message_id:
            self.cog._auto_drop_review_submitted_message_ids.add(self.source_message_id)

        review_channel = await self.cog.get_channel_by_id(self.cog.REVIEW_CHANNEL_ID)
        if review_channel is None:
            if self.source_message_id:
                self.cog._auto_drop_review_submitted_message_ids.discard(self.source_message_id)
            self.cog.clear_open_drop_submission(self.target_user, self.drop_name)
            await interaction.response.send_message(
                "I could not send this to the drop verification channel. Please use `/submitdrop` instead.",
                ephemeral=True,
            )
            return

        print(
            "Bingo Cog: Send Drop CLICKED - sending to drop verification "
            f"message={self.source_message_id}, drop={self.drop_name}, clicked_by={interaction.user.id}."
        )

        team_mention = self.cog.get_team_role_mention(self.target_user)
        embed = self.build_review_embed(interaction.user)
        try:
            await review_channel.send(
                embed=embed,
                view=DropReviewButtons(
                    self.cog,
                    self.target_user,
                    self.drop_name,
                    self.image_url,
                    interaction.user,
                    team_mention,
                    evidence_url=self.source_message_url,
                ),
            )
        except Exception as e:
            if self.source_message_id:
                self.cog._auto_drop_review_submitted_message_ids.discard(self.source_message_id)
            self.cog.clear_open_drop_submission(self.target_user, self.drop_name)
            print(f"Bingo Cog: Failed to send auto-detected drop to review channel: {e}")
            await interaction.response.send_message(
                "I could not send this to the drop verification channel. Please use `/submitdrop` instead.",
                ephemeral=True,
            )
            return

        self.completed = True
        self.disable_buttons()
        team_role_mention = f"<@&{self.cog.TEAM_ROLE_IDS[self.team_number]}>"
        await interaction.response.edit_message(
            content=(
                f"{team_role_mention}\n\n"
                "**Drop Received!**\n\n"
                f"{self.drop_name} for {self.target_user.mention}\n\n"
                f"*Chat submission link:* [Open message]({self.source_message_url})\n\n"
                f"Submitted to Drop Verification by {interaction.user.mention}.\n\n"
                "Please do not submit this same drop again unless it is a separate drop."
            ),
            view=self,
            allowed_mentions=discord.AllowedMentions(users=True, roles=True, everyone=False),
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.guard_team_member(interaction):
            return
        if self.completed:
            await interaction.response.send_message("This drop prompt has already been answered.", ephemeral=True)
            return

        self.completed = True
        self.cog.clear_pending_auto_drop_prompt(self.target_user, self.drop_name)
        self.disable_buttons()
        team_role_mention = f"<@&{self.cog.TEAM_ROLE_IDS[self.team_number]}>"
        await interaction.response.edit_message(
            content=(
                f"{team_role_mention}\n\n"
                "**Drop Received!**\n\n"
                f"{self.drop_name} for {self.target_user.mention}\n\n"
                f"*Chat submission link:* [Open message]({self.source_message_url})\n\n"
                "Not submitted. Please use `/submitdrop` only if this is not already in Drop Verification."
            ),
            view=self,
            allowed_mentions=discord.AllowedMentions(users=True, roles=True, everyone=False),
        )

    async def on_timeout(self):
        self.cog.clear_pending_auto_drop_prompt(self.target_user, self.drop_name)
        self.disable_buttons()


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

        ok, duplicate_message = await self.cog.reserve_open_drop_submission(self.target_user, drop_name)
        if not ok:
            await interaction.response.edit_message(
                content=duplicate_message,
                embed=None,
                view=None,
            )
            return

        embed = discord.Embed(title=f"{self.boss} Drop Submission", colour=discord.Colour.blurple())
        embed.add_field(name="Submitted For", value=f"{self.target_user.mention} ({self.target_user.id})", inline=False)
        embed.add_field(name="Drop Received", value=drop_name, inline=False)
        embed.add_field(name="Submitted By", value=f"{self.submitting_user.mention} ({self.submitting_user.id})", inline=False)
        embed.set_image(url=self.screenshot.url)

        await interaction.response.edit_message(content="Submitted for review.", embed=embed, view=None)

        if review_channel:
            team_mention = self.cog.get_team_role_mention(self.target_user)
            try:
                await review_channel.send(
                    embed=embed,
                    view=DropReviewButtons(self.cog, self.target_user, drop_name, self.screenshot.url, self.submitting_user, team_mention)
                )
            except Exception as e:
                self.cog.clear_open_drop_submission(self.target_user, drop_name)
                print(f"Bingo Cog: Failed to send manual drop to review channel: {e}")
        else:
            self.cog.clear_open_drop_submission(self.target_user, drop_name)



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
    def __init__(
        self,
        cog: BingoCog,
        submitted_user: discord.Member,
        drop: str,
        image_url: str,
        submitting_user: discord.Member,
        team_mention: str,
        evidence_url: Optional[str] = None,
    ):
        super().__init__(timeout=None)
        self.cog = cog
        self.submitted_user = submitted_user
        self.drop = drop
        self.image_url = image_url
        self.submitting_user = submitting_user
        self.team_mention = team_mention
        self.evidence_url = evidence_url or image_url
        self.reviewer: Optional[int] = None
        self.open_submission_key = self.cog.get_open_drop_submission_key(self.submitted_user, self.drop)

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

        log_channel = self.cog.bot.get_channel(self.cog.LOG_CHANNEL_ID)
        if log_channel:
            try:
                embed = discord.Embed(title="Drop Approved", colour=discord.Colour.green())
                embed.add_field(name="Approved By", value=interaction.user.display_name, inline=False)
                embed.add_field(name="Drop For", value=self.submitted_user.mention, inline=False)
                embed.add_field(name="Team", value=self.team_mention, inline=False)
                embed.add_field(name="Drop", value=self.drop, inline=False)
                embed.add_field(name="Submitted By", value=self.submitting_user.mention, inline=False)
                if self.image_url:
                    embed.set_image(url=self.image_url)
                if self.evidence_url and self.evidence_url != self.image_url:
                    embed.add_field(name="Chat Submission Link", value=f"[Open message]({self.evidence_url})", inline=False)
                await log_channel.send(embed=embed)
            except Exception as e:
                print(f"Bingo Cog: Failed to send to log channel: {e}")
                errors.append("Failed to log to channel")
        else:
            errors.append("Log channel not found")

        try:
            self.cog.log_approved_drop_to_sheet(
                reviewer_name=interaction.user.display_name,
                submitted_user_name=self.submitted_user.display_name,
                submitted_user_id=self.submitted_user.id,
                drop=self.drop,
                image_url=self.evidence_url,
            )
        except Exception as e:
            print(f"Bingo Cog: Failed to write drop log row: {e}")
            errors.append("Failed to log to spreadsheet")

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

        # This review is no longer open, so allow the same player/drop again.
        self.cog.clear_open_drop_submission(self.submitted_user, self.drop)

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

        try:
            self.cog.clear_open_drop_submission(self.parent_view.submitted_user, self.parent_view.drop)
        except Exception as e:
            print(f"Bingo Cog: Failed to clear open drop submission after rejection: {e}")

        try:
            await asyncio.sleep(1)
            await self.message.delete()
        except Exception as e:
            print(f"Bingo Cog: Failed to delete rejected review message: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(BingoCog(bot))
