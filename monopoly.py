import os
import discord
from discord.ext import commands
import gspread
from gspread.utils import rowcol_to_a1
from google.oauth2.service_account import Credentials
from datetime import datetime, timezone
import json
import asyncio
import math
import random
import traceback
from discord.ui import Modal, TextInput
from discord import app_commands, ui, Interaction, Member, TextStyle
from typing import List, Optional
from discord import ui, Interaction, Member
from typing import Optional
from discord import SelectOption, Attachment
from discord import ui, Interaction, SelectOption, TextStyle, Attachment, Member

# ========== CONFIG ==========
SPREADSHEET_ID = "1OVC8HImUpoh2keU-h2v_b2gFDa4zyfWsaJxBWRoSJ08"
SIGNUP_SPREADSHEET_ID = "1c7TzXlyn8KinCKNJadIBfY_6PcXF-9icbfC_E8NAGqI"
TEAM_ROLES = ["Team 1", "Team 2", "Team 3", "Team 4", "Team 5", "Team 6", "Team 7"]

REVIEW_CHANNEL = "1436465463742824499"
LOG_CHANNEL = "1436463720401211474"
GAME_LOG_CHANNEL_ID = 1477197002499690516
GAME_LOG_TEAM_COLOR_MAP = {
    "Team 1": 0xE74C3C,  # Red
    "Team 2": 0x9B59B6,  # Purple
    "Team 3": 0xF1C40F,  # Yellow
    "Team 4": 0x2ECC71,  # Green
    "Team 5": 0x00BCD4,  # Cyan
    "Team 6": 0xC4A484,  # Light Brown
    "Team 7": 0x3498DB,  # Blue
}


TEAM_CHANNELS_MAP = {
    "Team 1": 1436460767145754845,
    "Team 2": 1437851582183248113,
    "Team 3": 1437850674233872384,
    "Team 4": 1437851273113112707,
    "Team 5": 1437851747035910295,
    "Team 6": 1476784856028414074,
    "Team 7": 1476784946315002000
}
TEAM_CHANNEL_IDS_AS_STR = [str(cid) for cid in TEAM_CHANNELS_MAP.values()]

TEAM_REQUEST_CHANNEL_ID = 1477919745176109220
ACTIVE_TEAMS = ["Team 1", "Team 2", "Team 3"]
TEAM_LIST_CONFIG_FILE = "team_list_config.json"

SIGNUP_LIST_CONFIG_FILE = "signup_list_config.json"

EVENT_STAFF_ROLE_ID = 1286238788716199952
EVENT_CAPTAIN_ROLE_ID = 1286238713210474559
BINGO_PLAYER_ROLE_ID = 1464304452059267208

BOARD_SIZE = 40

# ========== CARD EMOJI MAPPING ==========
CARD_EMOJIS = {
    "Escape Crystal": "<:dragonstone:1437979925863862363>", 
    "Pickpocket": "<:thieving:1437980167791448237>",
    "Low Alchemy": "<:gold:1406230459301630043>",
    "High Alchemy": "<:MaxCash:1347684049040183427>",
    "Vengeance": "<:venge:1438084953559797884>",
    "Redemption": "<:redemption:1437979567900987493>",
    "Elder Maul": "<:maul:1437979898865258668>",
    "Vile Vigour": "<:agility:1437979594257993778>",
    "Varrock Tele": "<:varrocktele:1438084982491840583>",
    "POH Voucher": "<:houseicon:1438085020156821555>",
    "Home Tele": "<:housetele:1437980013831131206>",
    "Dragon Spear": "<:dragonspear:1437980060567994399>",
    "Rogue's Gloves": "<:rogue_gloves:1437980096790134914>",
    "Lure": "<:fishing:1437980297017688114>",
    "Backstab": "<:boner:1438085053102948383>",
    "Smite": "<:smite:1437979867084881950>",
    "Tele Other": "<:teleother:1437980130407350375>",
    "Tele Block": "<:teleblock:1438088930816819271>",
    "Chest": "<:chest:1437979807362191441>",
    "Chance": "<:questioning:1287623035381350441>"
}

GO_TILE = 0
JAIL_TILE = 10
BANK_STANDING_TILE = 20

CHEST_TILES = {2, 17, 33}
CHANCE_TILES = {7, 22, 36}
GLIDER_TILES = {12, 28, 38}

ROLL_GRANTING_TILES = {GO_TILE, BANK_STANDING_TILE} | GLIDER_TILES | CHEST_TILES | CHANCE_TILES

# ---------------------------
# 🔹 Boss-Drop Mapping
# ---------------------------
boss_drops = {
    "Araxxor": ["Noxious pommel", "Noxious point", "Noxious blade", "Araxyte fang", "Araxyte head", "Jar of venom", "Nid"],
    "Barrows": ["Ahrim's hood", "Ahrim's robetop", "Ahrim's robeskirt", "Ahrim's staff", "Karil's coif", "Karil's leathertop", "Karil's leatherskirt", "Karil's crossbow", "Dharok's helm", "Dharok's platebody", "Dharok's platelegs", "Dharok's greataxe", "Guthan's helm", "Guthan's platebody", "Guthan's chainskirt", "Guthan's warspear", "Torag's helm", "Torag's platebody", "Torag's platelegs", "Torag's hammers", "Verac's helm", "Verac's brassard", "Verac's plateskirt", "Verac's flail"],
    "Callisto": ["Callisto cub", "Tyrannical ring", "Dragon pickaxe", "Dragon 2h sword", "Claws of callisto", "Voidwaker hilt"],
    "Cerberus": ["Hellpuppy", "Eternal crystal", "Pegasian crystal", "Primordial crystal", "Jar of souls", "Smouldering stone"],
    "Chaos Fanatic": ["Pet chaos elemental", "Odium shard 1", "Malediction shard 1"],
    "Chambers of Xeric": ["Dexterous prayer scroll", "Arcane prayer scroll", "Twisted buckler", "Dragon hunter crossbow", "Dinh's bulwark", "Ancestral hat", "Ancestral robe top", "Ancestral robe bottom", "Dragon claws", "Elder maul", "Kodai insignia", "Twisted bow", "Olmlet", "Twisted ancestral colour kit", "Metamorphic dust"],
    "Colosseum": ["Dizana's quiver (uncharged)", "Sunfire fanatic cuirass", "Sunfire fanatic chausses", "Sunfire fanatic helm", "Echo crystal", "Tonalztics of ralos (uncharged)"],
    "Commander Zilyana": ["Pet zilyana", "Armadyl crossbow", "Saradomin hilt", "Saradomin sword", "Saradomin's light"],
    "Crazy Archaeologist": ["Odium shard 2", "Malediction shard 2", "Fedora"],
    "Doom of Mokhaiotl": ["Dom", "Avernic treads", "Eye of ayak (uncharged)", "Mokhaiotl cloth"],
    "Duke Sucellus": ["Baron", "Virtus mask", "Virtus robe top", "Virtus robe bottom", "Chromium ingot", "Magus vestige", "Eye of the duke", "Ice quartz"],
    "Gauntlet": ["Youngllef", "Crystal weapon seed", "Crystal armour seed", "Enhanced crystal weapon seed"],
    "General Graardor": ["Pet general graardor", "Bandos hilt", "Bandos chestplate", "Bandos tassets", "Bandos boots"],
    "Hueycoatl": ["Huberte", "Dragon hunter wand", "Hueycoatl hide", "Tome of earth (empty)"],
    "Kree'arra": ["Pet kree'arra", "Armadyl helmet", "Armadyl chestplate", "Armadyl chainskirt", "Armadyl hilt"],
    "K'ril Tsutsaroth": ["Pet K'ril Tsutsaroth", "Zamorakian spear", "Staff of the dead", "Zamorak hilt", "Steam battlestaff"],
    "Moons of Peril": ["Eclipse atlatl", "Eclipse moon helm", "Eclipse moon chestplate", "Eclipse moon tassets", "Dual macuahuitl", "Blood moon helm", "Blood moon chestplate", "Blood moon tassets", "Blue moon spear", "Blue moon helm", "Blue moon chestplate", "Blue moon tassets"],
    "Nightmare": ["Little nightmare", "Nightmare staff", "Inquisitor's great helm", "Inquisitor's hauberk", "Inquisitor's plateskirt", "Inquisitor's mace", "Eldritch orb", "Harmonised orb", "Volatile orb", "Parasitic egg", "Jar of dreams", "Slepey tablet"],
    "Nex": ["Nexling", "Ancient hilt", "Nihil horn", "Zaryte vambraces", "Torva full helm (damaged)", "Torva platebody (damaged)", "Torva platelegs (damaged)"],
    "Phantom Muspah": ["Muphin", "Venator shard", "Ancient icon"],
    "Scorpia": ["Scorpia's Offspring", "Malediction shard 3", "Odium shard 3"],
    "The Leviathan": ["Lil'viathan", "Virtus mask", "Virtus robe top", "Virtus robe bottom", "Chromium ingot", "Venator vestige", "Leviathan's lure", "Smoke quartz"],
    "The Whisperer": ["Wisp", "Virtus mask", "Virtus robe top", "Virtus robe bottom", "Chromium ingot", "Bellator vestige", "Siren's staff", "Shadow quartz"],
    "Theatre of Blood": ["Lil' zik", "Avernic defender hilt", "Ghrazi rapier", "Sanguinesti staff (uncharged)", "Justiciar faceguard", "Justiciar chestguard", "Justiciar legguards", "Scythe of vitur (uncharged)", "Holy ornament kit", "Sanguine ornament kit", "Sanguine dust"],
    "Tombs of Amascut": ["Tumeken's Guardian", "Masori mask", "Masori body", "Masori chaps", "Lightbearer", "Osmumten's fang", "Elidinis' ward", "Tumeken's shadow (uncharged)", "Cursed phalanx"],
    "Vardorvis": ["Butch", "Virtus mask", "Virtus robe top", "Virtus robe bottom", "Chromium ingot", "Ultor vestige", "Executioner's axe head", "Blood quartz"],
    "Venenatis": ["Venenatis spiderling", "Fangs of venenatis", "Dragon 2h sword", "Dragon pickaxe", "Voidwaker gem", "Treasonous ring"],
    "Vet'ion": ["Vet'ion jr.", "Skull of vet'ion", "Dragon 2h sword", "Dragon pickaxe", "Voidwaker blade", "Ring of the gods", "Skeleton champion scroll"],
    "Yama": ["Soulflame horn", "Oathplate helm", "Oathplate chest", "Oathplate legs"],
    "Zulrah": ["Pet snakeling", "Tanzanite mutagen", "Magma mutagen", "Jar of swamp", "Tanzanite fang", "Magic fang", "Serpentine visage", "Uncut onyx"]
}

# ========== COG CLASS ==========
class MonopolyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.signup_sheet = None
        self.signup_sheet_book = None
        
        required_env_vars = [
            'EVENT_TYPE', 'EVENT_PROJECT_ID', 'EVENT_PRIVATE_KEY_ID', 
            'EVENT_PRIVATE_KEY', 'EVENT_CLIENT_EMAIL', 'EVENT_CLIENT_ID', 
            'EVENT_AUTH_URI', 'EVENT_TOKEN_URI', 'EVENT_AUTH_PROVIDER_X509_CERT_URL', 
            'EVENT_CLIENT_X509_CERT_URL', 'EVENT_UNIVERSE_DOMAIN'
        ]
        
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            print("❌ FATAL ERROR: The following required environment variables are missing:")
            for var in missing_vars:
                print(f"- {var}")
            print("Monopoly Cog will not load.")
            return

        print("✅ Monopoly Cog: All required environment variables are present.")

        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        private_key_env = os.getenv('EVENT_PRIVATE_KEY')
        if not private_key_env:
            print("❌ FATAL ERROR: 'EVENT_PRIVATE_KEY' environment variable is not set.")
            private_key_formatted = None
        else:
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
        
        try:
            creds = Credentials.from_service_account_info(credentials_dict, scopes=scope)
            sheet_client = gspread.authorize(creds)
            
            sheet = sheet_client.open_by_key(SPREADSHEET_ID)

            print("Attempting to load worksheets...")
            self.command_log = sheet.worksheet("Command Log")
            print("... loaded Command Log")
            self.team_data_sheet = sheet.worksheet("TeamData")
            print("... loaded TeamData")
            self.chest_sheet = sheet.worksheet("ChestCards")
            print("... loaded ChestCards")
            self.chance_sheet = sheet.worksheet("ChanceCards")
            print("... loaded ChanceCards")
            self.drop_log_sheet = sheet.worksheet("DropLog")
            print("... loaded DropLog")
            self.item_values_sheet = sheet.worksheet("ItemValues")
            print("... loaded ItemValues")
            self.house_data_sheet = sheet.worksheet("HouseData")
            print("... loaded HouseData")
            
            print("✅ Monopoly Cog: Google Sheets initialized.")

            # Signup spreadsheet is optional for Monopoly gameplay; load separately so failures here
            # don't stop the event bot from running.
            try:
                self.signup_sheet_book = sheet_client.open_by_key(SIGNUP_SPREADSHEET_ID)
                try:
                    self.signup_sheet = self.signup_sheet_book.worksheet("Signups")
                    print("... loaded Signups worksheet (signup sheet)")
                except gspread.exceptions.WorksheetNotFound:
                    self.signup_sheet = self.signup_sheet_book.sheet1
                    print(f"... loaded signup sheet first worksheet: {self.signup_sheet.title}")
                print("✅ Signup sheet initialized.")
            except Exception as signup_err:
                self.signup_sheet = None
                self.signup_sheet_book = None
                print(f"⚠️ Signup sheet not initialized yet: {signup_err}")

        except gspread.exceptions.SpreadsheetNotFound:
            print(f"❌ FATAL ERROR: Spreadsheet with ID '{SPREADSHEET_ID}' not found.")
        except gspread.exceptions.WorksheetNotFound as e:
            print(f"❌ FATAL ERROR: Could not find a required worksheet in your Google Sheet.")
            print(f"Details: {e}")
        except gspread.exceptions.APIError as e:
            if "PERMISSION_DENIED" in str(e):
                print(f"❌ FATAL ERROR: Permission denied for Spreadsheet ID '{SPREADSHEET_ID}'.")
                print(f"Ensure the service account '{os.getenv('EVENT_CLIENT_EMAIL')}' has 'Editor' permissions on the Google Sheet.")
            else:
                print(f"❌ FATAL ERROR: An API error occurred: {e}")
        except Exception as e:
            print(f"❌ FATAL ERROR: An unexpected error occurred during GSheets initialization:")
            traceback.print_exc()
            print("This might be due to incorrect 'EVENT_' credentials in your .env file.")

    def log_command(self, player_name, command, args_dict):
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            args_json = json.dumps(args_dict)
            self.command_log.append_row([player_name, command, args_json, timestamp, "no"])
            print(f"✅ Logged {command} for {player_name}: {args_json}")
        except Exception as e:
            print(f"❌ Error logging command: {e}")

    def get_team_data(self, team_role_name: str) -> dict:
        """Fetches all data for a specific team."""
        try:
            team_row = self.team_data_sheet.find(team_role_name)
            data = self.team_data_sheet.row_values(team_row.row)
            headers = self.team_data_sheet.row_values(1)
            team_dict = dict(zip(headers, data))
            return team_dict
        except gspread.exceptions.CellNotFound:
            print(f"Error: Team '{team_role_name}' not found in TeamData.")
            return None
        except Exception as e:
            print(f"Error in get_team_data: {e}")
            return None
    
    def get_jail_status(self, team_name: str) -> str:
        """Checks if a team is actually in jail or just visiting."""
        try:
            records = self.team_data_sheet.get_all_records()
            team_info = next((r for r in records if r.get("Team") == team_name), None)
            return str(team_info.get("In Jail", "no")).strip().lower() if team_info else "no"
        except Exception as e:
            print(f"❌ Error getting jail status: {e}")
            return "no"

    def set_jail_status(self, team_name: str, status: str):
        """Updates the team's jail status ('yes' or 'no')."""
        try:
            records = self.team_data_sheet.get_all_records()
            headers = list(records[0].keys())
            
            if "In Jail" not in headers:
                print("❌ 'In Jail' column not found in TeamData sheet.")
                return
                
            col_index = headers.index("In Jail") + 1
            team_row = next((i for i, r in enumerate(records, start=2) if r.get("Team") == team_name), None)
            
            if team_row:
                self.team_data_sheet.update_cell(team_row, col_index, status)
        except Exception as e:
            print(f"❌ Error setting jail status: {e}")
    
    def get_team(self, member: discord.Member) -> Optional[str]:
        for role in member.roles:
            if role.name in TEAM_ROLES:
                return role.name
        return None

    def get_team_channel(self, team_name: str) -> Optional[discord.TextChannel]:
        """Fetches the discord.TextChannel object for a given team name."""
        channel_id = TEAM_CHANNELS_MAP.get(team_name)
        if channel_id:
            channel = self.bot.get_channel(channel_id)
            if isinstance(channel, discord.TextChannel):
                return channel
        print(f"❌ Could not find channel for team: {team_name}")
        return None


    def get_team_name_from_channel(self, channel: Optional[discord.abc.GuildChannel]) -> Optional[str]:
        """Best-effort reverse lookup from a team channel object to its team name."""
        try:
            if not channel:
                return None
            channel_id = getattr(channel, "id", None)
            if channel_id is None:
                return None
            for team_name, team_channel_id in TEAM_CHANNELS_MAP.items():
                if int(team_channel_id) == int(channel_id):
                    return team_name
        except Exception as e:
            print(f"❌ Error resolving team from channel: {e}")
        return None

    def _get_game_log_team_color(self, team_name: Optional[str]) -> discord.Color:
        try:
            return discord.Color(GAME_LOG_TEAM_COLOR_MAP.get(str(team_name), 0x5865F2))
        except Exception:
            return discord.Color.blurple()

    def _format_game_log_title(self, team_name: Optional[str]) -> str:
        return f"🕹️ Game Log • {team_name or 'Unknown Team'}"

    def _normalize_game_log_victim_description(self, description: Optional[str], team_name: Optional[str]) -> Optional[str]:
        """Convert victim-facing phrasing (you/your team) into neutral game-log phrasing."""
        try:
            if not description:
                return description
            team_name = team_name or "Unknown Team"
            desc = str(description).strip()
            # Prefer the first sentence/line for the public log to avoid duplicating victim-only detail.
            first_line = desc.split('\n', 1)[0].strip()
            first_sentence = first_line.split('. ', 1)[0].strip()
            candidate = (first_sentence + ('.' if first_sentence and not first_sentence.endswith('.') else '')) if first_sentence else first_line

            replacements = [
                (" on your team", f" on {team_name}"),
                (" on you", f" on {team_name}"),
                (" your team", f" {team_name}"),
                ("Your team", f"{team_name}"),
                ("You are ", f"{team_name} is "),
                ("You've been ", f"{team_name} was "),
                ("You were ", f"{team_name} was "),
            ]
            for old, new in replacements:
                candidate = candidate.replace(old, new)

            # Light cleanup if the source used markdown around team names.
            candidate = candidate.replace('**', '')
            return candidate or desc
        except Exception as e:
            print(f"❌ Error normalizing game log victim description: {e}")
            return description

    def _is_secret_game_log_message(self, content: Optional[str] = None, embed: Optional[discord.Embed] = None) -> bool:
        """Messages that should stay private to team channels (activation/status/card-receive secrets)."""
        try:
            parts = []
            if content:
                parts.append(str(content))
            if embed:
                if embed.title:
                    parts.append(str(embed.title))
                if embed.description:
                    parts.append(str(embed.description))
                for field in getattr(embed, 'fields', []):
                    parts.append(str(getattr(field, 'name', '')))
                    parts.append(str(getattr(field, 'value', '')))
            text_blob = ' '.join(parts).lower()

            # Keep hidden: drawing/receiving cards
            secret_card_phrases = [
                'drew a chance card', 'drew a chest card',
                'received a chance card', 'received a chest card',
                'tried to draw a chance card', 'tried to draw a chest card'
            ]
            if any(phrase in text_blob for phrase in secret_card_phrases):
                return True

            # Keep hidden: activation card usage / activation trigger messages
            secret_activation_phrases = [
                'vengeance activated',
                'redemption activated',
                'elder maul activated'
            ]
            if any(phrase in text_blob for phrase in secret_activation_phrases):
                return True

            return False
        except Exception as e:
            print(f"❌ Error checking game log secrecy filter: {e}")
            return False

    async def mirror_to_game_log(
        self,
        channel: Optional[discord.TextChannel],
        *,
        content: Optional[str] = None,
        embed: Optional[discord.Embed] = None,
        team_name: Optional[str] = None
    ):
        """Mirror public game action messages to the shared game log channel as embeds."""
        try:
            if self._is_secret_game_log_message(content=content, embed=embed):
                return

            if channel is None:
                return

            game_log_channel = self.bot.get_channel(int(GAME_LOG_CHANNEL_ID))
            if not isinstance(game_log_channel, discord.TextChannel):
                print(f"❌ Game log channel {GAME_LOG_CHANNEL_ID} not found")
                return

            if getattr(channel, 'id', None) == getattr(game_log_channel, 'id', None):
                return

            team_name = team_name or self.get_team_name_from_channel(channel) or 'Unknown Team'

            team_color = self._get_game_log_team_color(team_name)
            log_title = self._format_game_log_title(team_name)

            if embed is not None:
                log_embed = embed.copy()
                original_title = str(log_embed.title).strip() if log_embed.title else ""
                original_description = str(log_embed.description).strip() if log_embed.description else ""

                # Team-specific styling for easy scanning in the shared log.
                log_embed.color = team_color
                log_embed.title = log_title

                # Victim-facing embeds read awkwardly in a shared log ("you/your team").
                # Convert to a neutral summary and avoid extra fields/noise.
                lower_title = original_title.lower()
                lower_desc = original_description.lower()
                looks_victim_facing = (
                    lower_title.startswith('you ')
                    or "you were" in lower_title
                    or "you've" in lower_title
                    or " your team" in lower_desc
                    or " on your team" in lower_desc
                    or lower_desc.startswith('you ')
                )
                if looks_victim_facing and original_description:
                    log_embed.description = self._normalize_game_log_victim_description(original_description, team_name)

                if content:
                    extra = str(content).strip()
                    if extra:
                        # Append plain message text to the description instead of extra fields for cleaner logs.
                        if log_embed.description:
                            log_embed.description = f"{log_embed.description}\n{extra}"[:4096]
                        else:
                            log_embed.description = extra[:4096]
                await game_log_channel.send(embed=log_embed)
                return

            if content:
                log_embed = discord.Embed(
                    title=log_title,
                    description=str(content),
                    color=team_color
                )
                await game_log_channel.send(embed=log_embed)
        except Exception as e:
            print(f"❌ Error mirroring to game log: {e}")
    def has_event_captain_role(self, member: discord.Member) -> bool:
        return any(role.id == EVENT_CAPTAIN_ROLE_ID for role in member.roles)

    def has_event_staff_role(self, member: discord.Member) -> bool:
        return any(role.id == EVENT_STAFF_ROLE_ID for role in member.roles)
        
    def get_team_house_color(self, team_name: str) -> str:
        """
        Retrieves the team's background color hex from TeamData (column F).
        Used for house color visualization and ownership.
        """
        try:
            team_rows = self.team_data_sheet.get_all_records()
            for record in team_rows:
                if record.get("Team") == team_name:
                    color_hex = record.get("BG Color", "#FFFFFF")
                    if not str(color_hex).startswith("#"):
                        color_hex = f"#{color_hex}"
                    return color_hex
        except Exception as e:
            print(f"❌ Error fetching color for {team_name}: {e}")
        return "#FFFFFF"


    def get_houses(self) -> list:
        """
        Retrieves the list of all active houses from the house data sheet.
        Returns a list of dictionaries: [{"tile": 5, "color": "#ff0000"}, ...]
        """
        try:
            data = self.house_data_sheet.get_all_records()
            houses = []
            for record in data:
                tile = int(record.get("Tile", 0) or 0)
                owner = record.get("OwnerTeam", "")
                if tile > 0 and owner:
                    color = self.get_team_house_color(owner)
                    houses.append({"tile": tile, "color": color})
            return houses
        except Exception as e:
            print(f"❌ Error fetching house data: {e}")
            return []


    def place_house(self, team_name: str, tile_number: int, is_free: bool) -> bool:
        """
        Places or buys a house.
        For POH Voucher (is_free=True), immediately updates the HouseData sheet.
        For normal houses, sends a /buy_house command to the game engine.
        
        :returns: True if successful.
        """
        try:
            if is_free:
                data = self.house_data_sheet.get_all_records()
                updated = False

                for idx, row in enumerate(data, start=2):
                    if int(row.get("Tile", 0)) == tile_number:
                        if row.get("OwnerTeam", "") == team_name:
                            count = int(row.get("HouseCount", 0)) + 1
                        else:
                            count = 1

                        self.house_data_sheet.update_acell(f"C{idx}", team_name)
                        self.house_data_sheet.update_acell(f"D{idx}", str(count))
                        updated = True
                        print(f"<:housetele:1437980013831131206> Updated existing house on tile {tile_number} for {team_name} (now {count} houses).")
                        break

                if not updated:
                    self.house_data_sheet.append_row([tile_number, "", team_name, 1])
                    print(f"<:housetele:1437980013831131206> Added new free house for {team_name} on tile {tile_number}.")

                # ---> NEW: Sync the Houses Owned column <---
                self.sync_houses_owned(team_name)

                return True

            else:
                self.log_command(
                    team_name,
                    "/buy_house",
                    {"team": team_name, "tile": tile_number}
                )
                return True

        except Exception as e:
            print(f"❌ Error placing house for {team_name} on tile {tile_number}: {e}")
            return False

    def get_team_rolls(self, team_name: str) -> int:
        """
        Retrieves the current 'Rolls Available' count for a team.

        Uses a direct cell read (instead of get_all_records) to avoid stale reads
        immediately after a roll is spent, which can suppress the "Free Roll Granted"
        message on Chance/Chest/Glider/GO/Bank Standing landings.
        """
        try:
            headers = self.team_data_sheet.row_values(1)
            if "Rolls Available" not in headers:
                return 0
            rolls_col_index = headers.index("Rolls Available") + 1

            records = self.team_data_sheet.get_all_records()
            for idx, record in enumerate(records, start=2):
                if record.get("Team") == team_name:
                    raw_val = self.team_data_sheet.cell(idx, rolls_col_index).value
                    raw_str = str(raw_val).replace(',', '').strip() if raw_val is not None else "0"
                    return int(raw_str) if raw_str.lstrip('-').isdigit() else 0
            return 0
        except Exception as e:
            print(f"❌ Error getting team rolls for {team_name}: {e}")
            return 0

    def increment_rolls_available(self, team_name: str):
        try:
            records = self.team_data_sheet.get_all_records()
            for idx, record in enumerate(records, start=2):
                if record.get("Team") == team_name:
                    headers = self.team_data_sheet.row_values(1)
                    if "Rolls Available" not in headers:
                        print("❌ 'Rolls Available' column not found.")
                        return
                    col_index = headers.index("Rolls Available") + 1
                    current_rolls = self.team_data_sheet.cell(idx, col_index).value
                    current_rolls_int = int(current_rolls) if current_rolls and str(current_rolls).isdigit() else 0
                    self.team_data_sheet.update_cell(idx, col_index, current_rolls_int + 1)
                    print(f"✅ Incremented rolls for {team_name} to {current_rolls_int + 1}")
                    return
        except Exception as e:
            print(f"❌ Error incrementing rolls: {e}")

    def decrement_rolls_available(self, team_name: str):
        try:
            records = self.team_data_sheet.get_all_records()
            for idx, record in enumerate(records, start=2):
                if record.get("Team") == team_name:
                    headers = self.team_data_sheet.row_values(1)
                    if "Rolls Available" not in headers:
                        print("❌ 'Rolls Available' column not found.")
                        return
                    col_index = headers.index("Rolls Available") + 1
                    current_rolls = self.team_data_sheet.cell(idx, col_index).value
                    current_rolls_int = int(current_rolls) if current_rolls and str(current_rolls).isdigit() else 0
                    new_val = max(0, current_rolls_int - 1)
                    self.team_data_sheet.update_cell(idx, col_index, new_val)
                    print(f"✅ Decremented rolls for {team_name}: {current_rolls_int} → {new_val}")
                    return
        except Exception as e:
            print(f"❌ Error decrementing rolls: {e}")

    def get_used_card_flag(self, team_name: str) -> str:
        """Checks the 'Used Card This Turn' flag for a team. Defaults to 'no'."""
        try:
            records = self.team_data_sheet.get_all_records()
            for record in records:
                if record.get("Team") == team_name:
                    return record.get("Used Card This Turn", "no")
        except Exception as e:
            print(f"❌ Error in get_used_card_flag: {e}")
        return "no"

    def set_used_card_flag(self, team_name: str, status: str):
        """Sets the 'Used Card This Turn' flag (Col I) for a team."""
        try:
            records = self.team_data_sheet.get_all_records()
            headers = self.team_data_sheet.row_values(1)
            
            col_name = "Used Card This Turn"
            if col_name not in headers:
                print(f"❌ '{col_name}' column not found in TeamData.")
                return
                
            col_index = headers.index(col_name) + 1

            for idx, record in enumerate(records, start=2):
                if record.get("Team") == team_name:
                    self.team_data_sheet.update_cell(idx, col_index, status)
                    print(f"✅ Set '{col_name}' for {team_name} to '{status}'")
                    return
        except Exception as e:
            print(f"❌ Error in set_used_card_flag: {e}")


    def get_bought_house_flag(self, team_name: str) -> str:
        """Checks the 'Bought House This Turn' flag for a team. Defaults to 'no'."""
        try:
            records = self.team_data_sheet.get_all_records()
            for record in records:
                if record.get("Team") == team_name:
                    return record.get("Bought House This Turn", "no")
        except Exception as e:
            print(f"❌ Error in get_bought_house_flag: {e}")
        return "no"

    def set_bought_house_flag(self, team_name: str, status: str):
        """Sets the 'Bought House This Turn' flag for a team."""
        try:
            records = self.team_data_sheet.get_all_records()
            headers = self.team_data_sheet.row_values(1)
            
            col_name = "Bought House This Turn"
            if col_name not in headers:
                print(f"❌ '{col_name}' column not found in TeamData.")
                return
                
            col_index = headers.index(col_name) + 1

            for idx, record in enumerate(records, start=2):
                if record.get("Team") == team_name:
                    self.team_data_sheet.update_cell(idx, col_index, status)
                    print(f"✅ Set '{col_name}' for {team_name} to '{status}'")
                    return
        except Exception as e:
            print(f"❌ Error in set_bought_house_flag: {e}")

    class RejectModal(ui.Modal, title="Reject Drop Submission"):
        reason = ui.TextInput(
            label="Reason for rejection",
            style=discord.TextStyle.paragraph,
            placeholder="Explain why the drop is rejected...",
            required=True,
            max_length=1000
        )

        def __init__(self, review_message: discord.Message, submitter: discord.Member):
            super().__init__()
            self.review_message = review_message
            self.submitter = submitter

        async def on_submit(self, interaction: discord.Interaction):
            try:
                log_chan = interaction.client.get_channel(int(LOG_CHANNEL)) # 🔹 FIXED: Cast to int
                if log_chan:
                    await log_chan.send(
                        f"❌ Drop submission rejected for {self.submitter.mention} by {interaction.user.mention}.\n"
                        f"**Reason:** {self.reason.value}"
                    )
                else:
                    print(f"❌ RejectModal: Log channel {LOG_CHANNEL} not found.")

                embed = self.review_message.embeds[0]
                embed.color = discord.Color.red()
                if "[Rejected]" not in embed.title:
                    embed.title += " [Rejected]"
                existing_field = next((i for i, field in enumerate(embed.fields) if field.name == "Rejection Reason"), None)
                if existing_field is not None:
                    embed.set_field_at(existing_field, name="Rejection Reason", value=self.reason.value, inline=False)
                else:
                    embed.add_field(name="Rejection Reason", value=self.reason.value, inline=False)

                await self.review_message.edit(embed=embed, view=None)
                await interaction.response.send_message("✅ Rejection noted.", ephemeral=True)
            except Exception as e:
                print(f"❌ Error in RejectModal: {e}")
                await interaction.response.send_message(f"Error processing rejection: {e}", ephemeral=True)


    def log_drop_to_sheet(self, submitted_for: str, team: str, boss: str, drop: str, verified_by: str, screenshot: str):
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            self.drop_log_sheet.append_row([
                submitted_for,
                team,
                boss,
                drop,
                verified_by,
                screenshot,
                timestamp
            ])
            print(f"✅ Logged drop for {submitted_for} ({boss} - {drop})")
        except Exception as e:
            print(f"❌ Error writing to DropLog sheet: {e}")


    class DropReviewButtons(ui.View):
        def __init__(self, cog: 'MonopolyCog', submitted_user, drop, image_url, submitting_user, team_mention, boss):
            super().__init__(timeout=None)
            self.cog = cog # Store cog instance
            self.submitted_user = submitted_user
            self.drop = drop
            self.image_url = image_url
            self.submitting_user = submitting_user
            self.team_mention = team_mention
            self.boss = boss
            self.message = None
            self.current_reviewer = None
            self.approve_button.disabled = True
            self.reject_button.disabled = True

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if not self.cog.has_event_staff_role(interaction.user):
                await interaction.response.send_message("You do not have permission to use these buttons.", ephemeral=True)
                return False
            if self.current_reviewer and interaction.user != self.current_reviewer:
                await interaction.response.send_message(
                    f"This submission is currently being reviewed by {self.current_reviewer.mention}. Please wait.",
                    ephemeral=True,
                )
                return False
            return True

        @ui.button(label="Review", style=discord.ButtonStyle.primary, custom_id="review_drop")
        async def review_button(self, interaction: discord.Interaction, button: ui.Button):
            if self.current_reviewer == interaction.user:
                self.current_reviewer = None
                button.label = "Review"
                self.approve_button.disabled = True
                self.reject_button.disabled = True
                content = "Stopped reviewing."
            else:
                self.current_reviewer = interaction.user
                button.label = f"Reviewing: {interaction.user.display_name}"
                self.approve_button.disabled = False
                self.reject_button.disabled = False
                content = "You are now reviewing this submission."

            embed = self.message.embeds[0]
            status_field_index = -1
            for i, field in enumerate(embed.fields):
                if field.name == "Review Status":
                    status_field_index = i
                    break
            
            status_value = (f"Currently being reviewed by {self.current_reviewer.mention}" if self.current_reviewer else "Not currently being reviewed")
            
            if status_field_index != -1:
                embed.set_field_at(status_field_index, name="Review Status", value=status_value, inline=False)
            else:
                embed.insert_field_at(0, name="Review Status", value=status_value, inline=False)

            await self.message.edit(embed=embed, view=self)
            await interaction.response.send_message(content, ephemeral=True)

        @ui.button(label="Approve Drop", style=discord.ButtonStyle.success, custom_id="approve_drop")
        async def approve_button(self, interaction: discord.Interaction, button: ui.Button):
            if not self.current_reviewer:
                await interaction.response.send_message("You must start reviewing before approving.", ephemeral=True)
                return

            try:
                await interaction.response.defer(ephemeral=True)

                embed = self.message.embeds[0]
                embed.color = discord.Color.green()
                if "[Approved]" not in embed.title:
                    embed.title += " [Approved]"
                
                status_field_index = -1
                for i, field in enumerate(embed.fields):
                    if field.name in ("Review Status", "Reviewed By"):
                        status_field_index = i
                        break
                
                if status_field_index != -1:
                    embed.set_field_at(status_field_index, name="Reviewed By", value=interaction.user.mention, inline=False)
                else:
                    embed.insert_field_at(0, name="Reviewed By", value=interaction.user.mention, inline=False)
                
                await self.message.delete()

                log_chan = self.cog.bot.get_channel(int(LOG_CHANNEL))
                team_chan = self.cog.get_team_channel(self.cog.get_team(self.submitted_user))

                if log_chan:
                    mention = self.team_mention or self.submitted_user.mention or self.submitting_user.mention
                    await log_chan.send(content=f"{mention} Drop submission approved by {interaction.user.mention}.", embed=embed)
                    print(f"✅ Sent approval to DropLog ({log_chan.name})")
                else:
                    print(f"❌ DropLog channel {LOG_CHANNEL} not found")

                team_name = self.cog.get_team(self.submitted_user) or "*No team*"
                self.cog.log_drop_to_sheet(
                    submitted_for=str(self.submitted_user),
                    team=team_name,
                    boss=self.boss,
                    drop=self.drop,
                    verified_by=interaction.user.name,
                    screenshot=self.image_url
                )

                try:
                    gp_multiplier, consumed_card_name = self.cog.check_and_consume_alchemy(team_name)
                    alchemy_bonus = ""

                    item_values_records = self.cog.item_values_sheet.get_all_records()
                    gp_lookup = {item['Item']: int(str(item['GP']).replace(',', '')) for item in item_values_records}
                    
                    base_gp_value = gp_lookup.get(self.drop, 0)
                    final_gp_value = base_gp_value * gp_multiplier
                    original_gp_value_pre_tax = final_gp_value

                    if gp_multiplier > 1 and consumed_card_name:
                        emoji = CARD_EMOJIS.get(consumed_card_name, "")
                        alchemy_bonus = f" (x{gp_multiplier} from {emoji} **{consumed_card_name}**!)"

                    if final_gp_value > 0 and team_name != "*No team*":
                        records = self.cog.team_data_sheet.get_all_records()
                        house_records = self.cog.house_data_sheet.get_all_records()

                        current_tile = None
                        for rec in records:
                            if rec.get("Team") == team_name:
                                current_tile = int(rec.get("Position", 0) or 0)
                                break

                        tax_amount = 0
                        owner_team = None
                        house_count = 0

                        if current_tile is not None:
                            for hrec in house_records:
                                tile = int(hrec.get("Tile", 0) or 0)
                                if tile == current_tile:
                                    owner_team = hrec.get("OwnerTeam", "")
                                    house_count = int(hrec.get("HouseCount", 0) or 0)
                                    break

                            if owner_team and owner_team != team_name and house_count > 0:
                                tax_map = {1: 0.20, 2: 0.40, 3: 0.60, 4: 0.80}
                                tax_percent = tax_map.get(house_count, 0)
                                tax_amount = int(final_gp_value * tax_percent)
                                final_gp_value -= tax_amount

                        headers = self.cog.team_data_sheet.row_values(1)
                        try:
                            gp_col_index = headers.index("GP") + 1
                        except ValueError:
                            print("❌ GP column not found in TeamData.")
                            return

                        for idx, record in enumerate(records, start=2):
                            if record.get("Team") == team_name:
                                current_gp = int(record.get("GP", 0) or 0)
                                new_gp = max(0, current_gp + final_gp_value)
                                self.cog.team_data_sheet.update_cell(idx, gp_col_index, new_gp)
                                print(f"✅ Awarded {final_gp_value:,} GP to {team_name}. New total: {new_gp}")
                                
                                gp_message = (
                                    f"<:MaxCash:1347684049040183427> **{team_name}** earned **{final_gp_value:,} GP** "
                                    f"from a **{self.drop}** drop!{alchemy_bonus}"
                                )
                                if team_chan:
                                    await team_chan.send(gp_message)
                                    await self.cog.mirror_to_game_log(team_chan, content=gp_message, team_name=team_name)
                                break

                        if tax_amount > 0 and owner_team:
                            owner_team_chan = self.cog.get_team_channel(owner_team)
                            for o_idx, orec in enumerate(records, start=2):
                                if orec.get("Team") == owner_team:
                                    owner_gp = int(orec.get("GP", 0) or 0)
                                    new_owner_gp = owner_gp + tax_amount
                                    self.cog.team_data_sheet.update_cell(o_idx, gp_col_index, new_owner_gp)
                                    print(f"<:houseicon:1438085020156821555> {owner_team} received {tax_amount:,} GP house tax from {team_name}.")
                                    break
                            
                            tax_message = (
                                f"<:houseicon:1438085020156821555> **House Tax:** {team_name} paid **{tax_amount:,} GP** "
                                f"to **{owner_team}** for a level {house_count} house on tile {current_tile} "
                                f"(Original Value: **{original_gp_value_pre_tax:,} GP** | Tax: **{int(tax_percent * 100)}%**)."
                            )
                            if team_chan:
                                await team_chan.send(tax_message)
                                await self.cog.mirror_to_game_log(team_chan, content=tax_message, team_name=team_name)
                            if owner_team_chan:
                                await owner_team_chan.send(tax_message)
                                await self.cog.mirror_to_game_log(owner_team_chan, content=tax_message, team_name=owner_team)

                except Exception as e:
                    print(f"❌ Error in GP/tax logic: {e}")
                
                if team_name and team_name != "*No team*":
                    try:
                        records = self.cog.team_data_sheet.get_all_records()
                        current_tile = None
                        for record in records:
                            if record.get("Team") == team_name:
                                current_tile = int(record.get("Position", 0))
                                break
                        
                        tile_boss_map = {
                            1: ["Zulrah"], 3: ["General Graardor", "K'ril Tsutsaroth", "Kree'arra", "Commander Zilyana"],
                            4: ["Vet'ion", "Venenatis", "Callisto"], 5: ["The Whisperer"], 6: ["Tombs of Amascut"],
                            8: ["Theatre of Blood"], 9: ["Chambers of Xeric"], 10: ["Gauntlet", "Nex"], 11: ["Barrows"],
                            13: ["Moons of Peril"], 14: ["Nightmare"], 15: ["The Leviathan"], 16: ["Yama"],
                            18: ["Scorpia", "Chaos Fanatic", "Crazy Archaeologist"], 19: ["Cerberus"],
                            21: ["Tombs of Amascut"], 23: ["Theatre of Blood"], 24: ["Chambers of Xeric"],
                            25: ["Vardorvis"], 26: ["Hueycoatl"], 27: ["Colosseum"], 29: ["Doom of Mokhaiotl"],
                            31: ["Tombs of Amascut"], 32: ["Theatre of Blood"], 34: ["Chambers of Xeric"],
                            35: ["Duke Sucellus"], 37: ["Phantom Muspah"], 39: ["Araxxor"]
                        }

                        bosses_for_tile = tile_boss_map.get(current_tile, [])
                        if self.boss in bosses_for_tile:
                            self.cog.increment_rolls_available(team_name)
                            print(f"✅ Roll granted: Team {team_name} on tile {current_tile} ({self.boss})")
                            
                            if team_chan:
                                roll_grant_embed = discord.Embed(
                                    title="🎲 Roll Granted!",
                                    description=(
                                        f"Your team landed a drop at **{self.boss}**! "
                                        "A free roll has been granted! Use `/roll` to use it."
                                    ),
                                    color=discord.Color.green()
                                )
                                await team_chan.send(embed=roll_grant_embed)
                                await self.cog.mirror_to_game_log(team_chan, embed=roll_grant_embed, team_name=team_name)
                        else:
                            print(f"❗ No roll granted: Team {team_name} on tile {current_tile}, drop boss {self.boss} not valid here.")
                    except Exception as e:
                        print(f"❌ Error checking tile before granting roll: {e}")

                await interaction.followup.send("✅ Drop approved and logged.", ephemeral=True)

            except Exception as e:
                print(f"❌ Error in approve_button: {e}")
                await interaction.followup.send(f"❌ Error approving drop: {e}", ephemeral=True)

        @ui.button(label="Reject Drop", style=discord.ButtonStyle.danger, custom_id="reject_drop")
        async def reject_button(self, interaction: discord.Interaction, button: ui.Button):
            if not self.current_reviewer:
                await interaction.response.send_message("You must start reviewing before rejecting.", ephemeral=True)
                return
            await interaction.response.send_modal(self.cog.RejectModal(self.message, self.submitted_user))

    class BossSelectView(ui.View):
        def __init__(self, cog: 'MonopolyCog', submitting_user: discord.Member, submitted_for: discord.Member, screenshot_url: str):
            super().__init__(timeout=180)
            self.cog = cog
            self.submitting_user = submitting_user
            self.submitted_for = submitted_for
            self.screenshot_url = screenshot_url

            self.bosses = list(boss_drops.keys())
            self.page_size = 25
            self.current_page = 0

            self.boss_dropdown = ui.Select(
                placeholder="Select the boss",
                options=self.get_boss_options(),
                min_values=1,
                max_values=1,
            )
            self.boss_dropdown.callback = self.boss_selected
            self.add_item(self.boss_dropdown)

            self.prev_button = ui.Button(label="Previous", style=discord.ButtonStyle.secondary)
            self.next_button = ui.Button(label="Next", style=discord.ButtonStyle.secondary)
            self.prev_button.callback = self.prev_page
            self.next_button.callback = self.next_page
            self.add_item(self.prev_button)
            self.add_item(self.next_button)

            self.update_nav_buttons()

        def get_boss_options(self):
            start = self.current_page * self.page_size
            end = start + self.page_size
            return [discord.SelectOption(label=boss) for boss in sorted(self.bosses)[start:end]]

        def update_nav_buttons(self):
            self.prev_button.disabled = self.current_page == 0
            self.next_button.disabled = (self.current_page + 1) * self.page_size >= len(self.bosses)

        async def prev_page(self, interaction: discord.Interaction):
            if self.current_page > 0:
                self.current_page -= 1
                self.boss_dropdown.options = self.get_boss_options()
                self.update_nav_buttons()
                await interaction.response.edit_message(view=self)

        async def next_page(self, interaction: discord.Interaction):
            if (self.current_page + 1) * self.page_size < len(self.bosses):
                self.current_page += 1
                self.boss_dropdown.options = self.get_boss_options()
                self.update_nav_buttons()
                await interaction.response.edit_message(view=self)

        async def boss_selected(self, interaction: discord.Interaction):
            selected_boss = self.boss_dropdown.values[0]
            await interaction.response.edit_message(
                content=f"Selected boss: **{selected_boss}**. Now select the drop:",
                embed=None,
                view=self.cog.DropSelectView(
                    cog=self.cog,
                    submitting_user=self.submitting_user,
                    submitted_for=self.submitted_for,
                    screenshot_url=self.screenshot_url,
                    boss=selected_boss,
                ),
            )


    class DropSelect(ui.Select):
        def __init__(self, cog: 'MonopolyCog', submitting_user: discord.Member, submitted_for: discord.Member, screenshot_url: str, boss: str):
            self.cog = cog
            self.submitting_user = submitting_user
            self.submitted_for = submitted_for
            self.screenshot_url = screenshot_url
            self.boss = boss
            options = [discord.SelectOption(label=drop) for drop in sorted(boss_drops[boss])]
            super().__init__(placeholder=f"Select the drop from {boss}", options=options, min_values=1, max_values=1)

        async def callback(self, interaction: discord.Interaction):
            selected_drop = self.values[0]
            
            team_name = self.cog.get_team(self.submitted_for) or "*No team*"
            if team_name == "*No team*":
                await interaction.response.edit_message(content=f"❌ **{self.submitted_for.display_name}** is not on a team.", view=None, embed=None)
                return

            current_tile = None
            records = self.cog.team_data_sheet.get_all_records()
            for record in records:
                if record.get("Team") == team_name:
                    current_tile = int(record.get("Position", 0))
                    break

            if current_tile is None:
                await interaction.response.edit_message(content=f"❌ Could not find data for **{team_name}**.", view=None, embed=None)
                return
                
            tile_boss_map = {
                1: ["Zulrah"], 3: ["General Graardor", "K'ril Tsutsaroth", "Kree'arra", "Commander Zilyana"],
                4: ["Vet'ion", "Venenatis", "Callisto"], 5: ["The Whisperer"], 6: ["Tombs of Amascut"],
                8: ["Theatre of Blood"], 9: ["Chambers of Xeric"], 10: ["Gauntlet", "Nex"], 11: ["Barrows"],
                13: ["Moons of Peril"], 14: ["Nightmare"], 15: ["The Leviathan"], 16: ["Yama"],
                18: ["Scorpia", "Chaos Fanatic", "Crazy Archaeologist"], 19: ["Cerberus"],
                21: ["Tombs of Amascut"], 23: ["Theatre of Blood"], 24: ["Chambers of Xeric"],
                25: ["Vardorvis"], 26: ["Hueycoatl"], 27: ["Colosseum"], 29: ["Doom of Mokhaiotl"],
                31: ["Tombs of Amascut"], 32: ["Theatre of Blood"], 34: ["Chambers of Xeric"],
                35: ["Duke Sucellus"], 37: ["Phantom Muspah"], 39: ["Araxxor"]
            }

            bosses_for_tile = tile_boss_map.get(current_tile, [])
            if self.boss not in bosses_for_tile:
                await interaction.response.edit_message(
                    content=f"❌ Invalid drop: Your team is on tile **{current_tile}**, which does not include **{self.boss}**.",
                    embed=None,
                    view=None
                )
                return

            embed = discord.Embed(title=f"Drop Submission: {self.boss}", colour=discord.Colour.blurple())
            embed.add_field(name="Review Status", value="Awaiting review...", inline=False)
            embed.add_field(name="Submitted For", value=f"{self.submitted_for.mention} `({self.submitted_for.id})`", inline=False)
            embed.add_field(name="Drop Received", value=selected_drop, inline=False)
            embed.add_field(name="Submitted By", value=f"{self.submitting_user.mention} `({self.submitting_user.id})`", inline=False)
            embed.set_image(url=self.screenshot_url)

            review_channel = self.cog.bot.get_channel(int(REVIEW_CHANNEL)) # 🔹 FIXED: Cast to int
            if not review_channel:
                print(f"❌ Review channel {REVIEW_CHANNEL} not found")
                await interaction.response.edit_message(content="❌ Review channel not found.", view=None, embed=None)
                return

            team_role_obj = discord.utils.get(interaction.guild.roles, name=team_name)
            team_mention = team_role_obj.mention if team_role_obj else team_name

            view = self.cog.DropReviewButtons(
                cog=self.cog,
                submitted_user=self.submitted_for,
                drop=selected_drop,
                image_url=self.screenshot_url,
                submitting_user=self.submitting_user,
                team_mention=team_mention,
                boss=self.boss,
            )

            sent_msg = await review_channel.send(embed=embed, view=view)
            view.message = sent_msg
            print(f"✅ Sent drop submission to review channel ({review_channel.name})")

            await interaction.response.edit_message(
                content=f"✅ Drop submission for **{self.boss} - {selected_drop}** sent for review.",
                embed=None,
                view=None,
            )

    class DropSelectView(ui.View):
        def __init__(self, cog: 'MonopolyCog', submitting_user: discord.Member, submitted_for: discord.Member, screenshot_url: str, boss: str):
            super().__init__(timeout=180)
            self.cog = cog
            self.add_item(self.cog.DropSelect(cog, submitting_user, submitted_for, screenshot_url, boss))

    def get_teleblock_status(self, team_name):
        """Checks if a team is teleblocked. Returns 'yes' or 'no'."""
        try:
            team_data_headers = self.team_data_sheet.row_values(1)
            tb_col_index = team_data_headers.index("Teleblocked") + 1
            team_cell = self.team_data_sheet.find(team_name)
            if team_cell:
                return self.team_data_sheet.cell(team_cell.row, tb_col_index).value or "no"
            return "no"
        except Exception as e:
            print(f"Error getting teleblock status for {team_name}: {e}")
            return "no"

    def set_teleblock_status(self, team_name, status="yes"):
        """Sets a team's teleblock status. status should be 'yes' or 'no'."""
        try:
            team_data_headers = self.team_data_sheet.row_values(1)
            tb_col_index = team_data_headers.index("Teleblocked") + 1
            team_cell = self.team_data_sheet.find(team_name)
            if team_cell:
                self.team_data_sheet.update_cell(team_cell.row, tb_col_index, status)
                print(f"Set teleblock status for {team_name} to {status}")
        except Exception as e:
            print(f"Error setting teleblock status for {team_name}: {e}")

    @app_commands.command(name="signup", description="Submit your signup with RSN and a screenshot")
    @app_commands.describe(rsn="Your RSN (RuneScape name)", screenshot="Upload a screenshot for your signup")
    async def signup(self, interaction: discord.Interaction, rsn: str, screenshot: discord.Attachment):
        rsn_clean = (rsn or "").strip()
        if not rsn_clean:
            await interaction.response.send_message("❌ You must provide an RSN.", ephemeral=True)
            return

        # Slash param is required, but validate type to enforce screenshot/image uploads only.
        content_type = (getattr(screenshot, "content_type", None) or "").lower()
        filename = (getattr(screenshot, "filename", None) or "").lower()
        looks_like_image = content_type.startswith("image/") or filename.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif"))
        if not looks_like_image:
            await interaction.response.send_message(
                "❌ The uploaded file must be an image screenshot (PNG/JPG/WEBP/GIF).",
                ephemeral=True
            )
            return

        if not self.signup_sheet:
            await interaction.response.send_message(
                "❌ Signup sheet is not configured yet. Make sure the bot service account has access to the signup spreadsheet.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True, thinking=True)

        try:
            discord_username = getattr(interaction.user, "display_name", None) or getattr(interaction.user, "name", "Unknown")
            discord_id = str(interaction.user.id)
            screenshot_url = screenshot.url

            # Append to the next row. If the sheet has a decorative title row, append_row will still
            # place the submission after the last non-empty row.
            self.signup_sheet.append_row(
                [discord_username, discord_id, rsn_clean, screenshot_url],
                value_input_option="USER_ENTERED"
            )

            role_status_line = ""
            try:
                guild = interaction.guild
                if guild is None:
                    role_status_line = "\n**Role:** Not assigned (command was not used in a server)."
                else:
                    bingo_player_role = guild.get_role(BINGO_PLAYER_ROLE_ID)
                    if bingo_player_role is None:
                        # Fallback by name in case the configured ID is stale.
                        bingo_player_role = discord.utils.get(guild.roles, name="Bingo Player")
                    if bingo_player_role is None:
                        role_status_line = f"\n**Role:** Not assigned (`Bingo Player` role not found by ID `{BINGO_PLAYER_ROLE_ID}`)."
                    elif bingo_player_role in getattr(interaction.user, "roles", []):
                        role_status_line = "\n**Role:** `Bingo Player` already assigned."
                    else:
                        await interaction.user.add_roles(bingo_player_role, reason="User completed /signup")
                        role_status_line = "\n**Role:** `Bingo Player` assigned."
            except discord.Forbidden:
                role_status_line = "\n**Role:** Could not assign `Bingo Player` (missing Manage Roles permission / role hierarchy issue)."
            except discord.HTTPException as role_err:
                role_status_line = f"\n**Role:** Could not assign `Bingo Player` ({role_err})."
            except Exception as role_err:
                print(f"❌ Error assigning Bingo Player role in /signup: {role_err}")
                traceback.print_exc()
                role_status_line = "\n**Role:** Signup saved, but role assignment failed."

            success_embed = discord.Embed(
                title="✅ Signup Submitted!",
                description=(
                    f"Your signup has been recorded.\n\n"
                    f"**RSN:** {rsn_clean}\n"
                    f"**Screenshot:** [Open Image]({screenshot_url})"
                    f"{role_status_line}"
                ),
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=success_embed, ephemeral=False)

            # ---> UPDATED: Give Google Sheets 2.5 seconds to save, then refresh both boards <---
            async def delayed_list_update():
                await asyncio.sleep(2.5)
                if interaction.guild:
                    try:
                        await self.update_live_team_list(interaction.guild)
                        print(f"✅ Live team list successfully updated for {rsn_clean}'s signup.")
                    except Exception as err:
                        print(f"❌ Error updating team list: {err}")
                        
                    try:
                        await self.update_live_signup_list(interaction.guild)
                        print(f"✅ Live signup list successfully updated for {rsn_clean}'s signup.")
                    except Exception as err:
                        print(f"❌ Error updating signup list: {err}")
            
            self.bot.loop.create_task(delayed_list_update())
            
        except Exception as e:
            print(f"❌ Error in /signup: {e}")
            traceback.print_exc()
            await interaction.followup.send(f"❌ Failed to submit signup: {e}", ephemeral=True)

    @app_commands.command(name="roll", description="Roll a dice (1-6) for MONOPOLY")
    @app_commands.describe(value="Optional forced roll (1-6) for quick testing")
    async def roll(self, interaction: discord.Interaction, value: int | None = None):
        if str(interaction.channel_id) not in TEAM_CHANNEL_IDS_AS_STR:
            await interaction.response.send_message("❌ You can only use this command in your team's channel.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=False)  
        team_name = self.get_team(interaction.user) or "*No team*"
        if team_name == "*No team*":
            await interaction.followup.send("❌ You are not on a team.", ephemeral=True)
            return
            
        # Move teleblock update to background
        await asyncio.to_thread(self.set_teleblock_status, team_name, "no")
        team_chan = self.get_team_channel(team_name)

        # 1. Turn Reset Logic (Threaded)
        try:
            cleared_cards = await asyncio.to_thread(self.clear_all_active_statuses, team_name)
            if cleared_cards and team_chan:
                await team_chan.send(f"⌛️ **{team_name}**'s active status effects for: `({', '.join(cleared_cards)})` expired.")
            
            # Combine these two flags into one threaded call if possible, or run them back-to-back
            await asyncio.to_thread(self.set_used_card_flag, team_name, "no")
            await asyncio.to_thread(self.set_bought_house_flag, team_name, "no")

            # --- ADDED: Clear Random Event flags ---
            asyncio.create_task(asyncio.to_thread(self.clear_flag_column, team_name, "Silenced"))
            asyncio.create_task(asyncio.to_thread(self.clear_flag_column, team_name, "Double Card"))

        except Exception as e:
            print(f"❌ Error during turn reset: {e}")

        # 2. Fetch Team Data (ONE call, consolidated)
        # We fetch all records once and find our team locally to save API hits
        all_records = await asyncio.to_thread(self.team_data_sheet.get_all_records)
        headers = list(all_records[0].keys()) if all_records else []
        
        team_row_index = -1
        current_tile = 0
        rolls_available = 0

        for idx, record in enumerate(all_records, start=2):
            if record.get("Team") == team_name:
                rolls_available = int(record.get("Rolls Available", 0) or 0)
                current_tile = int(record.get("Position", 0) or 0)
                team_row_index = idx
                break
        
        if team_row_index == -1:
            await interaction.followup.send(f"❌ Could not find data for **{team_name}**.", ephemeral=True)
            return

        if rolls_available <= 0:
            await interaction.followup.send("❌ Your team has no rolls available.", ephemeral=True)
            return

        # 3. Dice Roll Execution
        raw_result = value if (value and 1 <= value <= 6) else random.randint(1, 6)
        
        # --- ADDED: Apply Pre-Roll Nerfs ---
        team_record = all_records[team_row_index-2]
        is_poisoned = str(team_record.get("Poisoned Roll", "no")).strip().lower() == "yes"
        is_halved = str(team_record.get("Roll Halved", "no")).strip().lower() == "yes"
        try:
            roll_penalty = int(team_record.get("Roll Penalty", 0))
        except ValueError:
            roll_penalty = 0

        result = raw_result
        if is_poisoned:
            result = min(result, 3)
            asyncio.create_task(asyncio.to_thread(self.clear_flag_column, team_name, "Poisoned Roll"))
        if is_halved:
            result = max(1, result // 2)
            asyncio.create_task(asyncio.to_thread(self.clear_flag_column, team_name, "Roll Halved"))
        if roll_penalty > 0:
            result = max(1, result - roll_penalty)
            asyncio.create_task(asyncio.to_thread(self.clear_flag_column, team_name, "Roll Penalty"))

        await asyncio.to_thread(self.decrement_rolls_available, team_name)

        raw_pos = current_tile + result
        new_pos = raw_pos % BOARD_SIZE
        go_message = ""
        
        # 4. Standard Pass Go logic
        if raw_pos >= BOARD_SIZE and new_pos != 30: 
            try:
                pass_go_col = headers.index("Go Passes") + 1
                gp_col = headers.index("GP") + 1
                
                # Use current record data instead of a new cell fetch
                cur_passes = int(all_records[team_row_index-2].get("Go Passes", 0))
                cur_gp = int(str(all_records[team_row_index-2].get("GP", 0)).replace(',',''))
                
                # --- ADDED: Ents GP Halved Check ---
                is_gp_halved = str(all_records[team_row_index-2].get("GP Halved", "no")).strip().lower() == "yes"
                go_reward = 10_000_000 if is_gp_halved else 20_000_000
                
                if is_gp_halved:
                    asyncio.create_task(asyncio.to_thread(self.clear_flag_column, team_name, "GP Halved"))

                await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_index, pass_go_col, cur_passes + 1)
                await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_index, gp_col, cur_gp + go_reward)
                
                if is_gp_halved:
                    go_message = f"🌳 **THE ENTS TOOK THEIR TOLL!** You passed **GO**, but your gear was damaged. You only received **10,000,000 GP**!"
                else:
                    go_message = f"💰 **CONGRATULATIONS!** You passed **GO** and received **20,000,000 GP**!"
            except Exception as e:
                print(f"❌ Error updating Pass Go: {e}")

        # 5. Special Tile Handling (Gliders / Jail)
        if new_pos == 12: 
            new_pos = 28 if current_tile != 38 else 12
        elif new_pos == 28: 
            new_pos = 38 if current_tile != 12 else 28
        elif new_pos == 38: 
            if current_tile != 12:
                new_pos = 12
                # Manual Glider 38 Go Bonus
                try:
                    pass_go_col = headers.index("Go Passes") + 1
                    gp_col = headers.index("GP") + 1
                    cur_passes = int(all_records[team_row_index-2].get("Go Passes", 0))
                    cur_gp = int(str(all_records[team_row_index-2].get("GP", 0)).replace(',',''))
                    
                    # --- ADDED: Ents GP Halved Check ---
                    is_gp_halved = str(all_records[team_row_index-2].get("GP Halved", "no")).strip().lower() == "yes"
                    glider_reward = 10_000_000 if is_gp_halved else 20_000_000
                    
                    if is_gp_halved:
                        asyncio.create_task(asyncio.to_thread(self.clear_flag_column, team_name, "GP Halved"))

                    await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_index, pass_go_col, cur_passes + 1)
                    await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_index, gp_col, cur_gp + glider_reward)
                    
                    if is_gp_halved:
                        go_message = f"🌳 **GLIDER BONUS REDUCED!** You flew over **GO**, but the Ents damaged your glider. You only received **10,000,000 GP**!"
                    else:
                        go_message = "💰 **GLIDER BONUS!** You flew over **GO** and received **20,000,000 GP**!"
                except Exception as e:
                    print(f"❌ Error updating Glider Go Bonus: {e}")
            else:
                new_pos = 38
        elif new_pos == 30:
            new_pos = JAIL_TILE
            go_message = "⛓️ **GO TO JAIL!** You are immediately sent to prison."
            await asyncio.to_thread(self.set_jail_status, team_name, "yes")

        # 6. Update Position & Display Results
        pos_idx = headers.index("Position") + 1
        await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_index, pos_idx, new_pos)
        
        tile_name = self.get_tile_name_for_display(new_pos)
        
        # Check if they were sent to jail THIS turn
        just_sent_to_jail = (new_pos == 10 and "GO TO JAIL" in go_message)
        
        if new_pos == 10 and not just_sent_to_jail:
            tile_name = "Jail (Just Visiting) - Nex, Gauntlet"
        elif new_pos == 10 and just_sent_to_jail:
            tile_name = "Jail"
        
        # --- ADDED: Dynamic Roll Description ---
        roll_desc = f"**{interaction.user.display_name}** rolled a **{raw_result}**!"
        if is_poisoned:
            roll_desc += f"\n🥀 *Your poison capped your roll at **{result}**!*"
        elif is_halved:
            roll_desc += f"\n🏋️ *The Demon's exhaustion cut your roll to **{result}**!*"
        elif roll_penalty > 0:
            roll_desc += f"\n🪦 *The Gravedigger's fatigue reduced your roll to **{result}**!*"
            
        roll_desc += f"\nMoving to the **{tile_name}** tile."
        
        roll_embed = discord.Embed(
            title=f"🎲 {team_name} Rolled!",
            description=roll_desc,
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=roll_embed)
        await self.mirror_to_game_log(interaction.channel, embed=roll_embed)

        if go_message:
            await interaction.channel.send(go_message)

        # 7. POST-MOVE TRIGGERS
        tile_boss_map = self._get_tile_boss_map()
        if new_pos in tile_boss_map:
            # Only block the drop embed if they were actively arrested and sent to jail
            if not just_sent_to_jail:
                await self.auto_post_show_drops_if_boss_tile(team_name, new_pos)

        # Final checks (Cards & Free Rolls)
        await self.check_and_award_card_on_land(team_name, new_pos, "rolling")

        # --- PASSIVE RANDOM EVENT ENGINE ---
        # (Leave your Random Event code here exactly as it is)
        
        try:
            team_mult = float(all_records[team_row_index-2].get("Multiplier", 1))
        except ValueError:
            team_mult = 1.0

        spawn_chance = int(team_mult * 5)
        if random.randint(1, 100) <= spawn_chance:
            asyncio.create_task(self.trigger_passive_random_event(interaction.channel, team_name))


    def _get_tile_boss_map(self) -> dict[int, list[str]]:
        return {
            1: ["Zulrah"], 3: ["General Graardor", "K'ril Tsutsaroth", "Kree'arra", "Commander Zilyana"],
            4: ["Vet'ion", "Venenatis", "Callisto"], 5: ["The Whisperer"], 6: ["Tombs of Amascut"],
            8: ["Theatre of Blood"], 9: ["Chambers of Xeric"], 10: ["Gauntlet", "Nex"], 11: ["Barrows"],
            13: ["Moons of Peril"], 14: ["Nightmare"], 15: ["The Leviathan"], 16: ["Yama"],
            18: ["Scorpia", "Chaos Fanatic", "Crazy Archaeologist"], 19: ["Cerberus"],
            21: ["Tombs of Amascut"], 23: ["Theatre of Blood"], 24: ["Chambers of Xeric"],
            25: ["Vardorvis"], 26: ["Hueycoatl"], 27: ["Colosseum"], 29: ["Doom of Mokhaiotl"],
            31: ["Tombs of Amascut"], 32: ["Theatre of Blood"], 34: ["Chambers of Xeric"],
            35: ["Duke Sucellus"], 37: ["Phantom Muspah"], 39: ["Araxxor"]
        }


    def get_tile_name_for_display(self, position: int) -> str:
        """Returns a human-readable tile name (boss/property/special) for a board tile."""
        try:
            tile_boss_map = self._get_tile_boss_map()
            if position in CHEST_TILES:
                return "Chest"
            if position in CHANCE_TILES:
                return "Chance"
            if position == GO_TILE:
                return "GO"
            if position == JAIL_TILE:
                return "Jail"
            if position == BANK_STANDING_TILE:
                return "Bank Standing"
            if position in GLIDER_TILES:
                return "Glider"
            if position in tile_boss_map:
                return ", ".join(tile_boss_map[position])

            for prop in self.house_data_sheet.get_all_records():
                try:
                    if int(prop.get("Tile", -1)) == position:
                        return prop.get("Name", f"Tile {position}")
                except Exception:
                    continue
        except Exception as e:
            print(f"❌ Error resolving tile name for {position}: {e}")
        return f"Tile {position}"

    def resolve_nonroll_landing_tile(self, intended_pos: int) -> int:
        """Resolve one-step board effects for card teleports/forced moves (gliders, go-to-jail)."""
        try:
            pos = int(intended_pos)
        except Exception:
            return intended_pos

        # Card/teleport landings should trigger gliders if you land on them.
        if pos == 12:
            return 28
        if pos == 28:
            return 38
        if pos == 38:
            return 12
        if pos == 30:
            return JAIL_TILE
        return pos

    def get_glider_redirect_note(self, intended_pos: int, final_pos: int, *, second_person: bool = False, quoted: bool = True) -> str:
        """Return feedback text when a non-roll move lands on a glider and is redirected."""
        try:
            intended = int(intended_pos)
            final = int(final_pos)
        except Exception:
            return ""

        if intended == final or intended not in GLIDER_TILES:
            return ""

        final_tile_name = self.get_tile_name_for_display(final)
        if second_person:
            msg = (
                f"You landed on a **Glider** tile and were launched to the **{final_tile_name}** tile "
                f"(Tile **{final}**)."
            )
        else:
            msg = (
                f"Landed on a **Glider** tile and was launched to the **{final_tile_name}** tile "
                f"(Tile **{final}**)."
            )

        return f"\n> {msg}" if quoted else f"\n{msg}"

    async def auto_post_show_drops_if_boss_tile(self, team_name: str, position: int):
        """Auto-post the /show_drops embed in a team's channel if the tile has boss drops."""
        try:
            team_chan = self.get_team_channel(team_name)
            if not team_chan:
                return
            drops_embed = self.build_show_drops_embed_for_tile(position)
            if drops_embed is not None:
                await team_chan.send(embed=drops_embed)
        except Exception as e:
            print(f"❌ Error auto-posting /show_drops for {team_name} on tile {position}: {e}")


    def build_show_drops_embed_for_tile(self, position: int) -> discord.Embed | None:
        """Build the same embed used by /show_drops for a board tile. Returns None if tile has no boss drops."""
        tile_boss_map = self._get_tile_boss_map()
        boss_list = tile_boss_map.get(position)
        if not boss_list:
            return None

        boss_name_str = ", ".join(boss_list)
        embed = discord.Embed(
            title=f"Available Drops for {boss_name_str} (Tile {position})",
            description="This list shows potential drops and their GP values.",
            color=discord.Color.gold()
        )

        all_items = self.item_values_sheet.get_all_records()

        drop_list_text = ""
        found_any_drops = False

        for boss in boss_list:
            boss_drops_text = ""
            for item in all_items:
                item_boss = item.get("Boss Name")
                if item_boss == boss:
                    item_name = item.get("Item", "Unknown Item")
                    item_gp = item.get("GP", "0")
                    formatted_gp = self._format_gp(item_gp)
                    boss_drops_text += f"• **{item_name}**: {formatted_gp} GP\n"
                    found_any_drops = True

            drop_list_text += f"\n**--- {boss} ---**\n"
            if not boss_drops_text:
                drop_list_text += "No drops found for this boss.\n"
            else:
                drop_list_text += boss_drops_text

        if not found_any_drops:
            drop_list_text = "No drops found for this boss in the `ItemValues` sheet. (Sheet must have 'Boss Name', 'Item', and 'GP' columns)."

        if len(drop_list_text) > 4096:
            drop_list_text = drop_list_text[:4090] + "...\n(List too long to display)"

        embed.description = drop_list_text
        return embed

    def _format_gp(self, gp_value_str: str) -> str:
        """Formats a GP string into M (Million) or K (Thousand)."""
        try:
            gp = int(str(gp_value_str).replace(',', ''))
        except ValueError:
            return gp_value_str

        if gp >= 1_000_000:
            if (gp % 1_000_000) == 0:
                return f"{gp // 1_000_000}M"
            else:
                return f"{gp / 1_000_000:.1f}M"
        elif gp >= 1_000:
            if (gp % 1_000) == 0:
                return f"{gp // 1_000}K"
            else:
                return f"{gp / 1_000:.1f}K"
        else:
            return f"{gp:,}"

    def clear_flag_column(self, team_name: str, column_name: str):
        """Helper to quickly clear a status flag from the TeamData sheet."""
        try:
            records = self.team_data_sheet.get_all_records()
            headers = list(records[0].keys())
            if column_name not in headers:
                return
                
            col_idx = headers.index(column_name) + 1
            for idx, r in enumerate(records, start=2):
                if r.get("Team", "").strip() == team_name:
                    self.team_data_sheet.update_cell(idx, col_idx, "") # Clear the cell
                    break
        except Exception as e:
            print(f"❌ Error clearing {column_name} flag for {team_name}: {e}")
    
    @app_commands.command(name="show_drops", description="Show available drops and prices for your current tile.")
    @app_commands.checks.has_any_role(*TEAM_ROLES)
    async def show_drops(self, interaction: Interaction):
        team_name = None
        for role in interaction.user.roles:
            if role.name in TEAM_ROLES:
                team_name = role.name
                break
        
        if not team_name:
            await interaction.response.send_message("You are not on a team.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=False)
        
        try:
            team_data = self.get_team_data(team_name)
            if not team_data:
                await interaction.followup.send("Could not retrieve your team's data.", ephemeral=True)
                return

            position = int(team_data.get("Position", 0))

            try:
                embed = self.build_show_drops_embed_for_tile(position)
            except Exception as e:
                print(f"Error fetching ItemValues: {e}")
                await interaction.followup.send("Error fetching item data from the sheet.", ephemeral=True)
                return

            if not embed:
                await interaction.followup.send("There are no special boss drops on this tile.", ephemeral=False)
                return

            await interaction.followup.send(embed=embed, ephemeral=False)

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)
            traceback.print_exc()

    @app_commands.command(name="monopoly_help", description="Show the help and rules for the Monopoly event.")
    async def monopoly_help(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            embed1 = discord.Embed(
                title="How to Play (The Basics)",
                description=(
                    "The whole game runs on drop submissions. Here's the loop:\n"
                    "1. **Submit a Drop:** A team member uses /submit_drop in the #drop-submission channel\n"
                    "2. **Get Approved:** Event Staff checks it out and approves it.\n"
                    "3. **Get GP & a Roll:** Once it's approved, two things happen:\n"
                    "    - Your team gets GP for the drop.\n"
                    "    - Your team gets one roll\n"
                    "4. **Use Your Roll:** Your team's Captain heads to your team channel and uses the /roll command.\n"
                    "5. **Move:** The bot rolls a 1-6, and your team moves on the board.\n"
                    "6. **Repeat:** Keep submitting those drops to get more rolls!"
                ),
                color=discord.Color.green()
            )
            
            embed2 = discord.Embed(
                title="Game Commands",
                color=discord.Color.green()
            )
            embed2.add_field(
                name="For Team Captains Only!",
                value=(
                    "**/use-card:** Lets you see and use the cards your team is holding.\n"
                    "**/buy-house:** Landed on a tile? Use this to buy a house for it (up to 4).\n"
                    "**/customize:** Change your character's icon and color!"
                ),
                inline=False
            )
            embed2.add_field(
                name="For Everyone on the Team!",
                value=(
                    "**/roll:** Uses one of your team's saved-up rolls to move your piece.\n"
                    "**/stats:** View your team's status, GP, and position.\n"
                    "**/gp:** Curious about your GP? Use this to check the team's total.\n"
                    "**/cards:** See all the cool cards your team is currently holding.\n"
                    "**/show_drops:** Shows every drop available for the tile you're on.\n"
                    "**/submit_drop:** Use this in your team channel to submit a drop."
                ),
                inline=False
            )
            
            await interaction.followup.send(embeds=[embed1, embed2], ephemeral=False)
        
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)
            traceback.print_exc()
    
    @app_commands.command(name="customize", description="Open the customization panel for your team")
    async def customize(self, interaction: discord.Interaction):
        if str(interaction.channel_id) not in TEAM_CHANNEL_IDS_AS_STR:
            await interaction.response.send_message(
                "❌ You can only use this command in your team's channel.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)
        team_name = self.get_team(interaction.user) or "*No team*"
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self.log_command,
            interaction.user.name,
            "/customize",
            {"team": team_name}
        )
        
        await interaction.followup.send(
            "🎨 Your customization request has been sent. The game board will update shortly.", ephemeral=True
        )

    @app_commands.command(name="gp", description="Check your team's current GP balance.")
    async def gp(self, interaction: discord.Interaction):
        if str(interaction.channel_id) not in TEAM_CHANNEL_IDS_AS_STR:
            await interaction.response.send_message(
                "❌ You can only use this command in your team's channel.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=False)  
        team_name = self.get_team(interaction.user)
        if not team_name:
            await interaction.followup.send("❌ You must be on a team to check GP.", ephemeral=True)
            return
        try:
            records = self.team_data_sheet.get_all_records()
            team_gp = 0
            found_team = False
            for record in records:
                if record.get("Team") == team_name:
                    team_gp = int(record.get("GP", 0) or 0)
                    found_team = True
                    break
            if not found_team:
                await interaction.followup.send(f"❌ Could not find data for **{team_name}**.", ephemeral=True)
                return
            embed = discord.Embed(
                title=f"<:MaxCash:1347684049040183427> {team_name} Team Status",
                color=discord.Color.gold()
            )
            embed.add_field(
                name="GP Balance",
                value=f"**{team_gp:,} GP**",
                inline=False
            )
            await interaction.followup.send(embed=embed)
        except Exception as e:
            print(f"❌ Error in /gp command: {e}")
            await interaction.followup.send("❌ An error occurred while fetching GP balance.", ephemeral=True)

    
    
    @app_commands.command(name="stats", description="Show GP, Go Passes, and Houses Owned for all teams.")
    async def stats(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        try:
            # 1. Fetch data snapshot concurrently (Prevents bot from hanging)
            records = await asyncio.to_thread(self.team_data_sheet.get_all_records)
            if not records:
                await interaction.followup.send("❌ Team data is unavailable.", ephemeral=True)
                return
            
            gp_list = []
            go_passes_list = []
            houses_list = [] # Tracker for the new Houses column

            for record in records:
                team_name = record.get("Team", "")
                if not team_name: 
                    continue # Skip empty rows
                
                # Format GP
                team_gp_str = str(record.get("GP", 0)).replace(',', '').strip()
                team_gp = int(team_gp_str) if team_gp_str and team_gp_str.lstrip('-').isdigit() else 0
                
                # Format Go Passes
                team_passes_str = str(record.get("Go Passes", 0)).replace(',', '').strip()
                team_passes = int(team_passes_str) if team_passes_str and team_passes_str.lstrip('-').isdigit() else 0
                
                # Format Houses Owned (New Column M)
                team_houses_str = str(record.get("Houses Owned", 0)).replace(',', '').strip()
                team_houses = int(team_houses_str) if team_houses_str and team_houses_str.lstrip('-').isdigit() else 0
                
                gp_list.append({"team": team_name, "value": team_gp})
                go_passes_list.append({"team": team_name, "value": team_passes})
                houses_list.append({"team": team_name, "value": team_houses})
                
            # 2. Sort all lists descending
            gp_list.sort(key=lambda x: x["value"], reverse=True)
            go_passes_list.sort(key=lambda x: x["value"], reverse=True)
            houses_list.sort(key=lambda x: x["value"], reverse=True)

            # 3. Build outputs
            gp_output = ""
            for i, entry in enumerate(gp_list, 1):
                gp_output += f"**{i}. {entry['team']}**: {entry['value']:,}\n"

            passes_output = ""
            for i, entry in enumerate(go_passes_list, 1):
                passes_output += f"**{i}. {entry['team']}**: {entry['value']}\n"

            houses_output = ""
            for i, entry in enumerate(houses_list, 1):
                houses_output += f"**{i}. {entry['team']}**: {entry['value']}\n"

            # 4. Construct Embed
            embed = discord.Embed(
                title="🌐 Monopoly Board Leaderboard",
                description="Current progress stats for all teams.",
                color=discord.Color.blue()
            )
            
            # Using inline=True makes the 3 leaderboards sit side-by-side nicely
            if gp_output:
                embed.add_field(name="<:MaxCash:1347684049040183427> GP Holdings", value=gp_output, inline=True)
                
            if passes_output:
                embed.add_field(name="🚶 Go Passes", value=passes_output, inline=True)

            if houses_output:
                embed.add_field(name="<:houseicon:1438085020156821555> Houses Owned", value=houses_output, inline=True)
                
            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"❌ Error in /stats command: {e}")
            traceback.print_exc()
            await interaction.followup.send("❌ An error occurred while fetching leaderboard data.", ephemeral=True)

    @app_commands.command(name="buy_house", description="Attempt to buy a house on your current tile.")
    async def buy_house(self, interaction: discord.Interaction):
        if str(interaction.channel_id) not in TEAM_CHANNEL_IDS_AS_STR:
            await interaction.response.send_message("❌ You can only use this command in your team's channel.", ephemeral=True)
            return
        if not self.has_event_captain_role(interaction.user):
            await interaction.response.send_message("❌ Only the Event Captain can use this command.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=False)
        team_name = self.get_team(interaction.user)
        if not team_name:
            await interaction.followup.send("❌ You must be on a team to buy a house.", ephemeral=True)
            return

        try:
            # 1. IMMEDIATE CHECK & LOCK
            bought_flag = await asyncio.to_thread(self.get_bought_house_flag, team_name)
            if bought_flag.lower() == "yes":
                await interaction.followup.send("❌ You have already purchased a house this turn. Roll again to buy another.", ephemeral=True)
                return
            
            # Set flag to 'yes' immediately to block concurrent/spam clicks
            await asyncio.to_thread(self.set_bought_house_flag, team_name, "yes")

            COST_MAP = {0: 25_000_000, 1: 50_000_000, 2: 100_000_000, 3: 200_000_000}
            
            # 2. DATA FETCHING
            team_data = await asyncio.to_thread(self.team_data_sheet.get_all_records)
            house_data = await asyncio.to_thread(self.house_data_sheet.get_all_records)
            
            team_info = next((r for r in team_data if r.get("Team") == team_name), None)
            if not team_info:
                await asyncio.to_thread(self.set_bought_house_flag, team_name, "no") 
                await interaction.followup.send("❌ Could not find team data.", ephemeral=True)
                return

            current_pos = int(team_info.get("Position", -1))
            current_gp = int(str(team_info.get("GP", 0)).replace(",", ""))
            
            # 3. HOUSE VALIDATION
            prop_index = -1
            prop_data = None
            for idx, row in enumerate(house_data, start=2):
                if int(row.get("Tile", -1)) == current_pos:
                    prop_data = row
                    prop_index = idx
                    break

            if not prop_data:
                await asyncio.to_thread(self.set_bought_house_flag, team_name, "no") 
                await interaction.followup.send("❌ This tile is not a buyable property.", ephemeral=True)
                return

            owner = prop_data.get("OwnerTeam", "").strip()
            if owner and owner != team_name:
                await asyncio.to_thread(self.set_bought_house_flag, team_name, "no") 
                await interaction.followup.send(f"❌ This property is owned by **{owner}**.", ephemeral=True)
                return

            house_count = int(prop_data.get("HouseCount", 0) or 0)
            if house_count >= 4:
                await asyncio.to_thread(self.set_bought_house_flag, team_name, "no") 
                await interaction.followup.send("❌ Max houses (4) reached on this tile.", ephemeral=True)
                return

            cost = COST_MAP.get(house_count, 999_999_999)
            if current_gp < cost:
                await asyncio.to_thread(self.set_bought_house_flag, team_name, "no") 
                await interaction.followup.send(f"❌ Not enough GP. Need **{cost:,}**, but you have **{current_gp:,}**.", ephemeral=True)
                return

            # 4. EXECUTE PURCHASE
            headers = list(team_data[0].keys())
            gp_col = headers.index("GP") + 1
            team_row_in_sheet = team_data.index(team_info) + 2

            # Perform the updates (background threads)
            await asyncio.to_thread(self.house_data_sheet.update_cell, prop_index, 3, team_name) 
            await asyncio.to_thread(self.house_data_sheet.update_cell, prop_index, 4, house_count + 1) 
            await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_in_sheet, gp_col, current_gp - cost)

            # --> NEW: Sync the Houses Owned column (Column M) <--
            await asyncio.to_thread(self.sync_houses_owned, team_name)

            # Output message with your custom emoji
            buy_msg = f"<:houseicon:1438085020156821555> **{team_name}** bought a house on tile **{current_pos}** for **{cost:,} GP**!"
            await interaction.followup.send(buy_msg)
            await self.mirror_to_game_log(interaction.channel, content=buy_msg)

        except Exception as e:
            print(f"❌ Error in /buy_house: {e}")
            await asyncio.to_thread(self.set_bought_house_flag, team_name, "no")
            await interaction.followup.send("❌ An error occurred. Please try again.", ephemeral=True)

    @app_commands.command(name="submitdrop", description="Submit a boss drop for review")
    @app_commands.describe(
        screenshot="Attach a screenshot of the drop",
        submitted_for="User you are submitting the drop for (optional)",
    )
    async def submitdrop(self, interaction: discord.Interaction, screenshot: discord.Attachment, submitted_for: Optional[discord.Member] = None):
        try:
            await interaction.response.defer(ephemeral=True)
        except discord.NotFound:
            print("❌ Interaction not found. (Original timeout)")
            return
        except discord.errors.InteractionResponded:
            print("❌ Interaction already responded to. (Likely >3s lag before defer)")
            return
            
        if submitted_for is None:
            submitted_for = interaction.user

        await interaction.followup.send(
            content=f"Submitting drop for {submitted_for.display_name}. Select the boss you received the drop from:",
            view=self.BossSelectView(cog=self, submitting_user=interaction.user, submitted_for=submitted_for, screenshot_url=screenshot.url),
            ephemeral=True
        )

    async def team_receives_card(self, team_name: str, card_type: str, team_channel: discord.TextChannel):
        card_sheet = self.chance_sheet if card_type == "Chance" else self.chest_sheet
        try:
            # 1. Fetch all records asynchronously
            rows = await asyncio.to_thread(card_sheet.get_all_records)
            if not rows:
                print(f"⚠️ No cards found in {card_type} sheet.")
                return

            # 2. Find eligible cards (cards this team doesn't already hold)
            eligible_cards = []
            for i, row in enumerate(rows, start=2):
                held_by = str(row.get("Held By Team", ""))
                # Split by comma to ensure exact team name matching
                teams_holding = [t.strip() for t in held_by.split(',') if t.strip()]
                
                if team_name not in teams_holding:
                    eligible_cards.append({"index": i, "data": row, "teams_holding": teams_holding})

            if not eligible_cards:
                await team_channel.send(f"❗ **{team_name}** tried to draw a {card_type} card, but they already hold every available card in the deck!")
                return

            # 3. Pick a random eligible card
            chosen_card = random.choice(eligible_cards)
            card_row_index = chosen_card["index"]
            card_data = chosen_card["data"]
            teams_holding = chosen_card["teams_holding"]
            
            card_name = card_data.get("Name", "Unknown Card")
            card_text = card_data.get("Card Text", "")
            
            new_roll = None

            # 4. Handle Wildcards (Dice Rolls inside cards)
            if "%d6" in card_text or "%d3" in card_text:
                if "%d6" in card_text:
                    new_roll = random.randint(1, 6)
                elif "%d3" in card_text:
                    new_roll = random.randint(1, 3)

                # Safely update wildcard JSON without erasing other teams
                wildcard_str = str(card_data.get("Wildcard", "{}"))
                if not wildcard_str.strip():
                    wildcard_str = "{}"
                    
                try:
                    wildcard_data = json.loads(wildcard_str)
                except Exception:
                    wildcard_data = {}

                wildcard_data[team_name] = new_roll
                
                await asyncio.to_thread(
                    card_sheet.update_cell, 
                    card_row_index, 
                    4, # Column D (Wildcard)
                    json.dumps(wildcard_data)
                )

            # 5. Append team to 'Held By Team' (Preserving other teams)
            teams_holding.append(team_name)
            await asyncio.to_thread(
                card_sheet.update_cell, 
                card_row_index, 
                3, # Column C (Held By Team)
                ", ".join(teams_holding)
            )

            # 6. Format and send output
            card_text_display = card_text
            if new_roll is not None:
                card_text_display = card_text_display.replace("%d6", str(new_roll)).replace("%d3", str(new_roll))

            card_emoji = CARD_EMOJIS.get(card_name, CARD_EMOJIS.get(card_type, "🃏"))

            embed = discord.Embed(
                title=f"{card_emoji} {card_type} Card Drawn!",
                description=f"**{team_name}** drew **{card_name}**!\n\n> {card_text_display}",
                color=discord.Color.gold() if card_type == "Chest" else discord.Color.blue()
            )
            await team_channel.send(embed=embed) 

        except Exception as e:
            print(f"❌ Error in team_receives_card: {e}")
            traceback.print_exc()


    def get_held_cards(self, sheet_obj, team_name: str):
        cards = []
        try:
            data = sheet_obj.get_all_values() 
            if not data:
                return []
            headers = data[0]
            
            try:
                name_col = headers.index("Name")
                text_col = headers.index("Card Text")
                held_by_col = headers.index("Held By Team")
                wildcard_col = headers.index("Wildcard")
            except ValueError as e:
                print(f"❌ Missing column in {sheet_obj.title}: {e}")
                return []

            for idx, row in enumerate(data[1:], start=2):
                if len(row) <= max(name_col, text_col, held_by_col, wildcard_col):
                    continue
                    
                held_by = str(row[held_by_col] or "")
                
                if team_name in held_by:
                    card_text = str(row[text_col] or "")
                    card_name = str(row[name_col] or "")
                    
                    wildcard_data_str = str(row[wildcard_col] or "{}")
                    if wildcard_data_str != "{}" and wildcard_data_str:
                        try:
                            wildcard_data = json.loads(wildcard_data_str)
                            stored_val = wildcard_data.get(team_name)
                            
                            if stored_val:
                                if isinstance(stored_val, int):
                                    card_text = card_text.replace("%d6", str(stored_val))
                                    card_text = card_text.replace("%d3", str(stored_val))
                                elif isinstance(stored_val, str) and stored_val.strip() == "active": 
                                    card_text += " **(ACTIVE)**"
                                    
                        except Exception as e:
                            print(f"❌ Error parsing wildcard JSON for {team_name}: {wildcard_data_str} | {e}")
                            
                    cards.append({
                        "row_index": idx,
                        "name": card_name,
                        "text": card_text,
                    })
        except Exception as e:
            print(f"❌ Error in get_held_cards: {e}")
        return cards

    def check_and_consume_vengeance(self, target_team_name: str) -> bool:
        try:
            for sheet_obj in (self.chest_sheet, self.chance_sheet):
                data = sheet_obj.get_all_values()
                if not data:
                    continue

                headers = data[0]
                if "Name" not in headers or "Held By Team" not in headers or "Wildcard" not in headers:
                    continue

                name_col = headers.index("Name")
                held_by_col = headers.index("Held By Team")
                wildcard_col = headers.index("Wildcard")

                for i, row in enumerate(data[1:], start=2):
                    if len(row) <= max(name_col, held_by_col, wildcard_col):
                        continue
                    if str(row[name_col]).strip() != "Vengeance":
                        continue

                    try:
                        wildcard_data = json.loads(row[wildcard_col] or "{}")
                    except Exception:
                        wildcard_data = {}

                    if wildcard_data.get(target_team_name) == "active":
                        wildcard_data.pop(target_team_name, None)
                        sheet_obj.update_cell(i, wildcard_col + 1, json.dumps(wildcard_data))

                        held_by_str = str(sheet_obj.cell(i, held_by_col + 1).value or "")
                        teams = [t.strip() for t in held_by_str.split(",") if t.strip()]
                        if target_team_name in teams:
                            teams.remove(target_team_name)
                        sheet_obj.update_cell(i, held_by_col + 1, ", ".join(teams))

                        print(f"Consumed Vengeance for {target_team_name} from {sheet_obj.title}")
                        return True

            return False

        except Exception as e:
            print(f"Error in check_and_consume_vengeance: {e}")
            return False
        
    def check_and_consume_redemption(self, target_team_name: str) -> bool:
        """
        Checks if a target team has Redemption active.
        This is a CHANCE card.
        If yes, consumes it (clears wildcard AND held by) and returns True.
        If no, returns False.
        """
        try:
            chance_cards_data = self.chance_sheet.get_all_values()
            if not chance_cards_data:
                return False
                
            headers = chance_cards_data[0]
            name_col = headers.index("Name")
            held_by_col = headers.index("Held By Team")
            wildcard_col = headers.index("Wildcard")
            
            redemption_row_index = -1
            redemption_wildcard_data = {}
            
            for i, row in enumerate(chance_cards_data[1:], start=2):
                if len(row) > name_col and row[name_col] == "Redemption":
                    redemption_row_index = i
                    try:
                        wildcard_str = row[wildcard_col] or "{}"
                        redemption_wildcard_data = json.loads(wildcard_str)
                    except:
                        redemption_wildcard_data = {}
                    break
            
            if redemption_row_index == -1:
                print("❗ Redemption card not found on chance sheet.")
                return False

            team_status = redemption_wildcard_data.get(target_team_name)
            if team_status and isinstance(team_status, str) and team_status.strip() == "active":
                del redemption_wildcard_data[target_team_name]
                self.chance_sheet.update_cell(redemption_row_index, wildcard_col + 1, json.dumps(redemption_wildcard_data))
                
                held_by_str = str(self.chance_sheet.cell(redemption_row_index, held_by_col + 1).value or "")
                teams = [t.strip() for t in held_by_str.split(',') if t.strip()]
                if target_team_name in teams:
                    teams.remove(target_team_name)
                self.chance_sheet.update_cell(redemption_row_index, held_by_col + 1, ", ".join(teams))
                
                print(f"✅ Consumed Redemption for {target_team_name}")
                return True
                
        except Exception as e:
            print(f"❌ Error in check_and_consume_redemption: {e}")
            
        return False

    def check_and_consume_elder_maul(self, target_team_name: str) -> bool:
        """
        Checks if a target team has Elder Maul active.
        Consolidates API calls and handles removal in a single threaded flow.
        """
        try:
            # 1. Single Fetch
            chance_cards_data = self.chance_sheet.get_all_values()
            if not chance_cards_data:
                return False
                
            headers = chance_cards_data[0]
            name_col = headers.index("Name")
            held_by_col = headers.index("Held By Team")
            wildcard_col = headers.index("Wildcard")
            
            # 2. Find the card and the team status in memory
            for i, row in enumerate(chance_cards_data[1:], start=2):
                if len(row) > name_col and row[name_col] == "Elder Maul":
                    
                    # Parse wildcard for team status
                    try:
                        wildcard_str = row[wildcard_col] or "{}"
                        card_wildcard_data = json.loads(wildcard_str)
                    except:
                        card_wildcard_data = {}

                    team_status = card_wildcard_data.get(target_team_name)
                    
                    if team_status and isinstance(team_status, str) and team_status.strip() == "active":
                        # --- CONSUMPTION LOGIC ---
                        # Remove from wildcard
                        del card_wildcard_data[target_team_name]
                        self.chance_sheet.update_cell(i, wildcard_col + 1, json.dumps(card_wildcard_data))
                        
                        # Remove from Held By Team (using the row data we already have)
                        held_by_str = str(row[held_by_col] or "")
                        teams = [t.strip() for t in held_by_str.split(',') if t.strip()]
                        if target_team_name in teams:
                            teams.remove(target_team_name)
                        
                        self.chance_sheet.update_cell(i, held_by_col + 1, ", ".join(teams))
                        
                        print(f"✅ Consumed Elder Maul for {target_team_name}")
                        return True
            
            return False
                
        except Exception as e:
            print(f"❌ Error in check_and_consume_elder_maul: {e}")
            return False

    def check_and_consume_alchemy(self, team_name: str) -> (int, str):
        """
        Checks if a team has an active Alchemy card.
        If yes, consumes it and returns the multiplier (2 or 3) and card name.
        If no, returns 1 and None.
        """
        try:
            chance_cards_data = self.chance_sheet.get_all_values()
            if not chance_cards_data:
                return 1, None
                
            headers = chance_cards_data[0]
            name_col = headers.index("Name")
            held_by_col = headers.index("Held By Team")
            wildcard_col = headers.index("Wildcard")
            
            for i, row in enumerate(chance_cards_data[1:], start=2):
                if len(row) <= max(name_col, held_by_col, wildcard_col):
                    continue
                    
                card_name = row[name_col]
                if card_name not in ("Low Alchemy", "High Alchemy"):
                    continue

                try:
                    wildcard_str = row[wildcard_col] or "{}"
                    wildcard_data = json.loads(wildcard_str)
                except:
                    wildcard_data = {}

                team_status = None
                found_key = None
                for key, value in wildcard_data.items():
                    if key.strip() == team_name:
                        team_status = value
                        found_key = key
                        break
                
                if team_status and isinstance(team_status, str) and team_status.strip() == "active":
                    multiplier = 3 if card_name == "High Alchemy" else 2
                    
                    del wildcard_data[found_key]
                    self.chance_sheet.update_cell(i, wildcard_col + 1, json.dumps(wildcard_data)) # +1 for 1-based index
                    
                    held_by_str = str(self.chance_sheet.cell(i, held_by_col + 1).value or "")
                    teams = [t.strip() for t in held_by_str.split(',') if t.strip()]
                    if team_name in teams:
                        teams.remove(team_name)
                    self.chance_sheet.update_cell(i, held_by_col + 1, ", ".join(teams))
                    
                    print(f"✅ Consumed {card_name} for {team_name}, applying x{multiplier} GP multiplier.")
                    return multiplier, card_name
                
        except Exception as e:
            print(f"❌ Error in check_and_consume_alchemy: {e}")
            
        return 1, None

    def clear_all_active_statuses(self, team_name: str):
        """
        Finds and clears all "active" statuses for a given team
        from both card sheets. This is called at the start of a team's turn.
        
        🔹 FIXED: Will no longer clear Alchemy cards, as those are
        consumed on use, not at the start of a turn.
        """
        print(f"❗ Clearing all active statuses for {team_name}...")
        sheets_to_check = [self.chance_sheet, self.chest_sheet]
        cards_cleared = []

        for sheet_obj in sheets_to_check:
            try:
                data = sheet_obj.get_all_values()
                if not data:
                    continue
                    
                headers = data[0]
                name_col = headers.index("Name")
                held_by_col = headers.index("Held By Team")
                wildcard_col = headers.index("Wildcard")

                for i, row in enumerate(data[1:], start=2):
                    if len(row) <= max(name_col, held_by_col, wildcard_col):
                        continue
                    
                    card_name = row[name_col]
                    if card_name in ("Low Alchemy", "High Alchemy"):
                        continue
                    
                    wildcard_str = str(row[wildcard_col] or "{}")
                    if "active" not in wildcard_str:
                        continue

                    try:
                        wildcard_data = json.loads(wildcard_str)
                    except:
                        wildcard_data = {}

                    team_status = None
                    found_key = None
                    for key, value in wildcard_data.items():
                        if key.strip() == team_name:
                            team_status = value
                            found_key = key
                            break
                    
                    if team_status and isinstance(team_status, str) and team_status.strip() == "active":
                        card_name = row[name_col]
                        print(f"        > Found active card: {card_name}. Consuming...")
                        
                        del wildcard_data[found_key]
                        sheet_obj.update_cell(i, wildcard_col + 1, json.dumps(wildcard_data))
                        
                        held_by_str = str(row[held_by_col] or "")
                        teams = [t.strip() for t in held_by_str.split(',') if t.strip()]
                        if team_name in teams:
                            teams.remove(team_name)
                        sheet_obj.update_cell(i, held_by_col + 1, ", ".join(teams))
                        
                        cards_cleared.append(card_name)

            except Exception as e:
                print(f"❌ Error in clear_all_active_statuses for sheet {sheet_obj.title}: {e}")
                
        return cards_cleared

    def sync_houses_owned(self, team_name: str):
        """
        Calculates the total number of houses a team owns across all properties 
        in HouseData and updates the 'Houses Owned' column in TeamData.
        """
        try:
            # 1. Tally up houses from HouseData
            house_records = self.house_data_sheet.get_all_records()
            total_houses = 0
            
            for row in house_records:
                if str(row.get("OwnerTeam", "")).strip() == team_name:
                    count_str = str(row.get("HouseCount", "0")).strip()
                    if count_str.isdigit():
                        total_houses += int(count_str)
            
            # 2. Update the TeamData sheet
            team_records = self.team_data_sheet.get_all_records()
            headers = self.team_data_sheet.row_values(1)
            
            if "Houses Owned" not in headers:
                print("❌ 'Houses Owned' column not found in TeamData. Please check the header name.")
                return
                
            houses_col_idx = headers.index("Houses Owned") + 1
            
            for idx, record in enumerate(team_records, start=2):
                if record.get("Team") == team_name:
                    self.team_data_sheet.update_cell(idx, houses_col_idx, total_houses)
                    print(f"✅ Synced {total_houses} total houses for {team_name} in TeamData.")
                    return
                    
        except Exception as e:
            print(f"❌ Error syncing houses owned for {team_name}: {e}")

    async def check_and_award_card_on_land(self, team_name: str, new_pos: int, reason: str = "landing on"):
        """
        Handles post-move checks:
        1. Grants a free roll if landing on a special tile with 0 rolls left.
        2. Awards Chest/Chance cards with correct emojis.
        """
        team_channel = self.get_team_channel(team_name)
        if not team_channel:
            return

        is_in_jail = await asyncio.to_thread(self.get_jail_status, team_name)
        is_just_visiting = (new_pos == JAIL_TILE and is_in_jail == "no")

        # 1. Roll Protection Logic
        if new_pos in ROLL_GRANTING_TILES or is_just_visiting:
            try:
                rolls_available = self.get_team_rolls(team_name)
                
                if rolls_available <= 0:
                    # We update the sheet first
                    self.increment_rolls_available(team_name)
                    
                    try:
                        tile_name = self.get_tile_name_for_display(new_pos)
                        if is_just_visiting:
                            tile_name = "Jail (Just Visiting) - Nex, Gauntlet"
                            
                        roll_embed = discord.Embed(
                            title="🎲 Free Roll Granted!",
                            description=f"**{team_name}** reached **{tile_name}** with no rolls remaining. A free roll has been granted!",
                            color=discord.Color.yellow()
                        )
                        await team_channel.send(embed=roll_embed)
                        await self.mirror_to_game_log(team_channel, embed=roll_embed)
                        print(f"✅ Roll message sent for {team_name}")
                    except Exception as msg_err:
                        print(f"⚠️ Sheet updated, but Discord message failed: {msg_err}")

            except Exception as e:
                print(f"❌ Error during roll protection check: {e}")

        # Chest Emoji
        if new_pos in CHEST_TILES:
            print(f"📦 {team_name} triggered CHEST on tile {new_pos}")
            await self.team_receives_card(team_name, "Chest", team_channel)
            
        # Chance Emoji
        elif new_pos in CHANCE_TILES:
            print(f"❓ {team_name} triggered CHANCE on tile {new_pos}")
            await self.team_receives_card(team_name, "Chance", team_channel)

        pass

    @app_commands.command(name="cards", description="Show all cards currently held by your team.")
    async def cards(self, interaction: discord.Interaction):
        if str(interaction.channel_id) not in TEAM_CHANNEL_IDS_AS_STR:
            await interaction.response.send_message(
                "❌ You can only use this command in your team's channel.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)
        team_name = self.get_team(interaction.user)
        if not team_name:
            await interaction.followup.send("❌ You don't have a team role assigned.", ephemeral=True)
            return

        chest_cards = self.get_held_cards(self.chest_sheet, team_name)
        chance_cards = self.get_held_cards(self.chance_sheet, team_name)

        if not chest_cards and not chance_cards:
            await interaction.followup.send("❌ Your team holds no cards.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"{team_name}'s Cards",
            color=discord.Color.purple(),
            description="Cards currently held by your team:\n"
        )

        if chest_cards:
            for i, card in enumerate(chest_cards, start=1):
                emoji = CARD_EMOJIS.get(card['name'], "<:chest:1437979807362191441>")
                embed.add_field(
                    name=f"{emoji} [{i}] Chest Card — {card['name']}",
                    value=f"```{card['text']}```",
                    inline=False
                )

        offset = len(chest_cards)
        if chance_cards:
            for i, card in enumerate(chance_cards, start=1):
                emoji = CARD_EMOJIS.get(card['name'], "<:questioning:1287623035381350441>")
                embed.add_field(
                    name=f"{emoji} [{i+offset}] Chance Card — {card['name']}",
                    value=f"```{card['text']}```",
                    inline=False
                )

        await interaction.followup.send(embed=embed, ephemeral=True)

    class CardTargetView(discord.ui.View):
        def __init__(self, cog, user_team: str, valid_targets: list, card_name: str, card_action: str, extra_data: dict = None):
            super().__init__(timeout=180)
            self.cog = cog
            self.user_team = user_team
            self.card_name = card_name
            self.card_action = card_action
            self.extra_data = extra_data or {} 
    
            options = []
            for target in valid_targets:
                desc = None
                
                # If Rogue's Gloves, show the eligible card count directly in the dropdown menu
                if card_action == "rogues_gloves":
                    try:
                        # We can pull the exact count directly from the memory we passed in!
                        stealable = self.extra_data.get("stealable_cards", [])
                        target_count = len([c for c in stealable if c["victim_team"] == target])
                        desc = f"Holding {target_count} eligible card(s)"
                    except:
                        desc = "Card count unknown"
                        
                options.append(discord.SelectOption(label=target, description=desc, value=target))
    
            select = discord.ui.Select(
                placeholder=f"Select target for {card_name}...", 
                options=options
                # Removed custom_id to prevent conflicts if multiple cards are used at once
            )
            select.callback = self.select_callback
            self.add_item(select)
    
        async def select_callback(self, interaction: discord.Interaction):
            # Security: Only let the captain of the team that used the card click the dropdown
            if self.cog.get_team(interaction.user) != self.user_team:
                await interaction.response.send_message("❌ You cannot make selections for this team.", ephemeral=True)
                return
    
            target_team = self.children[0].values[0]
            
            # Disable the dropdown so it can't be clicked twice
            self.children[0].disabled = True
            await interaction.response.edit_message(view=self)
    
            await self.cog.execute_targeted_card_effect(interaction, self.user_team, target_team, self.card_name, self.card_action, self.extra_data)
    
    @app_commands.command(name="use_card", description="Use a held card by its index from /cards")
    @app_commands.describe(index="The index of the card you want to use (starts at 1)")
    async def use_card(self, interaction: discord.Interaction, index: int):
        if str(interaction.channel_id) not in TEAM_CHANNEL_IDS_AS_STR:
            await interaction.response.send_message(
                "❌ You can only use this command in your team's channel.", ephemeral=True
            )
            return
            
        if not self.has_event_captain_role(interaction.user):
            await interaction.response.send_message(
                "❌ Only the Event Captain can use this command.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=False)  
        team_name = self.get_team(interaction.user)
        if not team_name:
            await interaction.followup.send("❌ You are not on a team.", ephemeral=True)
            return

        try:
            team_data_headers = self.team_data_sheet.row_values(1)
            gp_col_index = team_data_headers.index("GP") + 1
            teleblocked_col_index = team_data_headers.index("Teleblocked") + 1
        except ValueError as e:
            if 'GP' in str(e):
                await interaction.followup.send("❌ Data sheet error: Missing 'GP' column.", ephemeral=True)
            elif 'Teleblocked' in str(e):
                await interaction.followup.send("❌ Data sheet error: Missing 'Teleblocked' column. Please add it.", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Data sheet error: {e}", ephemeral=True)
            return

        try:
            # 1. Fetch team data so team_info exists!
            all_records = await asyncio.to_thread(self.team_data_sheet.get_all_records)
            team_info = next((r for r in all_records if r.get("Team") == team_name), None)
            
            if not team_info:
                await interaction.followup.send(f"❌ Could not find data for **{team_name}**.", ephemeral=True)
                return

            # 2. Check if silenced by the Mime
            is_silenced = str(team_info.get("Silenced", "no")).strip().lower()
            if is_silenced == "yes":
                await interaction.followup.send("❌ 🎭 **You are Silenced!** The Mime's aura prevents you from using any cards. You must roll the dice to break the silence.", ephemeral=True)
                return
            
            # 3. Check normal card limits (and allow Double Card bypass)
            has_double_card = str(team_info.get("Double Card", "no")).strip().lower() == "yes"
            used_card_flag = str(team_info.get("Used Card This Turn", "no")).strip().lower()
            
            if used_card_flag == "yes":
                if has_double_card:
                    # They have the buff! Clear it so they can't use 3 cards, but let them pass.
                    asyncio.create_task(asyncio.to_thread(self.clear_flag_column, team_name, "Double Card"))
                else:
                    await interaction.followup.send("❌ You can only use one card per turn. Roll again to use another card.", ephemeral=True)
                    return
                
        except Exception as e:
            print(f"❌ Error checking team status flags: {e}")
        
        chest_cards = self.get_held_cards(self.chest_sheet, team_name)
        chance_cards = self.get_held_cards(self.chance_sheet, team_name)
        all_cards = chest_cards + chance_cards

        if index < 1 or index > len(all_cards):
            await interaction.followup.send(f"❌ Invalid card index. Use `/cards` and pick a number between 1 and {len(all_cards)}.", ephemeral=True)
            return
        
        selected_card = all_cards[index - 1]
        card_type = "Chest" if (index - 1) < len(chest_cards) else "Chance"
        card_sheet = self.chest_sheet if card_type == "Chest" else self.chance_sheet
        card_row = selected_card['row_index']
        
        card_name = selected_card['name']
        card_emoji = CARD_EMOJIS.get(card_name, "✅")
        
        stored_roll = None
        final_card_text = selected_card['text']
        
        is_status_activation = False
        embed_description = ""
        
        loop = asyncio.get_event_loop()

        try:
            wildcard_data_str = card_sheet.cell(card_row, 4).value or "{}"
            wildcard_data = {}
            team_wildcard_value = None
            try:
                wildcard_data = json.loads(wildcard_data_str)
                val = wildcard_data.get(team_name)
                if val is not None and isinstance(val, str):
                    val_str = val.strip()
                    if val_str.lstrip('-').isdigit():
                        team_wildcard_value = int(val_str)
                    else:
                        team_wildcard_value = val_str
                else:
                    team_wildcard_value = val
            except Exception as e:
                print(f"❌ Error parsing wildcard for {team_name}: {e}")

            if card_name == "Vengeance":
                if team_wildcard_value == "active":
                    await interaction.followup.send("❌ This card is already active!", ephemeral=True)
                    return
                
                wildcard_data[team_name] = "active"
                card_sheet.update_cell(card_row, 4, json.dumps(wildcard_data))
                is_status_activation = True
                
                embed_description = "> The next card effect used on your team will be rebounded."

            elif card_name == "Redemption":
                if team_wildcard_value == "active":
                    await interaction.followup.send("❌ This card is already active!", ephemeral=True)
                    return
                
                wildcard_data[team_name] = "active"
                card_sheet.update_cell(card_row, 4, json.dumps(wildcard_data))
                is_status_activation = True
                
                embed_description = "> The next negative card effect used on your team will be fizzled."

            elif card_name == "Elder Maul":
                if team_wildcard_value == "active":
                    await interaction.followup.send("❌ This card is already active!", ephemeral=True)
                    return
                
                wildcard_data[team_name] = "active"
                
                await asyncio.to_thread(
                    card_sheet.update_cell, 
                    card_row, 
                    4, 
                    json.dumps(wildcard_data)
                )
                
                is_status_activation = True
                embed_description = "> <:maul:1437979898865258668> **Elder Maul Activated!** The next negative card effect used on your team will be reduced."

            elif card_name == "Low Alchemy":
                if team_wildcard_value == "active":
                    await interaction.followup.send("❌ This card is already active!", ephemeral=True)
                    return

                wildcard_data[team_name] = "active"
                card_sheet.update_cell(card_row, 4, json.dumps(wildcard_data))
                is_status_activation = True
                
                embed_description = "> Your next drop this turn will be worth **double GP**."
                
            elif card_name == "High Alchemy":
                if team_wildcard_value == "active":
                    await interaction.followup.send("❌ This card is already active!", ephemeral=True)
                    return
                    
                wildcard_data[team_name] = "active"
                card_sheet.update_cell(card_row, 4, json.dumps(wildcard_data))
                is_status_activation = True
                
                embed_description = "> Your next drop this turn will be worth **triple GP**."
                
            elif card_name == "Vile Vigour" and isinstance(team_wildcard_value, int):
                stored_roll = team_wildcard_value
                
                # Fetch snapshot
                all_teams_data = await asyncio.to_thread(self.team_data_sheet.get_all_records)
                caster_pos = -1
                for record in all_teams_data:
                    if record.get("Team") == team_name:
                        caster_pos = int(record.get("Position", -1))
                        break
                
                if caster_pos == -1:
                    await interaction.followup.send("❌ Could not find your team's position.", ephemeral=True)
                    return

                # Calculate movement
                intended_pos = (caster_pos + stored_roll) % BOARD_SIZE
                new_pos = self.resolve_nonroll_landing_tile(intended_pos)

                await asyncio.to_thread(self.log_command, team_name, "/card_effect_set_tile", {"team": team_name, "tile": new_pos})
                
                destination_tile_name = self.get_tile_name_for_display(new_pos)
                embed_description = f"> Moved **{stored_roll}** spaces forward to the **{destination_tile_name}** tile (Tile **{new_pos}**)."
                embed_description += self.get_glider_redirect_note(intended_pos, new_pos)

                # Route through normal board triggers (Only grants rolls on Special tiles)
                await self.check_and_award_card_on_land(team_name, new_pos, "using Vile Vigour to")
                await self.auto_post_show_drops_if_boss_tile(team_name, new_pos)

            except Exception as e:
                print(f"❌ Error during card effect execution: {e}")
                await interaction.followup.send(f"❌ An error occurred: {e}", ephemeral=True)
            
            elif card_name == "Dragon Spear" and isinstance(team_wildcard_value, int):
            try:
                stored_roll = team_wildcard_value
                move_amount = -stored_roll
                
                # Fetch a fast snapshot of the data
                all_teams_data = await asyncio.to_thread(self.team_data_sheet.get_all_records)
                caster_pos = -1
                targets = []
                actual_target_pos = -1
                
                for record in all_teams_data:
                    if record.get("Team") == team_name:
                        caster_pos = int(record.get("Position", -1))
                        break
                
                if caster_pos != -1:
                    import random
                    valid_targets_data = []
                    
                    for record in all_teams_data:
                        opponent_team_name = record.get("Team")
                        if opponent_team_name == team_name:
                            continue
                        
                        opp_pos = int(record.get("Position", -1))
                        
                        # Target teams within 1 tile (ahead, behind, or same tile)
                        if abs(opp_pos - caster_pos) <= 1:
                            valid_targets_data.append((opponent_team_name, opp_pos))
                            
                    if valid_targets_data:
                        # Randomly pick exactly ONE valid target
                        chosen = random.choice(valid_targets_data)
                        targets.append(chosen[0])
                        actual_target_pos = chosen[1]
                
                if not targets:
                    await interaction.followup.send("❌ Card effect failed: No other teams are within 1 tile of you.", ephemeral=True)
                    return 

                embed_description = f"**{team_name}** automatically targeted **{targets[0]}** (Tile {actual_target_pos}) with the **Dragon Spear**!\n"
                
                for target_team in targets:
                    victim_channel = self.get_team_channel(target_team)
                    
                    # 1. Check Redemption
                    if await asyncio.to_thread(self.check_and_consume_redemption, target_team):
                        embed_description += f"> <:redemption:1437979567900987493> **{target_team}**'s Redemption activated. **Dragon Spear** fizzled.\n"
                        if victim_channel:
                            fizzle_embed = discord.Embed(
                                title="<:redemption:1437979567900987493> Redemption Activated!", 
                                description=f"**{team_name}** tried to use **Dragon Spear** on you, but your **Redemption** activated!", 
                                color=discord.Color.blue()
                            )
                            await victim_channel.send(embed=fizzle_embed)
                            await self.mirror_to_game_log(victim_channel, embed=fizzle_embed)
                        continue  
                            
                    # 2. Check Vengeance
                    if await asyncio.to_thread(self.check_and_consume_vengeance, target_team):
                        elder_maul_active = await asyncio.to_thread(self.check_and_consume_elder_maul, team_name)
                        final_move_amount = -(stored_roll // 2) if elder_maul_active else move_amount
                        maul_suffix = " (Halved by <:maul:1437979898865258668> **Elder Maul**!)" if elder_maul_active else ""
                        
                        intended_pos_after_rebound = max(0, caster_pos + final_move_amount)
                        new_pos = self.resolve_nonroll_landing_tile(intended_pos_after_rebound)
                        destination_tile_name = self.get_tile_name_for_display(new_pos)
                        glider_note = self.get_glider_redirect_note(intended_pos_after_rebound, new_pos)
                        glider_note_victim = self.get_glider_redirect_note(intended_pos_after_rebound, new_pos, second_person=True, quoted=False)
                        
                        await asyncio.to_thread(self.log_command, team_name, "/card_effect_set_tile", {"team": team_name, "tile": new_pos})
                        
                        embed_description += (
                            f"> <:venge:1438084953559797884> **{target_team}** had Vengeance! Your team was moved back "
                            f"**{abs(final_move_amount)}** tiles to the **{destination_tile_name}** tile (Tile **{new_pos}**) "
                            f"(stops at Go){maul_suffix}.\n"
                        )
                        embed_description += glider_note
                        
                        await self.check_and_award_card_on_land(team_name, new_pos, "being rebounded by Dragon Spear to")
                        await self.auto_post_show_drops_if_boss_tile(team_name, new_pos)
                        
                        skull_embed = discord.Embed(
                            title="<:venge:1438084953559797884> Vengeance Activated!", 
                            description=(f"You activated **{target_team}**'s Vengeance!\nYour team moved back **{abs(final_move_amount)}** spaces to the **{destination_tile_name}** tile (Tile **{new_pos}**)!" + glider_note_victim), 
                            color=discord.Color.dark_red()
                        )
                        await interaction.channel.send(embed=skull_embed)
                        await self.mirror_to_game_log(interaction.channel, embed=skull_embed)
                        
                        if victim_channel:
                            victim_embed = discord.Embed(
                                title="<:venge:1438084953559797884> Vengeance Activated!",
                                description=(
                                    f"**{team_name}** tried to use **Dragon Spear** on your team, but your **Vengeance** rebounded the effect!\n"
                                    f"They were moved back **{abs(final_move_amount)}** tiles to the **{destination_tile_name}** tile (Tile **{new_pos}**) (stops at Go)."
                                    + glider_note_victim
                                ),
                                color=discord.Color.dark_red()
                            )
                            await victim_channel.send(embed=victim_embed)
                            await self.mirror_to_game_log(victim_channel, embed=victim_embed)
                        continue  
                    
                    # 3. Normal Hit
                    else:
                        elder_maul_active = await asyncio.to_thread(self.check_and_consume_elder_maul, target_team)
                        final_move_amount = -(stored_roll // 2) if elder_maul_active else move_amount
                        maul_suffix = " (Halved by <:maul:1437979898865258668> **Elder Maul**!)" if elder_maul_active else ""
                        
                        target_pos = actual_target_pos 
                        intended_target_pos = max(0, target_pos + final_move_amount)
                        new_pos = self.resolve_nonroll_landing_tile(intended_target_pos)
                        glider_note = self.get_glider_redirect_note(intended_target_pos, new_pos)
                        glider_note_victim = self.get_glider_redirect_note(intended_target_pos, new_pos, second_person=True, quoted=False)
                        
                        await asyncio.to_thread(self.log_command, team_name, "/card_effect_set_tile", {"team": target_team, "tile": new_pos})
                        
                        destination_tile_name = self.get_tile_name_for_display(new_pos)
                        embed_description += f"> **{target_team}** was moved back **{abs(final_move_amount)}** tiles to the **{destination_tile_name}** tile (Tile **{new_pos}**) (stops at Go){maul_suffix}.\n"
                        embed_description += glider_note
                        
                        await self.check_and_award_card_on_land(target_team, new_pos, "being hit by Dragon Spear to")
                        await self.auto_post_show_drops_if_boss_tile(target_team, new_pos)
                        
                        if victim_channel:
                            victim_embed = discord.Embed(
                                title="<:dragonspear:1437980060567994399> You Were Hit by Dragon Spear!",
                                description=(
                                    f"**{team_name}** used **Dragon Spear** on your team.\n"
                                    f"You were moved back **{abs(final_move_amount)}** tiles to the **{self.get_tile_name_for_display(new_pos)}** tile (Tile **{new_pos}**) (stops at Go){maul_suffix}."
                                    + glider_note_victim
                                ),
                                color=discord.Color.dark_red()
                            )
                            await victim_channel.send(embed=victim_embed)
                            await self.mirror_to_game_log(victim_channel, embed=victim_embed)

                final_embed = discord.Embed(title="🃏 Dragon Spear Used!", description=embed_description, color=discord.Color.red())
                await interaction.followup.send(embed=final_embed)

                await self.remove_card(team_name, card_name)
                return
            except Exception as e:
                print(f"❌ Error in Dragon Spear block: {e}")
                return

            elif card_name == "Rogue's Gloves":
                stealable_cards = []
                chance_data = self.chance_sheet.get_all_values()
                if chance_data:
                    headers = chance_data[0]
                    name_col = headers.index("Name")
                    held_by_col = headers.index("Held By Team")
                    wildcard_col = headers.index("Wildcard")
                    
                    for i, row in enumerate(chance_data[1:], start=2):
                        if len(row) <= max(name_col, held_by_col, wildcard_col): continue
                        held_by_str = str(row[held_by_col] or "")
                        
                        if held_by_str and team_name not in held_by_str:
                            is_active = False
                            wildcard_str = str(row[wildcard_col] or "{}")
                            if wildcard_str != "{}" and wildcard_str:
                                try:
                                    import json
                                    wildcard_data_json = json.loads(wildcard_str)
                                    victim_team = held_by_str.strip() 
                                    victim_status = wildcard_data_json.get(victim_team)
                                    if victim_status and isinstance(victim_status, str) and victim_status.strip() == "active":
                                        is_active = True
                                except:
                                    pass 
                            
                            if not is_active:
                                stealable_cards.append({
                                    "sheet": self.chance_sheet,
                                    "row_index": i,
                                    "card_name": str(row[name_col]),
                                    "card_type": "Chance",
                                    "victim_team": held_by_str.strip() 
                                })
    
                chest_data = self.chest_sheet.get_all_values()
                if chest_data:
                    headers = chest_data[0]
                    name_col = headers.index("Name")
                    held_by_col = headers.index("Held By Team")
                    wildcard_col = headers.index("Wildcard")
    
                    for i, row in enumerate(chest_data[1:], start=2):
                        if len(row) <= max(name_col, held_by_col, wildcard_col): continue
                        held_by_str = str(row[held_by_col] or "")
                        
                        if held_by_str and team_name not in held_by_str:
                            all_holders = [t.strip() for t in held_by_str.split(',') if t.strip()]
                            
                            wildcard_str = str(row[wildcard_col] or "{}")
                            wildcard_data_json = {}
                            try:
                                import json
                                wildcard_data_json = json.loads(wildcard_str)
                            except:
                                pass
    
                            valid_victims = []
                            for holder in all_holders:
                                if holder == team_name: continue
                                holder_status = wildcard_data_json.get(holder)
                                if not (holder_status and isinstance(holder_status, str) and holder_status.strip() == "active"):
                                    valid_victims.append(holder)
    
                            if valid_victims:
                                import random
                                victim_team = random.choice(valid_victims) 
                                stealable_cards.append({
                                    "sheet": self.chest_sheet,
                                    "row_index": i,
                                    "card_name": str(row[name_col]),
                                    "card_type": "Chest",
                                    "victim_team": victim_team
                                })
                
                if not stealable_cards:
                    await interaction.followup.send("❌ Card effect failed: There are no eligible cards to steal.", ephemeral=True)
                    return 
    
                team_card_counts = {}
                for c in stealable_cards:
                    t = c["victim_team"]
                    team_card_counts[t] = team_card_counts.get(t, 0) + 1
    
                valid_targets = list(team_card_counts.keys())
    
                embed = discord.Embed(
                    title="🎯 Target Selection: Rogue's Gloves",
                    description="Select a team to steal from! Here is what everyone is holding:\n",
                    color=discord.Color.dark_gray()
                )
                for t, count in team_card_counts.items():
                    embed.description += f"\n• **{t}**: {count} cards"
    
                extra_memory = {
                    "stealable_cards": stealable_cards,
                    "rg_sheet": card_sheet,
                    "rg_row": card_row
                }
                view = CardTargetView(self, team_name, valid_targets, "Rogue's Gloves", "rogues_gloves", extra_data=extra_memory)
                await interaction.followup.send(embed=embed, view=view, ephemeral=False)
                return

            elif card_name == "Pickpocket":
                all_teams_data = await asyncio.to_thread(self.team_data_sheet.get_all_records)
                
                valid_targets = []
                target_gp_data = {}
                caster_record = None
    
                for record in all_teams_data:
                    current_team = record.get("Team")
                     if not current_team: continue
                    
                    try:
                        current_gp = int(str(record.get("GP", 0)).replace(",", "") or 0)
                    except ValueError:
                        current_gp = 0
    
                    if current_team == team_name:
                        caster_record = record
                        continue
    
                    if current_gp > 0:
                        valid_targets.append(current_team)
                        target_gp_data[current_team] = current_gp
    
                if not caster_record:
                    await interaction.followup.send("❌ Card effect failed: Could not locate your team's data.", ephemeral=True)
                    return
    
                if not valid_targets:
                    await interaction.followup.send("❌ Card effect failed: No other teams have any GP to steal.", ephemeral=True)
                    return
    
                embed = discord.Embed(
                    title="🎯 Target Selection: Pickpocket",
                    description="Select a team to pickpocket! Here is the current GP of all eligible targets:\n",
                    color=discord.Color.dark_gold()
                )
                for t in valid_targets:
                    embed.description += f"\n• **{t}**: {target_gp_data[t]:,} GP"
    
                # Pass the parsed team data so we don't have to read the sheet twice!
                extra_memory = {
                    "all_teams_data": all_teams_data,
                    "caster_record": caster_record
                }
                view = CardTargetView(self, team_name, valid_targets, "Pickpocket", "pickpocket", extra_data=extra_memory)
                await interaction.followup.send(embed=embed, view=view, ephemeral=False)
                return
    
                elif card_name == "Lure":
                    all_teams_data = self.team_data_sheet.get_all_records()
                    caster_pos = -1
                    opponents_ahead = []
    
                    for record in all_teams_data:
                        if record.get("Team") == team_name:
                            caster_pos = int(record.get("Position", -1))
                            break
                    
                    if caster_pos == -1:
                        await interaction.followup.send("❌ Could not find your team's position.", ephemeral=True)
                        return
    
                    for record in all_teams_data:
                        opponent_team_name = record.get("Team")
                        if opponent_team_name == team_name:
                            continue
                        
                        opponent_pos = int(record.get("Position", -1))
                        if opponent_pos > caster_pos:
                            opponents_ahead.append((opponent_team_name, opponent_pos))
                    
                    if not opponents_ahead:
                        await interaction.followup.send("❌ Card effect failed: No opponents are ahead of you.", ephemeral=True)
                        return 
    
                    sorted_opponents = sorted(opponents_ahead, key=lambda x: x[1])
                    target_team = sorted_opponents[0][0]
                    target_pos = sorted_opponents[0][1]
                    
                    victim_channel = self.get_team_channel(target_team)
    
                    if self.check_and_consume_redemption(target_team):
                        embed_description = f"<:fishing:1437980297017688114> **{team_name}** tried to use **Lure** on **{target_team}**...\n\n<:redemption:1437979567900987493> But **{target_team}**'s Redemption activated!"
                        if victim_channel:
                            fizzle_embed = discord.Embed(title="<:redemption:1437979567900987493> Redemption Activated!", description=f"**{team_name}** tried to use **Lure** on you, but your **Redemption** activated!", color=discord.Color.blue())
                            await victim_channel.send(embed=fizzle_embed)
    
                            await self.mirror_to_game_log(victim_channel, embed=fizzle_embed)
                    
                    else:
                        intended_lure_pos = caster_pos
                        final_lure_pos = self.resolve_nonroll_landing_tile(intended_lure_pos)
                        glider_note = self.get_glider_redirect_note(intended_lure_pos, final_lure_pos)
                        glider_note_victim = self.get_glider_redirect_note(intended_lure_pos, final_lure_pos, second_person=True, quoted=False)
                        self.log_command(
                            team_name,
                            "/card_effect_set_tile",
                            {"team": target_team, "tile": final_lure_pos}
                        )
                        source_tile_name = self.get_tile_name_for_display(target_pos)
                        destination_tile_name = self.get_tile_name_for_display(final_lure_pos)
                        embed_description = (
                            f"<:fishing:1437980297017688114> **{target_team}** was lured from the "
                            f"**{source_tile_name}** tile (Tile **{target_pos}**) to your tile: the "
                            f"**{destination_tile_name}** tile (Tile **{final_lure_pos}**)!"
                        )
                        embed_description += glider_note
                        
                        if victim_channel:
                        
                            lure_embed = discord.Embed(
                        
                                title="<:fishing:1437980297017688114> You Were Lured!",
                        
                                description=(f"**{team_name}** used **Lure** and pulled your team to the **{self.get_tile_name_for_display(final_lure_pos)}** tile (Tile **{final_lure_pos}**)." + glider_note_victim),
                        
                                color=discord.Color.orange()
                        
                            )
                        
                            await victim_channel.send(embed=lure_embed)
    
                        
                            await self.mirror_to_game_log(victim_channel, embed=lure_embed)
    
                        
                        await self.check_and_award_card_on_land(target_team, final_lure_pos, "being lured to")
                        await self.auto_post_show_drops_if_boss_tile(target_team, final_lure_pos)

            elif card_name == "Escape Crystal":
                # 1. Teleblock Check
                if self.get_teleblock_status(team_name) == "yes":
                    await interaction.followup.send("<:teleblock:1438088930816819271> You are Teleblocked! You cannot use this card, even in jail!", ephemeral=True)
                    return 

                # 2. Jail Status Check (The new guard clause)
                jail_status = await asyncio.to_thread(self.get_jail_status, team_name)
                if jail_status != "yes":
                    await interaction.followup.send(
                        "❌ **Action Denied:** You are currently 'Just Visiting' Tile 10. "
                        "The Escape Crystal can only be used if you were sent to Jail!",
                        ephemeral=True
                    )
                    return

                # 3. Execution
                self.increment_rolls_available(team_name)
                # Clear the jail status after a successful escape
                await asyncio.to_thread(self.set_jail_status, team_name, "no")
                
                embed_description = "> 🎲 You have used your crystal to escape! You gained a free roll."

            elif card_name == "Backstab":
                import random
                
                # Fetch a fast snapshot of the data
                all_teams_data = await asyncio.to_thread(self.team_data_sheet.get_all_records)
                caster_pos = -1
                opponents_ahead = []

                for record in all_teams_data:
                    if record.get("Team") == team_name:
                        caster_pos = int(record.get("Position", -1))
                        break
                
                if caster_pos == -1:
                    await interaction.followup.send("❌ Could not find your team's position.", ephemeral=True)
                    return 

                for record in all_teams_data:
                    opponent_team_name = record.get("Team")
                    if opponent_team_name == team_name:
                        continue
                    
                    opponent_pos = int(record.get("Position", -1))
                    dist = opponent_pos - caster_pos
                    
                    # CHANGE: Ensure they are strictly 1 to 5 tiles ahead
                    if 1 <= dist <= 5:
                        opponents_ahead.append((opponent_team_name, opponent_pos, dist))
                
                if not opponents_ahead:
                    await interaction.followup.send("❌ Card effect failed: No opponents are within 5 tiles ahead of you.", ephemeral=True)
                    return 

                # Sort by distance to find the closest
                sorted_opponents = sorted(opponents_ahead, key=lambda x: x[2])
                closest_dist = sorted_opponents[0][2]
                
                # Handle ties just in case two teams are equally close ahead
                closest_teams = [opp for opp in sorted_opponents if opp[2] == closest_dist]
                chosen_target = random.choice(closest_teams)
                
                target_team = chosen_target[0]
                target_pos = chosen_target[1] 
                
                # CHANGE: Roll a 1d3 to determine how far behind the caster they are thrown
                base_roll = random.randint(1, 3)
                
                embed_description = f"**{team_name}** lunges at **{target_team}** and rolled a **{base_roll}** on their d3!\n"
                victim_channel = self.get_team_channel(target_team)

                # 1. Check Redemption (Total Immunity)
                if await asyncio.to_thread(self.check_and_consume_redemption, target_team):
                    embed_description += f"> <:redemption:1437979567900987493> **{target_team}**'s Redemption activated. **Backstab** fizzled!\n"
                    if victim_channel:
                        fizzle_embed = discord.Embed(
                            title="<:redemption:1437979567900987493> Redemption Activated!", 
                            description=f"**{team_name}** tried to use **Backstab** on you, but your **Redemption** activated!", 
                            color=discord.Color.blue()
                        )
                        await victim_channel.send(embed=fizzle_embed)
                        await self.mirror_to_game_log(victim_channel, embed=fizzle_embed)
                
                # 2. Check Vengeance (Rebound)
                elif await asyncio.to_thread(self.check_and_consume_vengeance, target_team):
                    # Caster gets hit. Does the CASTER have an Elder Maul?
                    elder_maul_active = await asyncio.to_thread(self.check_and_consume_elder_maul, team_name) 
                    
                    # Halve the effect if Maul is active
                    final_roll_val = (base_roll // 2) if elder_maul_active else base_roll
                    maul_suffix = " (Halved by <:maul:1437979898865258668> **Elder Maul**!)" if elder_maul_active else ""
                    
                    intended_rebound_pos = max(0, caster_pos - final_roll_val)
                    new_pos = self.resolve_nonroll_landing_tile(intended_rebound_pos)
                    destination_tile_name = self.get_tile_name_for_display(new_pos)
                    glider_note = self.get_glider_redirect_note(intended_rebound_pos, new_pos)
                    glider_note_victim = self.get_glider_redirect_note(intended_rebound_pos, new_pos, second_person=True, quoted=False)
                    
                    await asyncio.to_thread(self.log_command, team_name, "/card_effect_set_tile", {"team": team_name, "tile": new_pos})
                    
                    embed_description += (
                        f"> <:venge:1438084953559797884> **{target_team}** had Vengeance! Your team was moved to the "
                        f"**{destination_tile_name}** tile (Tile **{new_pos}**){maul_suffix}.\n"
                    )
                    embed_description += glider_note
                    
                    await self.check_and_award_card_on_land(team_name, new_pos, "being rebounded by Backstab to")
                    await self.auto_post_show_drops_if_boss_tile(team_name, new_pos)
                    
                    skull_embed = discord.Embed(
                        title="<:venge:1438084953559797884> Vengeance Activated!", 
                        description=(f"You activated **{target_team}**'s Vengeance!\nYour team was moved to the **{destination_tile_name}** tile (Tile **{new_pos}**)!" + glider_note_victim), 
                        color=discord.Color.dark_red()
                    )
                    await interaction.channel.send(embed=skull_embed)
                    await self.mirror_to_game_log(interaction.channel, embed=skull_embed)
                    
                    if victim_channel:
                        victim_embed = discord.Embed(
                            title="<:venge:1438084953559797884> Vengeance Activated!",
                            description=(
                                f"**{team_name}** tried to use **Backstab** on your team, but your **Vengeance** rebounded the effect!\n"
                                f"They were moved to the **{destination_tile_name}** tile (Tile **{new_pos}**)."
                                + glider_note_victim
                            ),
                            color=discord.Color.dark_red()
                        )
                        await victim_channel.send(embed=victim_embed)
                        await self.mirror_to_game_log(victim_channel, embed=victim_embed)
                
                # 3. Normal Hit
                else:
                    # Target gets hit. Does the TARGET have an Elder Maul?
                    elder_maul_active = await asyncio.to_thread(self.check_and_consume_elder_maul, target_team)
                    
                    # Halve the effect if Maul is active
                    final_roll_val = (base_roll // 2) if elder_maul_active else base_roll 
                    maul_suffix = " (Halved by <:maul:1437979898865258668> **Elder Maul**!)" if elder_maul_active else ""
                    
                    # CHANGE: The destination is now the CASTER'S position minus the d3 roll
                    intended_backstab_pos = max(0, caster_pos - final_roll_val) 
                    new_pos = self.resolve_nonroll_landing_tile(intended_backstab_pos)
                    glider_note = self.get_glider_redirect_note(intended_backstab_pos, new_pos)
                    glider_note_victim = self.get_glider_redirect_note(intended_backstab_pos, new_pos, second_person=True, quoted=False)
                    source_tile_name = self.get_tile_name_for_display(target_pos)
                    destination_tile_name = self.get_tile_name_for_display(new_pos)
                    
                    await asyncio.to_thread(self.log_command, team_name, "/card_effect_set_tile", {"team": target_team, "tile": new_pos})
                    
                    embed_description += (
                        f"> **{target_team}** was dragged from the **{source_tile_name}** tile (Tile **{target_pos}**) "
                        f"and thrown **{final_roll_val}** tiles behind {team_name} to the **{destination_tile_name}** tile (Tile **{new_pos}**){maul_suffix}."
                    )
                    embed_description += glider_note

                    await self.check_and_award_card_on_land(target_team, new_pos, "being backstabbed to")
                    await self.auto_post_show_drops_if_boss_tile(target_team, new_pos)
                    
                    if victim_channel:
                        victim_embed = discord.Embed(
                            title="<:boner:1438085053102948383> You Were Backstabbed!",
                            description=(
                                f"**{team_name}** used **Backstab** on your team.\n"
                                f"You were dragged behind them to the **{destination_tile_name}** tile (Tile **{new_pos}**){maul_suffix}."
                                + glider_note_victim
                            ),
                            color=discord.Color.dark_red()
                        )
                        await victim_channel.send(embed=victim_embed)
                        await self.mirror_to_game_log(victim_channel, embed=victim_embed)
                        
            elif card_name == "Smite":
            # 1. Fetch data snapshot to get all teams
            all_teams_data = await asyncio.to_thread(self.team_data_sheet.get_all_records)
            
            valid_targets = []
            for record in all_teams_data:
                current_team_name = record.get("Team")
                # Add all teams except the caster to the target list
                if current_team_name and current_team_name != team_name:
                    valid_targets.append(current_team_name)

            if not valid_targets:
                await interaction.followup.send("❌ Card effect failed: There are no other teams to Smite.", ephemeral=True)
                return 

            # Prepare the Dropdown
            embed = discord.Embed(
                title="🎯 Target Selection: Smite",
                description="Select a team to Smite! You can choose ANY team on the board.",
                color=discord.Color.red()
            )

            # Pass the card's sheet/row data so we can delete it from their inventory later!
            extra_memory = {
                "card_sheet": card_sheet,
                "card_row": card_row,
                "wildcard_data": wildcard_data,
                "team_wildcard_value": team_wildcard_value
            }
            
            view = CardTargetView(self, team_name, valid_targets, "Smite", "smite", extra_data=extra_memory)
            await interaction.followup.send(embed=embed, view=view, ephemeral=False)
            return

            elif card_name == "Varrock Tele":
                # Check Teleblock
                if await asyncio.to_thread(self.get_teleblock_status, team_name) == "yes":
                    await interaction.followup.send("<:teleblock:1438088930816819271> You are Teleblocked! You cannot use this card.", ephemeral=True)
                    return 

                # Fetch snapshot
                all_teams_data = await asyncio.to_thread(self.team_data_sheet.get_all_records)
                caster_pos = -1
                for record in all_teams_data:
                    if record.get("Team") == team_name:
                        caster_pos = int(record.get("Position", -1))
                        break
                
                if caster_pos == 10:
                    await interaction.followup.send("❌ You cannot use **Varrock Tele** while on tile 10 (Nex/Gauntlet).", ephemeral=True)
                    return 

                new_pos = self.resolve_nonroll_landing_tile(BANK_STANDING_TILE)
                await asyncio.to_thread(self.log_command, team_name, "/card_effect_set_tile", {"team": team_name, "tile": new_pos})
                
                embed_description = "> Teleported to **Bank Standing** (Tile 20)."

                # Route through normal board triggers (Tile 20 grants a free roll automatically here)
                await self.check_and_award_card_on_land(team_name, new_pos, "teleporting to via Varrock Tele")
                await self.auto_post_show_drops_if_boss_tile(team_name, new_pos)

            elif card_name == "POH Voucher":
                # 1. Fetch snapshot of data
                all_teams_data = await asyncio.to_thread(self.team_data_sheet.get_all_records)
                house_data = await asyncio.to_thread(self.house_data_sheet.get_all_records)
                
                # 2. Get Caster Position
                team_info = next((r for r in all_teams_data if r.get("Team") == team_name), None)
                if not team_info:
                    await interaction.followup.send("❌ Could not find your team's position.", ephemeral=True)
                    return 

                caster_pos = int(team_info.get("Position", -1))

                # 3. Check Tile Data
                target_tile_data = next((h for h in house_data if int(h.get("Tile", -1)) == caster_pos), None)

                if not target_tile_data:
                    await interaction.followup.send("❌ This tile is not a valid tile for housing.", ephemeral=True)
                    return

                current_owner = str(target_tile_data.get("OwnerTeam", "")).strip()
                try:
                    current_house_count = int(target_tile_data.get("HouseCount", 0) or 0)
                except ValueError:
                    current_house_count = 0

                # 4a. VALIDATION: Check if someone else owns it
                if current_owner and current_owner != team_name:
                    await interaction.followup.send(
                        f"❌ **Action Denied:** Tile {caster_pos} is already owned by **{current_owner}**. "
                        "You cannot use a POH Voucher on another team's property!",
                        ephemeral=True
                    )
                    return

                # 4b. VALIDATION: Check if max houses (4) is reached
                if current_owner == team_name and current_house_count >= 4:
                    await interaction.followup.send(
                        f"❌ **Action Denied:** Tile {caster_pos} already has the maximum of 4 houses! "
                        "Save your POH Voucher for another property.",
                        ephemeral=True
                    )
                    return

                # 5. Success: ACTUALLY PLACE THE HOUSE!
                # We call your place_house function in a thread so it runs fast
                house_placed_successfully = await asyncio.to_thread(self.place_house, team_name, caster_pos, True)
                
                if house_placed_successfully:
                    # Still log it for your records
                    await asyncio.to_thread(self.log_command, team_name, "/card_effect_place_house_free", {"team": team_name, "tile": caster_pos})
                    embed_description = f"> <:houseicon:1438085020156821555> Placed a **free house** on tile **{caster_pos}**!"
                else:
                    await interaction.followup.send("❌ A database error occurred while trying to place the house. Your card was not consumed.", ephemeral=True)
                    return # Exit so the card isn't lost

            elif card_name == "Home Tele":
                if self.get_teleblock_status(team_name) == "yes":
                    await interaction.followup.send("<:teleblock:1438088930816819271> You are Teleblocked! You cannot use this card.", ephemeral=True)
                    return 

                all_teams_data = self.team_data_sheet.get_all_records()
                caster_pos = -1
                for record in all_teams_data:
                    if record.get("Team") == team_name:
                        caster_pos = int(record.get("Position", -1))
                        break

                if caster_pos == -1:
                    await interaction.followup.send("❌ Could not find your team's position.", ephemeral=True)
                    return  

                if caster_pos == 10:
                    await interaction.followup.send("❌ You cannot use **Home Tele** while on tile 10 (Nex/Gauntlet).", ephemeral=True)
                    return  

                try:
                    houses = self.get_houses()
                except Exception as e:
                    print(f"❌ Error fetching houses for Home Tele: {e}")
                    await interaction.followup.send("❌ An internal error occurred while finding houses.", ephemeral=True)
                    return

                closest_house_pos = -1
                min_distance = float('inf')

                for house in houses:
                    house_tile = house.get("tile", 0)
                    if house_tile > caster_pos:
                        distance = house_tile - caster_pos
                        if distance < min_distance:
                            min_distance = distance
                            closest_house_pos = house_tile

                if closest_house_pos == -1:
                    await interaction.followup.send("❌ Card effect failed: No house tiles are ahead of you on the board.", ephemeral=True)
                    return  

                new_pos = self.resolve_nonroll_landing_tile(closest_house_pos)
                destination_tile_name = self.get_tile_name_for_display(new_pos)
                embed_description = f"> Teleported to the **{destination_tile_name}** tile (Tile **{new_pos}**) — nearest house tile ahead."
                await loop.run_in_executor(None, self.log_command, team_name, "/card_effect_set_tile", {"team": team_name, "tile": new_pos})
                await self.check_and_award_card_on_land(team_name, new_pos, "teleporting to")
                await self.auto_post_show_drops_if_boss_tile(team_name, new_pos)

            elif card_name == "Tele Other":
                all_teams_data = self.team_data_sheet.get_all_records()
                caster_pos = -1
                opponents = []

                for record in all_teams_data:
                    current_team_name = record.get("Team")
                    if current_team_name == team_name:
                        caster_pos = int(record.get("Position", -1))
                    elif current_team_name:
                        opponents.append({
                            "team": current_team_name,
                            "pos": int(record.get("Position", -1))
                        })
                
                if caster_pos == 10:
                    await interaction.followup.send("❌ You cannot use **Tele Other** while on tile 10 (Nex/Gauntlet).", ephemeral=True)
                    return 

                if not opponents:
                    await interaction.followup.send("❌ Card effect failed: There are no other teams to swap with.", ephemeral=True)
                    return 

                target = random.choice(opponents)
                target_team = target["team"]
                target_pos = target["pos"]
                victim_channel = self.get_team_channel(target_team)
                embed_description = ""
                
                if self.check_and_consume_vengeance(target_team):
                    embed_description += f"> <:venge:1438084953559797884> **{target_team}** had Vengeance active! The teleport fizzled, and both cards were consumed."
                    if victim_channel:
                        victim_embed = discord.Embed(
                            title="<:venge:1438084953559797884> Vengeance Activated!",
                            description=f"**{team_name}** tried to use **Tele Other** on your team, but your **Vengeance** caused the teleport to fizzle.",
                            color=discord.Color.dark_red()
                        )
                        await victim_channel.send(embed=victim_embed)

                        await self.mirror_to_game_log(victim_channel, embed=victim_embed)
                
                elif self.check_and_consume_redemption(target_team):
                    embed_description += f"> <:redemption:1437979567900987493> **{target_team}**\'s Redemption activated! The teleport was cancelled."
                    if victim_channel:
                        fizzle_embed = discord.Embed(title="<:redemption:1437979567900987493> Redemption Activated!", description=f"**{team_name}** tried to use **Tele Other** on you, but your **Redemption** activated!", color=discord.Color.blue())
                        await victim_channel.send(embed=fizzle_embed)

                        await self.mirror_to_game_log(victim_channel, embed=fizzle_embed)

                else:
                    caster_intended_pos = target_pos
                    target_intended_pos = caster_pos
                    caster_final_pos = self.resolve_nonroll_landing_tile(caster_intended_pos)
                    target_final_pos = self.resolve_nonroll_landing_tile(target_intended_pos)
                    caster_glider_note = self.get_glider_redirect_note(caster_intended_pos, caster_final_pos)
                    target_glider_note = self.get_glider_redirect_note(target_intended_pos, target_final_pos)
                    target_glider_note_victim = self.get_glider_redirect_note(target_intended_pos, target_final_pos, second_person=True, quoted=False)
                    caster_dest_name = self.get_tile_name_for_display(caster_final_pos)
                    target_dest_name = self.get_tile_name_for_display(target_final_pos)
                    embed_description += (
                        f"> Swapped places with **{target_team}**. "
                        f"You moved to the **{caster_dest_name}** tile (Tile **{caster_final_pos}**), "
                        f"and they moved to the **{target_dest_name}** tile (Tile **{target_final_pos}**)."
                    )
                    embed_description += caster_glider_note
                    if target_glider_note:
                        embed_description += target_glider_note.replace(" was launched", f" {target_team} was launched")
                    
                    await loop.run_in_executor(None, self.log_command, team_name, "/card_effect_set_tile", {"team": team_name, "tile": caster_final_pos})
                    await loop.run_in_executor(None, self.log_command, team_name, "/card_effect_set_tile", {"team": target_team, "tile": target_final_pos})

                    if victim_channel:
                        swap_embed = discord.Embed(title="<:teleother:1437980130407350375> You've Been Swapped!", description=(f"**{team_name}** used **Tele Other** and swapped places with your team!\nYour team is now on the **{target_dest_name}** tile (Tile **{target_final_pos}**)." + target_glider_note_victim), color=discord.Color.orange())
                        await victim_channel.send(embed=swap_embed)

                        await self.mirror_to_game_log(victim_channel, embed=swap_embed)

                    await self.check_and_award_card_on_land(team_name, caster_final_pos, "being teleported to")
                    await self.check_and_award_card_on_land(target_team, target_final_pos, "being teleported to")
                    await self.auto_post_show_drops_if_boss_tile(team_name, caster_final_pos)
                    await self.auto_post_show_drops_if_boss_tile(target_team, target_final_pos)

            elif card_name == "Tele Block":
            # 1. Fetch data snapshot to get all teams
            all_teams_data = await asyncio.to_thread(self.team_data_sheet.get_all_records)
            
            valid_targets = []
            for record in all_teams_data:
                current_team_name = record.get("Team")
                # Add all teams except the caster to the target list
                if current_team_name and current_team_name != team_name:
                    valid_targets.append(current_team_name)

            if not valid_targets:
                await interaction.followup.send("❌ Card effect failed: There are no other teams to Teleblock.", ephemeral=True)
                return 

            # Prepare the Dropdown
            embed = discord.Embed(
                title="🎯 Target Selection: Tele Block",
                description="Select a team to Teleblock! You can choose ANY team on the board.",
                color=discord.Color.dark_purple()
            )

            # Pass the card's sheet/row data so we can delete it from their inventory later!
            extra_memory = {
                "card_sheet": card_sheet,
                "card_row": card_row,
                "wildcard_data": wildcard_data,
                "team_wildcard_value": team_wildcard_value
            }
            
            view = CardTargetView(self, team_name, valid_targets, "Tele Block", "teleblock", extra_data=extra_memory)
            await interaction.followup.send(embed=embed, view=view, ephemeral=False)
            return

    async def execute_targeted_card_effect(self, interaction: discord.Interaction, team_name: str, target_team: str, card_name: str, action: str, extra_data: dict):
        """Catches the dropdown selection and applies the effects of the card."""
        
        if action == "pickpocket":
            all_teams_data = extra_data.get("all_teams_data")
            caster_record = extra_data.get("caster_record")
            
            # Find the specific target record based on the dropdown selection
            target_record = None
            highest_gp = 0 
            for record in all_teams_data:
                if record.get("Team") == target_team:
                    target_record = record
                    try:
                        highest_gp = int(str(record.get("GP", 0)).replace(",", "") or 0)
                    except ValueError:
                        highest_gp = 0
                    break
                    
            if not target_record:
                await interaction.channel.send("❌ Error: Target data could not be located.")
                return

            victim_channel = self.get_team_channel(target_team)
            caster_gp = int(str(caster_record.get("GP", 0)).replace(",", ""))
            
            embed_description = f"**{team_name}** targeted **{target_team}** with **Pickpocket**!\n"
            headers = list(all_teams_data[0].keys())
            gp_col_idx = headers.index("GP") + 1
            target_row_idx = all_teams_data.index(target_record) + 2
            caster_row_idx = all_teams_data.index(caster_record) + 2

            # 2. Check Redemption (Total Fizzle)
            if await asyncio.to_thread(self.check_and_consume_redemption, target_team):
                embed_description += f"> <:redemption:1437979567900987493> **{target_team}**'s Redemption activated! The Pickpocket fizzled."
                if victim_channel:
                    fizzle_embed = discord.Embed(title="<:redemption:1437979567900987493> Redemption Activated!", description=f"**{team_name}** tried to use **Pickpocket** on you, but your **Redemption** activated!", color=discord.Color.blue())
                    await victim_channel.send(embed=fizzle_embed)
                    await self.mirror_to_game_log(victim_channel, embed=fizzle_embed)

            # 3. Check Vengeance (Rebound to Caster)
            elif await asyncio.to_thread(self.check_and_consume_vengeance, target_team):
                base_percent = 0.20
                maul_active = await asyncio.to_thread(self.check_and_consume_elder_maul, team_name)
                maul_note = ""
                if maul_active:
                    base_percent = 0.10
                    maul_note = " (Halved by <:maul:1437979898865258668> **Elder Maul**!)"

                steal_amount = max(1, int(caster_gp * base_percent))
                new_caster_gp = max(0, caster_gp - steal_amount)
                new_target_gp = highest_gp + steal_amount

                await asyncio.to_thread(self.team_data_sheet.update_cell, caster_row_idx, gp_col_idx, new_caster_gp)
                await asyncio.to_thread(self.team_data_sheet.update_cell, target_row_idx, gp_col_idx, new_target_gp)

                embed_description += f"> <:venge:1438084953559797884> **{target_team}** had Vengeance! They stole **{steal_amount:,} GP** from **{team_name}** instead!{maul_note}"

                if victim_channel:
                    victim_embed = discord.Embed(title="<:venge:1438084953559797884> Vengeance Activated!", description=f"**{team_name}** tried to use **Pickpocket** on you, but your **Vengeance** rebounded it! You stole **{steal_amount:,} GP** from them!{maul_note}", color=discord.Color.green())
                    await victim_channel.send(embed=victim_embed)
                    await self.mirror_to_game_log(victim_channel, embed=victim_embed)

            # 4. Normal Hit (Caster steals from Target)
            else:
                base_percent = 0.20
                maul_active = await asyncio.to_thread(self.check_and_consume_elder_maul, target_team)
                maul_note = ""
                if maul_active:
                    base_percent = 0.10
                    maul_note = " (Halved by <:maul:1437979898865258668> **Elder Maul**!)"

                steal_amount = max(1, int(highest_gp * base_percent))
                new_target_gp = max(0, highest_gp - steal_amount)
                new_caster_gp = caster_gp + steal_amount

                await asyncio.to_thread(self.team_data_sheet.update_cell, target_row_idx, gp_col_idx, new_target_gp)
                await asyncio.to_thread(self.team_data_sheet.update_cell, caster_row_idx, gp_col_idx, new_caster_gp)

                embed_description += f"> Stole **{steal_amount:,} GP** from **{target_team}**!{maul_note}"

                if victim_channel:
                    maul_msg = "\n\n🛡️ Your **Elder Maul** activated and halved the losses!" if maul_active else ""
                    victim_embed = discord.Embed(
                        title="💸 Pickpocketed!",
                        description=f"**{team_name}** used **Pickpocket** and stole **{steal_amount:,} GP** from your team.{maul_msg}",
                        color=discord.Color.dark_red() if not maul_active else discord.Color.blue()
                    )
                    await victim_channel.send(embed=victim_embed)
                    await self.mirror_to_game_log(victim_channel, embed=victim_embed)
                    
            # Send the final receipt to the channel where the card was used
            final_embed = discord.Embed(title="🃏 Pickpocket Used!", description=embed_description, color=discord.Color.dark_gold())
            await interaction.channel.send(embed=final_embed)

        elif action == "rogues_gloves":
            # Retrieve memory passed from the dropdown
            stealable_cards = extra_data.get("stealable_cards", [])
            card_sheet = extra_data.get("rg_sheet")
            card_row = extra_data.get("rg_row")

            # Filter the stealable cards down to ONLY the team the Captain clicked
            target_cards = [c for c in stealable_cards if c["victim_team"] == target_team]
            if not target_cards:
                await interaction.channel.send("❌ Error: No cards found for that target.")
                return
            
            stolen_card = random.choice(target_cards)
            victim_team = target_team
            target_sheet = stolen_card["sheet"]
            target_row = stolen_card["row_index"]
            
            victim_channel = self.get_team_channel(victim_team)

            if self.check_and_consume_redemption(victim_team):
                embed_description = f"<:rogue_gloves:1437980096790134914> **{team_name}** tried to use **Rogue's Gloves** on **{victim_team}**...\n\n<:redemption:1437979567900987493> But **{victim_team}**'s Redemption activated!"
                if victim_channel:
                    fizzle_embed = discord.Embed(
                        title="<:redemption:1437979567900987493> Redemption Activated!",
                        description=f"**{team_name}** tried to use **Rogue's Gloves** on you, but your **Redemption** activated!",
                        color=discord.Color.blue()
                    )
                    await victim_channel.send(embed=fizzle_embed)
                    await self.mirror_to_game_log(victim_channel, embed=fizzle_embed)

            elif self.check_and_consume_vengeance(victim_team):
                embed_description = (
                    f"<:rogue_gloves:1437980096790134914> **{team_name}** tried to use **Rogue's Gloves** on **{victim_team}**...\n\n"
                    f"<:venge:1438084953559797884> **{victim_team}** had Vengeance! The effect was rebounded!\n"
                )

                caster_chest_cards = self.get_held_cards(self.chest_sheet, team_name)
                caster_chance_cards = self.get_held_cards(self.chance_sheet, team_name)

                caster_cards_with_sheet = []
                for c in caster_chest_cards:
                    caster_cards_with_sheet.append({
                        "sheet": self.chest_sheet,
                        "row_index": c["row_index"],
                        "card_name": c["name"],
                        "card_type": "Chest"
                    })
                for c in caster_chance_cards:
                    caster_cards_with_sheet.append({
                        "sheet": self.chance_sheet,
                        "row_index": c["row_index"],
                        "card_name": c["name"],
                        "card_type": "Chance"
                    })

                other_caster_cards = [
                    c for c in caster_cards_with_sheet
                    if not (c["sheet"] == card_sheet and c["row_index"] == card_row)
                ]

                stolen_from_caster_name = None

                if other_caster_cards:
                    rebounded_card = random.choice(other_caster_cards)
                    rebound_sheet = rebounded_card["sheet"]
                    rebound_row = rebounded_card["row_index"]
                    stolen_from_caster_name = rebounded_card["card_name"]

                    held_by_str_rebound = str(rebound_sheet.cell(rebound_row, 3).value or "")
                    teams_rebound = [t.strip() for t in held_by_str_rebound.split(',') if t.strip()]
                    if team_name in teams_rebound:
                        teams_rebound.remove(team_name)
                    if victim_team not in teams_rebound:
                        teams_rebound.append(victim_team)
                    rebound_sheet.update_cell(rebound_row, 3, ", ".join(teams_rebound))

                    wildcard_str_rebound = str(rebound_sheet.cell(rebound_row, 4).value or "{}")
                    try:
                        import json
                        wildcard_data_json_rebound = json.loads(wildcard_str_rebound)
                        caster_wildcard = wildcard_data_json_rebound.pop(team_name, None)
                        if caster_wildcard is not None:
                            wildcard_data_json_rebound[victim_team] = caster_wildcard
                        rebound_sheet.update_cell(rebound_row, 4, json.dumps(wildcard_data_json_rebound))
                    except Exception as e:
                        print(f"❌ Error transferring wildcard data on Rogue's Gloves Vengeance rebound: {e}")

                    embed_description += f"🧤 The steal rebounded! **{victim_team}** stole **{stolen_from_caster_name}** from **{team_name}** instead."

                else:
                    stolen_from_caster_name = "Rogue's Gloves"

                    held_by_str_rg = str(card_sheet.cell(card_row, 3).value or "")
                    teams_rg = [t.strip() for t in held_by_str_rg.split(',') if t.strip()]
                    if team_name in teams_rg:
                        teams_rg.remove(team_name)
                    if victim_team not in teams_rg:
                        teams_rg.append(victim_team)
                    card_sheet.update_cell(card_row, 3, ", ".join(teams_rg))

                    wildcard_str_rg = str(card_sheet.cell(card_row, 4).value or "{}")
                    try:
                        import json
                        wildcard_data_json_rg = json.loads(wildcard_str_rg)
                        caster_wildcard = wildcard_data_json_rg.pop(team_name, None)
                        if caster_wildcard is not None:
                            wildcard_data_json_rg[victim_team] = caster_wildcard
                        card_sheet.update_cell(card_row, 4, json.dumps(wildcard_data_json_rg))
                    except Exception as e:
                        print(f"❌ Error transferring wildcard data for Rogue's Gloves on Vengeance rebound: {e}")

                    embed_description += f"🧤 The steal rebounded! **{victim_team}** stole the **Rogue's Gloves** card from **{team_name}**!"

                skull_embed = discord.Embed(
                    title="<:venge:1438084953559797884> Vengeance Activated!",
                    description=f"You activated **{victim_team}**'s Vengeance!\nThey stole your **{stolen_from_caster_name}** card!",
                    color=discord.Color.dark_red()
                )
                await interaction.channel.send(embed=skull_embed)
                await self.mirror_to_game_log(interaction.channel, embed=skull_embed)

                if victim_channel:
                    victim_embed = discord.Embed(
                        title="<:venge:1438084953559797884> Vengeance Activated!",
                        description=f"**{team_name}** tried to use **Rogue's Gloves** on you, but your **Vengeance** rebounded the effect!\nYou stole **{stolen_from_caster_name}** from their team.",
                        color=discord.Color.dark_red()
                    )
                    await victim_channel.send(embed=victim_embed)
                    await self.mirror_to_game_log(victim_channel, embed=victim_embed)
            
            else:
                held_by_str = str(target_sheet.cell(target_row, 3).value or "")
                teams = [t.strip() for t in held_by_str.split(',') if t.strip()]
                if victim_team in teams:
                    teams.remove(victim_team)
                if team_name not in teams:
                    teams.append(team_name)
                target_sheet.update_cell(target_row, 3, ", ".join(teams))

                wildcard_str = str(target_sheet.cell(target_row, 4).value or "{}")
                try:
                    import json
                    wildcard_data_json = json.loads(wildcard_str)
                    victim_wildcard = wildcard_data_json.pop(victim_team, None)
                    if victim_wildcard is not None:
                        wildcard_data_json[team_name] = victim_wildcard
                        target_sheet.update_cell(target_row, 4, json.dumps(wildcard_data_json))
                except Exception as e:
                    print(f"❌ Error transferring wildcard data: {e}")

                embed_description = f"<:rogue_gloves:1437980096790134914> **{team_name}** used **Rogue's Gloves** and stole **{stolen_card['card_name']}** from **{victim_team}**!"
                
                if victim_channel:
                    victim_embed = discord.Embed(
                        title="‼️ Card Stolen!",
                        description=f"**{team_name}** used **Rogue's Gloves** and stole your **{stolen_card['card_name']}** card!",
                        color=discord.Color.dark_red()
                    )
                    await victim_channel.send(embed=victim_embed)
                    await self.mirror_to_game_log(victim_channel, embed=victim_embed)

            # Send the final result embed to the channel
            final_embed = discord.Embed(title="🃏 Rogue's Gloves Used!", description=embed_description, color=discord.Color.dark_gray())
            await interaction.channel.send(embed=final_embed)
        
        elif action == "teleblock":
            victim_channel = self.get_team_channel(target_team)
            embed_description = ""

            # 1. Check Redemption (Total Fizzle)
            if await asyncio.to_thread(self.check_and_consume_redemption, target_team):
                embed_description += f"> <:redemption:1437979567900987493> **{target_team}**'s Redemption activated! The effect fizzled."
                if victim_channel:
                    fizzle_embed = discord.Embed(title="<:redemption:1437979567900987493> Redemption Activated!", description=f"**{team_name}** tried to use **Tele Block** on you, but your **Redemption** activated!", color=discord.Color.blue())
                    await victim_channel.send(embed=fizzle_embed)
                    await self.mirror_to_game_log(victim_channel, embed=fizzle_embed)

            # 2. Check Vengeance (Rebound to Caster)
            elif await asyncio.to_thread(self.check_and_consume_vengeance, target_team):
                embed_description += f"> <:venge:1438084953559797884> **{target_team}** had Vengeance! The effect rebounded, and your team is now **Teleblocked**."
                self.set_teleblock_status(team_name, "yes") 
                
                skull_embed = discord.Embed(title="<:venge:1438084953559797884> Vengeance Activated!", description=f"You activated **{target_team}**'s Vengeance!\nYour team is now **Teleblocked**!", color=discord.Color.dark_red())
                await interaction.channel.send(embed=skull_embed)
                await self.mirror_to_game_log(interaction.channel, embed=skull_embed) 
                
                if victim_channel:
                    victim_embed = discord.Embed(
                        title="<:venge:1438084953559797884> Vengeance Activated!",
                        description=f"**{team_name}** tried to use **Tele Block** on your team, but your **Vengeance** rebounded the effect and **Teleblocked** them instead!",
                        color=discord.Color.dark_red()
                    )
                    await victim_channel.send(embed=victim_embed)
                    await self.mirror_to_game_log(victim_channel, embed=victim_embed)

            # 3. Normal Hit (Target is Teleblocked)
            else:
                embed_description += f"> <:teleblock:1438088930816819271> **{target_team}** is now **Teleblocked** until after their next roll."
                self.set_teleblock_status(target_team, "yes") 

                if victim_channel:
                    tb_embed = discord.Embed(title="<:teleblock:1438088930816819271> You are Teleblocked!", description=f"**{team_name}** used **Tele Block** on your team! You cannot use teleport cards until after your next roll.", color=discord.Color.dark_purple())
                    await victim_channel.send(embed=tb_embed)
                    await self.mirror_to_game_log(victim_channel, embed=tb_embed)

            # --- DEDUCT THE CARD FROM INVENTORY ---
            card_sheet = extra_data.get("card_sheet")
            card_row = extra_data.get("card_row")
            wildcard_data = extra_data.get("wildcard_data", {})
            team_wildcard_value = extra_data.get("team_wildcard_value")

            try:
                import json
                if team_wildcard_value is not None:
                    wildcard_data.pop(team_name, None) 
                    await asyncio.to_thread(card_sheet.update_cell, card_row, 4, json.dumps(wildcard_data))
                    print(f"✅ Cleared wildcard for {team_name} from Tele Block")
                
                cell_val = str(await asyncio.to_thread(lambda: card_sheet.cell(card_row, 3).value) or "")
                teams = [t.strip() for t in cell_val.split(',') if t.strip()]
                if team_name in teams:
                    teams.remove(team_name)
                await asyncio.to_thread(card_sheet.update_cell, card_row, 3, ", ".join(teams))
            except Exception as e:
                print(f"❌ Error updating inventory for Tele Block: {e}")

            self.set_used_card_flag(team_name, "yes")

            # --- SEND FINAL RECEIPT ---
            final_embed = discord.Embed(
                title=f"🃏 {team_name} used Tele Block!",
                description=embed_description,
                color=discord.Color.blue()
            )
            await interaction.channel.send(embed=final_embed)
            await self.mirror_to_game_log(interaction.channel, embed=final_embed)

        elif action == "smite":
            victim_team = target_team
            embed_description = ""
            victim_channel = self.get_team_channel(victim_team)

            # --- YOUR EXACT EXECUTION LOGIC ---
            victim_chest_cards = self.get_held_cards(self.chest_sheet, victim_team)
            victim_chance_cards = self.get_held_cards(self.chance_sheet, victim_team)
            all_victim_cards = victim_chest_cards + victim_chance_cards
            
            if not all_victim_cards:
                await interaction.channel.send(f"❌ Card effect failed: **{victim_team}** has no cards. Your **Smite** card was not used.")
                return

            non_active_cards = [card for card in all_victim_cards if "(ACTIVE)" not in card['text']]
            
            if not non_active_cards:
                await interaction.channel.send(f"❌ Card effect failed: **{victim_team}**'s cards are all active and cannot be removed. Your **Smite** card was not used.")
                return 

            if await asyncio.to_thread(self.check_and_consume_redemption, victim_team):
                embed_description += f"> <:redemption:1437979567900987493> **{victim_team}**'s Redemption activated!"
                if victim_channel:
                    fizzle_embed = discord.Embed(title="<:redemption:1437979567900987493> Redemption Activated!", description=f"**{team_name}** tried to use **Smite** on you, but your **Redemption** activated!", color=discord.Color.blue())
                    await victim_channel.send(embed=fizzle_embed)
                    await self.mirror_to_game_log(victim_channel, embed=fizzle_embed)
            
            elif await asyncio.to_thread(self.check_and_consume_vengeance, victim_team):
                embed_description += f"> <:venge:1438084953559797884> **{victim_team}** had Vengeance! The effect rebounded.\n> "
                
                caster_chest_cards = self.get_held_cards(self.chest_sheet, team_name)
                caster_chance_cards = self.get_held_cards(self.chance_sheet, team_name)
                all_caster_cards = caster_chest_cards + caster_chance_cards
                non_active_caster_cards = [card for card in all_caster_cards if "(ACTIVE)" not in card['text']]
                
                if not non_active_caster_cards:
                    embed_description += f"**{team_name}** had no cards to lose."
                    if victim_channel:
                        victim_embed = discord.Embed(
                            title="<:venge:1438084953559797884> Vengeance Activated!",
                            description=(
                                f"**{team_name}** tried to use **Smite** on your team, but your **Vengeance** rebounded the effect!\n"
                                f"They had no removable cards to lose."
                            ),
                            color=discord.Color.dark_red()
                        )
                        await victim_channel.send(embed=victim_embed)
                        await self.mirror_to_game_log(victim_channel, embed=victim_embed)
                else:
                    import random
                    card_to_remove = random.choice(non_active_caster_cards)
                    remove_sheet = self.chest_sheet if card_to_remove in caster_chest_cards else self.chance_sheet
                    remove_row = card_to_remove['row_index']
                    
                    wildcard_str = str(await asyncio.to_thread(lambda: remove_sheet.cell(remove_row, 4).value) or "{}")
                    try:
                        import json
                        wildcard_data = json.loads(wildcard_str)
                        wildcard_data.pop(team_name, None)
                        await asyncio.to_thread(remove_sheet.update_cell, remove_row, 4, json.dumps(wildcard_data))
                    except Exception as e:
                        print(f"❌ Error clearing wildcard on Vengeance Smite: {e}")
                        
                    held_by_str = str(await asyncio.to_thread(lambda: remove_sheet.cell(remove_row, 3).value) or "")
                    teams = [t.strip() for t in held_by_str.split(',') if t.strip()]
                    if team_name in teams:
                        teams.remove(team_name)
                    await asyncio.to_thread(remove_sheet.update_cell, remove_row, 3, ", ".join(teams))
                    
                    embed_description += f"**{team_name}** lost their **{card_to_remove['name']}** card."
                    
                    skull_embed = discord.Embed(title="<:venge:1438084953559797884> Vengeance Activated!", description=f"You activated **{victim_team}**'s Vengeance!\nYou lost your **{card_to_remove['name']}** card!", color=discord.Color.dark_red())
                    await interaction.channel.send(embed=skull_embed)
                    await self.mirror_to_game_log(interaction.channel, embed=skull_embed)
                    
                    if victim_channel:
                        victim_embed = discord.Embed(
                            title="<:venge:1438084953559797884> Vengeance Activated!",
                            description=(
                                f"**{team_name}** tried to use **Smite** on your team, but your **Vengeance** rebounded the effect!\n"
                                f"They lost their **{card_to_remove['name']}** card."
                            ),
                            color=discord.Color.dark_red()
                        )
                        await victim_channel.send(embed=victim_embed)
                        await self.mirror_to_game_log(victim_channel, embed=victim_embed)

            else:
                import random
                card_to_remove = random.choice(non_active_cards)
                remove_sheet = self.chest_sheet if card_to_remove in victim_chest_cards else self.chance_sheet
                remove_row = card_to_remove['row_index']

                wildcard_str = str(await asyncio.to_thread(lambda: remove_sheet.cell(remove_row, 4).value) or "{}")
                try:
                    import json
                    wildcard_data = json.loads(wildcard_str)
                    wildcard_data.pop(victim_team, None)
                    await asyncio.to_thread(remove_sheet.update_cell, remove_row, 4, json.dumps(wildcard_data))
                except Exception as e:
                    print(f"❌ Error clearing wildcard on Smite: {e}")
                    
                held_by_str = str(await asyncio.to_thread(lambda: remove_sheet.cell(remove_row, 3).value) or "")
                teams = [t.strip() for t in held_by_str.split(',') if t.strip()]
                if victim_team in teams:
                    teams.remove(victim_team)
                await asyncio.to_thread(remove_sheet.update_cell, remove_row, 3, ", ".join(teams))

                embed_description += f"> **{victim_team}** lost their **{card_to_remove['name']}** card."
                
                if victim_channel:
                    victim_embed = discord.Embed(title="‼️ Card Lost!", description=f"**{team_name}** used **Smite**! Your team lost your **{card_to_remove['name']}** card!", color=discord.Color.dark_red())
                    await victim_channel.send(embed=victim_embed)
                    await self.mirror_to_game_log(victim_channel, embed=victim_embed)

            # --- DEDUCT THE CARD FROM INVENTORY ---
            card_sheet = extra_data.get("card_sheet")
            card_row = extra_data.get("card_row")
            wildcard_data = extra_data.get("wildcard_data", {})
            team_wildcard_value = extra_data.get("team_wildcard_value")

            try:
                import json
                if team_wildcard_value is not None:
                    wildcard_data.pop(team_name, None) 
                    await asyncio.to_thread(card_sheet.update_cell, card_row, 4, json.dumps(wildcard_data))
                    
                cell_val = str(await asyncio.to_thread(lambda: card_sheet.cell(card_row, 3).value) or "")
                teams = [t.strip() for t in cell_val.split(',') if t.strip()]
                if team_name in teams:
                    teams.remove(team_name)
                await asyncio.to_thread(card_sheet.update_cell, card_row, 3, ", ".join(teams))
            except Exception as e:
                print(f"❌ Error updating inventory for Smite: {e}")

            self.set_used_card_flag(team_name, "yes")

            # --- SEND FINAL RECEIPT ---
            final_embed = discord.Embed(
                title=f"🃏 {team_name} used Smite!",
                description=embed_description,
                color=discord.Color.blue()
            )
            await interaction.channel.send(embed=final_embed)
            await self.mirror_to_game_log(interaction.channel, embed=final_embed)

    
    @app_commands.command(name="random_event", description="[TESTING] Simulate a tile-landing random event.")
    @app_commands.describe(
        team_name="The team to test the event on",
        force_trigger="If True, bypasses the 5% chance and forces an event to spawn"
    )
    async def random_event(self, interaction: discord.Interaction, team_name: str, force_trigger: bool = False):
        if not self.has_event_captain_role(interaction.user):
            await interaction.response.send_message("❌ Only the Event Captain can use this command.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=False)

        try:
            # 1. Fetch team data snapshot
            records = await asyncio.to_thread(self.team_data_sheet.get_all_records)
            
            team_info = next((r for r in records if str(r.get("Team", "")).strip().lower() == team_name.strip().lower()), None)
            if not team_info:
                await interaction.followup.send(f"❌ Could not find team **{team_name}**.", ephemeral=True)
                return

            chosen_team = str(team_info.get("Team")).strip()
            team_row_idx = records.index(team_info) + 2
            
            # Find max multiplier on the board for the Buff math
            team_multipliers = []
            for row in records:
                try:
                    mult = float(row.get("Event Multiplier", 1))
                except ValueError:
                    mult = 1.0
                team_multipliers.append(mult)
                
            max_mult = max(team_multipliers) if team_multipliers else 1.0
            
            # Get Victim's Multiplier
            try:
                victim_mult = float(team_info.get("Event Multiplier", 1))
            except ValueError:
                victim_mult = 1.0

            # 2. Roll for Spawn Chance (Multiplier * 5%)
            spawn_chance = int(victim_mult * 5)
            rng_roll = random.randint(1, 100)
            
            if not force_trigger and rng_roll > spawn_chance:
                await interaction.followup.send(f"🎲 **{chosen_team}** landed safely. (Rolled {rng_roll} vs {spawn_chance}% chance). No event spawned.")
                return

            # 3. Determine Nerf vs Buff
            nerf_weight = victim_mult
            buff_weight = (max_mult - victim_mult) + 1.0
            
            event_type = random.choices(["nerf", "buff"], weights=[nerf_weight, buff_weight], k=1)[0]
            
            headers = list(records[0].keys())
            gp_col = headers.index("GP") + 1 if "GP" in headers else -1
            current_gp = int(str(team_info.get("GP", 0)).replace(',', ''))
            current_pos = int(team_info.get("Position", 0))

            embed_desc = ""
            event_title = ""
            embed_color = discord.Color.red() if event_type == "nerf" else discord.Color.green()

            # ==========================================
            # 🔴 NERF MECHANICS
            # ==========================================
            if event_type == "nerf":
                event_title = "⚠️ A Disastrous Random Event Appears!"
                nerf_pool = [
                    "dwarf", "whirlpool", "ents", "forester", "bob", "twin", 
                    "pete", "gravedigger", "sandwich", "jekyll", "demon", 
                    "plant", "beekeeper", "mime", "maze"
                ]
                chosen_nerf = random.choice(nerf_pool)

                if chosen_nerf == "dwarf":
                    fine = int(current_gp * 0.20)
                    await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, gp_col, current_gp - fine)
                    embed_desc = f"🍺 **The Drunken Dwarf!**\n*\"Have a kebab, mate!\"* The dwarf corners **{chosen_team}** and forces them to pay his massive bar tab! They lose **20%** of their total wealth (**{fine:,} GP**)!"

                elif chosen_nerf == "ents":
                    col = headers.index("GP Halved") + 1 if "GP Halved" in headers else -1
                    if col != -1: await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, col, "yes")
                    embed_desc = f"🌳 **The Ents!**\nAn ent grew and shakes **{chosen_team}** upside down! Their gear is damaged. **All GP earned is cut in half** until their next roll!"

                elif chosen_nerf == "forester":
                    all_chance = await asyncio.to_thread(self.chance_sheet.get_all_records)
                    all_chest = await asyncio.to_thread(self.chest_sheet.get_all_records)
                    owned_cards = []
                    
                    for idx, r in enumerate(all_chance, start=2):
                        if chosen_team in [t.strip() for t in str(r.get("Held By Team", "")).split(",")]:
                            owned_cards.append({"sheet": self.chance_sheet, "row": idx, "data": r})
                    for idx, r in enumerate(all_chest, start=2):
                        if chosen_team in [t.strip() for t in str(r.get("Held By Team", "")).split(",")]:
                            owned_cards.append({"sheet": self.chest_sheet, "row": idx, "data": r})
                            
                    if owned_cards:
                        card_to_lose = random.choice(owned_cards)
                        teams_holding = [t.strip() for t in str(card_to_lose["data"].get("Held By Team", "")).split(",") if t.strip() != chosen_team]
                        await asyncio.to_thread(card_to_lose["sheet"].update_cell, card_to_lose["row"], 3, ", ".join(teams_holding))
                        card_name = card_to_lose["data"].get("Name", "a card")
                        embed_desc = f"🪶 **The Freaky Forester!**\n*\"You killed the wrong pheasant!\"* The Forester banishes **{chosen_team}** and strips them of their **{card_name}** card!"
                    else:
                        fine = int(current_gp * 0.15)
                        await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, gp_col, current_gp - fine)
                        embed_desc = f"🪶 **The Freaky Forester!**\n*\"You killed the wrong pheasant!\"* **{chosen_team}** had no cards to give, so they were fined **15%** of their wealth (**{fine:,} GP**)!"

                elif chosen_nerf == "whirlpool":
                    spaces_back = random.randint(1, 6)
                    new_pos = self.resolve_nonroll_landing_tile(max(0, current_pos - spaces_back))
                    await asyncio.to_thread(self.log_command, chosen_team, "/card_effect_set_tile", {"team": chosen_team, "tile": new_pos})
                    embed_desc = f"🌀 **The Whirlpool!**\nA sudden whirlpool sucks **{chosen_team}** under! They wash up **{spaces_back}** spaces backwards on Tile **{new_pos}**!"

                elif chosen_nerf == "sandwich":
                    spaces_back = random.randint(1, 6)
                    new_pos = max(0, current_pos - spaces_back)
                    await asyncio.to_thread(self.log_command, chosen_team, "/card_effect_set_tile", {"team": chosen_team, "tile": new_pos})
                    embed_desc = f"🥖 **The Sandwich Lady!**\n*\"You picked the wrong sandwich!\"* She whacks **{chosen_team}** with a stale baguette! They are knocked **{spaces_back}** tiles backwards to Tile **{new_pos}** and receive **no tile rewards**!"

                elif chosen_nerf == "demon":
                    col = headers.index("Roll Halved") + 1 if "Roll Halved" in headers else -1
                    if col != -1: await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, col, "yes")
                    embed_desc = f"📣 **The Demon Drill Sergeant!**\n*\"Drop and give me 50!\"* The Demon exhausts **{chosen_team}**. Their next dice roll is strictly **cut in half**!"

                elif chosen_nerf == "beekeeper":
                    new_pos = self.resolve_nonroll_landing_tile(max(0, current_pos - 3))
                    await asyncio.to_thread(self.log_command, chosen_team, "/card_effect_set_tile", {"team": chosen_team, "tile": new_pos})
                    embed_desc = f"🐝 **The Beekeeper!**\n**{chosen_team}** failed to build the hive and got swarmed! They panic and flee backwards **3 tiles** to Tile **{new_pos}**!"

                elif chosen_nerf == "plant":
                    col = headers.index("Poisoned Roll") + 1 if "Poisoned Roll" in headers else -1
                    if col != -1: await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, col, "yes")
                    embed_desc = f"🥀 **The Strange Plant!**\nA strange plant poisons **{chosen_team}**, severely draining their stamina! They can barely walk—their next dice roll **cannot exceed a 3**!"

                elif chosen_nerf == "jekyll":
                    house_records = await asyncio.to_thread(self.house_data_sheet.get_all_records)
                    owned_houses = [r for r in house_records if str(r.get("OwnerTeam", "")).strip() == chosen_team]
                    if owned_houses:
                        target_prop = random.choice(owned_houses)
                        prop_idx = house_records.index(target_prop) + 2
                        current_count = int(target_prop.get("HouseCount", 0))
                        if current_count <= 1:
                            await asyncio.to_thread(self.house_data_sheet.update_cell, prop_idx, 3, "") 
                            await asyncio.to_thread(self.house_data_sheet.update_cell, prop_idx, 4, 0)
                        else:
                            await asyncio.to_thread(self.house_data_sheet.update_cell, prop_idx, 4, current_count - 1)
                        
                        await asyncio.to_thread(self.sync_houses_owned, chosen_team)
                        embed_desc = f"🧪 **Mr. Hyde's Rampage!**\n**{chosen_team}** refused to hand over a guam leaf... Mr. Hyde goes berserk! **1 House** on Tile **{target_prop.get('Tile')}** has been completely destroyed!"
                    else:
                        embed_desc = f"🧪 **Mr. Hyde's Rampage!**\nMr. Hyde attacks **{chosen_team}**, but they don't own any houses to destroy! They narrowly escape."

                elif chosen_nerf == "gravedigger":
                    col = headers.index("Roll Penalty") + 1 if "Roll Penalty" in headers else -1
                    if col != -1: await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, col, "3")
                    embed_desc = f"🪦 **The Gravedigger!**\nLeo forces **{chosen_team}** to organize heavy coffins. A heavy fatigue penalty is applied; their next dice roll will receive a strict **-3 penalty**!"

                elif chosen_nerf == "maze":
                    spaces_back = random.randint(1, 12)
                    
                    new_pos = max(0, current_pos - spaces_back)
                    
                    if hasattr(self, "resolve_nonroll_landing_tile"):
                        new_pos = self.resolve_nonroll_landing_tile(new_pos)
                        
                    await asyncio.to_thread(self.log_command, chosen_team, "/card_effect_set_tile", {"team": chosen_team, "tile": new_pos})
                    
                    embed_desc = f"🧭 **The Mysterious Old Man's Maze!**\n**{chosen_team}** is dragged into the maze and completely loses their sense of direction! They eventually stumble out **{spaces_back}** spaces backwards, ending up on Tile **{new_pos}**!"

                elif chosen_nerf == "twin":
                    all_chance = await asyncio.to_thread(self.chance_sheet.get_all_records)
                    all_chest = await asyncio.to_thread(self.chest_sheet.get_all_records)
                    owned_cards = []
                    
                    for idx, r in enumerate(all_chance, start=2):
                        if chosen_team in [t.strip() for t in str(r.get("Held By Team", "")).split(",")]:
                            owned_cards.append({"sheet": self.chance_sheet, "row": idx, "data": r})
                    for idx, r in enumerate(all_chest, start=2):
                        if chosen_team in [t.strip() for t in str(r.get("Held By Team", "")).split(",")]:
                            owned_cards.append({"sheet": self.chest_sheet, "row": idx, "data": r})
                            
                    if owned_cards:
                        card_to_lose = random.choice(owned_cards)
                        teams_holding = [t.strip() for t in str(card_to_lose["data"].get("Held By Team", "")).split(",") if t.strip() != chosen_team]
                        
                        # Find an underdog (Multiplier of 1)
                        underdogs = [str(r.get("Team", "")) for r in records if float(r.get("Event Multiplier", 1)) == 1.0 and str(r.get("Team", "")) != chosen_team]
                        beneficiary = random.choice(underdogs) if underdogs else None
                        
                        if beneficiary:
                            teams_holding.append(beneficiary)
                            await asyncio.to_thread(card_to_lose["sheet"].update_cell, card_to_lose["row"], 3, ", ".join(teams_holding))
                            card_name = card_to_lose["data"].get("Name", "a card")
                            embed_desc = f"👯 **The Evil Twin!**\nMolly's evil twin frames **{chosen_team}**! Their **{card_name}** card is confiscated by the authorities and awarded to **{beneficiary}** as compensation!"
                        else:
                            await asyncio.to_thread(card_to_lose["sheet"].update_cell, card_to_lose["row"], 3, ", ".join(teams_holding))
                            embed_desc = f"👯 **The Evil Twin!**\nMolly's evil twin frames **{chosen_team}**! Their **{card_to_lose['data'].get('Name')}** card is confiscated by the authorities and destroyed!"
                    else:
                        embed_desc = f"👯 **The Evil Twin!**\nMolly's evil twin attempts to frame **{chosen_team}**, but their pockets are completely empty!"

                elif chosen_nerf == "pete":
                    await asyncio.to_thread(self.log_command, chosen_team, "/card_effect_set_tile", {"team": chosen_team, "tile": 10})
                    if hasattr(self, "set_jail_status"): await asyncio.to_thread(self.set_jail_status, chosen_team, "yes")
                    embed_desc = f"🎈 **Prison Pete!**\n**{chosen_team}** is trapped in the balloon animal cage! They are instantly dragged to **Tile 10 (Jail)**!"

                elif chosen_nerf == "bob":
                    if hasattr(self, "set_teleblock_status"): await asyncio.to_thread(self.set_teleblock_status, chosen_team, "yes")
                    embed_desc = f"🐈‍⬛ **Evil Bob!**\n**{chosen_team}** is kidnapped to ScapeRune to catch uncerted fish! They are **Teleblocked** until their next roll!"

                elif chosen_nerf == "mime":
                    col = headers.index("Silenced") + 1 if "Silenced" in headers else -1
                    if col != -1: await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, col, "yes")
                    embed_desc = f"🎭 **The Mime!**\n**{chosen_team}** failed to copy the Mime's emotes! A silencing aura is cast over them. They are **unable to use ANY cards** until they roll the dice again!"
            
            # ==========================================
            # 🟢 BUFF MECHANICS
            # ==========================================
            else:
                event_title = "✨ A Blessing Appears!"
                buff_pool = ["certers", "arnav", "oldman", "frog", "countcheck", "exam", "genie"]
                chosen_buff = random.choice(buff_pool)

                if chosen_buff == "certers":
                    await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, gp_col, current_gp + 30_000_000)
                    embed_desc = f"📜 **The Certers!**\nNiles, Miles, and Giles uncert some rare items for **{chosen_team}**! They have been granted a massive injection of **30,000,000 GP**!"

                elif chosen_buff == "arnav":
                    all_chest = await asyncio.to_thread(self.chest_sheet.get_all_records)
                    available_cards = [r for r in all_chest if chosen_team not in [t.strip() for t in str(r.get("Held By Team", "")).split(",")]]
                    
                    if available_cards:
                        drawn_card = random.choice(available_cards)
                        card_idx = all_chest.index(drawn_card) + 2
                        current_holders = [t.strip() for t in str(drawn_card.get("Held By Team", "")).split(",") if t.strip()]
                        current_holders.append(chosen_team)
                        await asyncio.to_thread(self.chest_sheet.update_cell, card_idx, 3, ", ".join(current_holders))
                        embed_desc = f"🏴‍☠️ **Capt' Arnav's Chest!**\n**{chosen_team}** successfully cracked the combination! They have been granted a free **{drawn_card.get('Name')}** Chest card!"
                    else:
                        await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, gp_col, current_gp + 10_000_000)
                        embed_desc = f"🏴‍☠️ **Capt' Arnav's Chest!**\n**{chosen_team}** opened the chest but already has all the cards! They found **10,000,000 GP** instead!"

                elif chosen_buff == "oldman":
                    all_chance = await asyncio.to_thread(self.chance_sheet.get_all_records)
                    available_cards = [r for r in all_chance if chosen_team not in [t.strip() for t in str(r.get("Held By Team", "")).split(",")]]
                    
                    if available_cards:
                        drawn_card = random.choice(available_cards)
                        card_idx = all_chance.index(drawn_card) + 2
                        current_holders = [t.strip() for t in str(drawn_card.get("Held By Team", "")).split(",") if t.strip()]
                        current_holders.append(chosen_team)
                        await asyncio.to_thread(self.chance_sheet.update_cell, card_idx, 3, ", ".join(current_holders))
                        embed_desc = f"🎁 **The Mysterious Old Man!**\n**{chosen_team}** successfully solved the Strange Box! They have been granted a free **{drawn_card.get('Name')}** Chance card!"
                    else:
                        await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, gp_col, current_gp + 10_000_000)
                        embed_desc = f"🎁 **The Mysterious Old Man!**\n**{chosen_team}** solved the box but already has all the cards! They found **10,000,000 GP** inside instead!"

                elif chosen_buff == "frog":
                    await asyncio.to_thread(self.increment_rolls_available, chosen_team)
                    embed_desc = f"🐸 **Kiss the Frog!**\n**{chosen_team}** kisses the royal frog and breaks the curse! The Frog Princess has rewarded them with an immediate **Free Dice Roll**!"

                elif chosen_buff == "countcheck":
                    col = headers.index("Double Card") + 1 if "Double Card" in headers else -1
                    if col != -1: await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, col, "yes")
                    embed_desc = f"✅ **Count Check!**\n**{chosen_team}** sets up their Authenticator and Bank PIN! Their account security grants them the ability to use **TWO cards** on their current tile instead of just one!"

                elif chosen_buff == "exam":
                    all_chance = await asyncio.to_thread(self.chance_sheet.get_all_records)
                    all_chest = await asyncio.to_thread(self.chest_sheet.get_all_records)
                    owned_cards_count = sum(1 for r in all_chance + all_chest if chosen_team in [t.strip() for t in str(r.get("Held By Team", "")).split(",")])
                    
                    if owned_cards_count == 0:
                        await asyncio.to_thread(self.increment_rolls_available, chosen_team)
                        embed_desc = f"🍎 **Surprise Exam!**\nMr. Mordaut notices **{chosen_team}** has empty pockets and takes pity on them. He awards them a **Free Dice Roll**!"
                    else:
                        unowned_cards = [
                            {"sheet": self.chance_sheet, "row": all_chance.index(r) + 2, "data": r} for r in all_chance if chosen_team not in [t.strip() for t in str(r.get("Held By Team", "")).split(",")]
                        ] + [
                            {"sheet": self.chest_sheet, "row": all_chest.index(r) + 2, "data": r} for r in all_chest if chosen_team not in [t.strip() for t in str(r.get("Held By Team", "")).split(",")]
                        ]
                        
                        if unowned_cards:
                            drawn_card = random.choice(unowned_cards)
                            current_holders = [t.strip() for t in str(drawn_card["data"].get("Held By Team", "")).split(",") if t.strip()]
                            current_holders.append(chosen_team)
                            await asyncio.to_thread(drawn_card["sheet"].update_cell, drawn_card["row"], 3, ", ".join(current_holders))
                            embed_desc = f"🍎 **Surprise Exam!**\nMr. Mordaut tests **{chosen_team}**, and they score an A+! They are awarded a free **{drawn_card['data'].get('Name')}** card!"
                        else:
                            await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, gp_col, current_gp + 10_000_000)
                            embed_desc = f"🍎 **Surprise Exam!**\nMr. Mordaut tests **{chosen_team}**, but they already know everything! He awards them a **10,000,000 GP** scholarship instead!"

                elif chosen_buff == "genie":
                    boost = int(current_gp * 0.15)
                    await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, gp_col, current_gp + boost)
                    embed_desc = f"🧞 **The Genie!**\n*\"A wish granted!\"* The Genie magically multiplies **{chosen_team}**'s wealth, granting them a permanent **15% boost** to their current GP stack (**+{boost:,} GP**)!"

            # 4. Announce the Chaos
            if force_trigger:
                embed_desc += f"\n\n*(Triggered via testing force command for **{chosen_team}**)*"
                
            embed = discord.Embed(title=event_title, description=embed_desc, color=embed_color)
            await interaction.followup.send(embed=embed)
            await self.mirror_to_game_log(interaction.channel, embed=embed)

        except Exception as e:
            print(f"❌ Error in /random_event: {e}")
            traceback.print_exc()
            await interaction.followup.send("❌ A database error occurred while rolling the random event.", ephemeral=True)

    async def trigger_passive_random_event(self, channel: discord.TextChannel, team_name: str):
        """Silently handles a random event if the 5% spawn chance is met in /roll."""
        try:
            # 1. Fetch a fresh snapshot so we have their updated GP and Position from the roll
            records = await asyncio.to_thread(self.team_data_sheet.get_all_records)
            
            team_info = next((r for r in records if str(r.get("Team", "")).strip().lower() == team_name.strip().lower()), None)
            if not team_info: return

            chosen_team = str(team_info.get("Team")).strip()
            team_row_idx = records.index(team_info) + 2
            
            # Find max multiplier on the board for the Buff math
            team_multipliers = []
            for row in records:
                try:
                    mult = float(row.get("Multiplier", 1))
                except ValueError:
                    mult = 1.0
                team_multipliers.append(mult)
                
            max_mult = max(team_multipliers) if team_multipliers else 1.0
            
            # Get Victim's Multiplier
            try:
                victim_mult = float(team_info.get("Multiplier", 1))
            except ValueError:
                victim_mult = 1.0

            # 2. Determine Nerf vs Buff using the Inverse Weight Math
            nerf_weight = victim_mult
            buff_weight = (max_mult - victim_mult) + 1.0
            
            event_type = random.choices(["nerf", "buff"], weights=[nerf_weight, buff_weight], k=1)[0]
            
            headers = list(records[0].keys())
            gp_col = headers.index("GP") + 1 if "GP" in headers else -1
            current_gp = int(str(team_info.get("GP", 0)).replace(',', ''))
            current_pos = int(team_info.get("Position", 0))

            embed_desc = ""
            event_title = ""
            embed_color = discord.Color.red() if event_type == "nerf" else discord.Color.green()

            # ==========================================
            # 🔴 NERF MECHANICS
            # ==========================================
            if event_type == "nerf":
                event_title = "⚠️ A Disastrous Random Event Appears!"
                nerf_pool = [
                    "dwarf", "whirlpool", "ents", "forester", "bob", "twin", 
                    "pete", "gravedigger", "sandwich", "jekyll", "demon", 
                    "plant", "beekeeper", "mime", "maze"
                ]
                chosen_nerf = random.choice(nerf_pool)

                if chosen_nerf == "dwarf":
                    fine = int(current_gp * 0.20)
                    await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, gp_col, current_gp - fine)
                    embed_desc = f"🍺 **The Drunken Dwarf!**\n*\"Have a kebab, mate!\"* The dwarf corners **{chosen_team}** and forces them to pay his massive bar tab! They lose **20%** of their total wealth (**{fine:,} GP**)!"

                elif chosen_nerf == "ents":
                    col = headers.index("GP Halved") + 1 if "GP Halved" in headers else -1
                    if col != -1: await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, col, "yes")
                    embed_desc = f"🌳 **The Ents!**\nAn ent grew and shakes **{chosen_team}** upside down! Their gear is damaged. **All GP earned is cut in half** until their next roll!"

                elif chosen_nerf == "forester":
                    all_chance = await asyncio.to_thread(self.chance_sheet.get_all_records)
                    all_chest = await asyncio.to_thread(self.chest_sheet.get_all_records)
                    owned_cards = []
                    for idx, r in enumerate(all_chance, start=2):
                        if chosen_team in [t.strip() for t in str(r.get("Held By Team", "")).split(",")]:
                            owned_cards.append({"sheet": self.chance_sheet, "row": idx, "data": r})
                    for idx, r in enumerate(all_chest, start=2):
                        if chosen_team in [t.strip() for t in str(r.get("Held By Team", "")).split(",")]:
                            owned_cards.append({"sheet": self.chest_sheet, "row": idx, "data": r})
                            
                    if owned_cards:
                        card_to_lose = random.choice(owned_cards)
                        teams_holding = [t.strip() for t in str(card_to_lose["data"].get("Held By Team", "")).split(",") if t.strip() != chosen_team]
                        await asyncio.to_thread(card_to_lose["sheet"].update_cell, card_to_lose["row"], 3, ", ".join(teams_holding))
                        embed_desc = f"🌽 **The Freaky Forester!**\n*\"You killed the wrong pheasant!\"* The Forester banishes **{chosen_team}** and strips them of their **{card_to_lose['data'].get('Name')}** card!"
                    else:
                        fine = int(current_gp * 0.15)
                        await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, gp_col, current_gp - fine)
                        embed_desc = f"🌽 **The Freaky Forester!**\n*\"You killed the wrong pheasant!\"* **{chosen_team}** had no cards to give, so they were fined **15%** of their wealth (**{fine:,} GP**)!"

                elif chosen_nerf == "whirlpool":
                    spaces_back = random.randint(1, 6)
                    new_pos = max(0, current_pos - spaces_back)
                    if hasattr(self, "resolve_nonroll_landing_tile"): new_pos = self.resolve_nonroll_landing_tile(new_pos)
                    await asyncio.to_thread(self.log_command, chosen_team, "/card_effect_set_tile", {"team": chosen_team, "tile": new_pos})
                    embed_desc = f"🌀 **The Whirlpool!**\nA sudden whirlpool sucks **{chosen_team}** under! They wash up **{spaces_back}** spaces backwards on Tile **{new_pos}**!"

                elif chosen_nerf == "sandwich":
                    spaces_back = random.randint(1, 6)
                    new_pos = max(0, current_pos - spaces_back)
                    await asyncio.to_thread(self.log_command, chosen_team, "/card_effect_set_tile", {"team": chosen_team, "tile": new_pos})
                    embed_desc = f"🥖 **The Sandwich Lady!**\n*\"You picked the wrong sandwich!\"* She whacks **{chosen_team}** with a stale baguette! They are knocked **{spaces_back}** tiles backwards to Tile **{new_pos}** and receive **no tile rewards**!"

                elif chosen_nerf == "demon":
                    col = headers.index("Roll Halved") + 1 if "Roll Halved" in headers else -1
                    if col != -1: await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, col, "yes")
                    embed_desc = f"🏋️ **The Demon Drill Sergeant!**\n*\"Drop and give me 50!\"* The Demon exhausts **{chosen_team}**. Their next dice roll is strictly **cut in half**!"

                elif chosen_nerf == "beekeeper":
                    new_pos = max(0, current_pos - 3)
                    if hasattr(self, "resolve_nonroll_landing_tile"): new_pos = self.resolve_nonroll_landing_tile(new_pos)
                    await asyncio.to_thread(self.log_command, chosen_team, "/card_effect_set_tile", {"team": chosen_team, "tile": new_pos})
                    embed_desc = f"🐝 **The Beekeeper!**\n**{chosen_team}** failed to build the hive and got swarmed! They panic and flee backwards **3 tiles** to Tile **{new_pos}**!"

                elif chosen_nerf == "plant":
                    col = headers.index("Poisoned Roll") + 1 if "Poisoned Roll" in headers else -1
                    if col != -1: await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, col, "yes")
                    embed_desc = f"🥀 **The Strange Plant!**\nA strange plant poisons **{chosen_team}**, severely draining their stamina! They can barely walk—their next dice roll **cannot exceed a 3**!"

                elif chosen_nerf == "jekyll":
                    house_records = await asyncio.to_thread(self.house_data_sheet.get_all_records)
                    owned_houses = [r for r in house_records if str(r.get("OwnerTeam", "")).strip() == chosen_team]
                    if owned_houses:
                        target_prop = random.choice(owned_houses)
                        prop_idx = house_records.index(target_prop) + 2
                        current_count = int(target_prop.get("HouseCount", 0))
                        if current_count <= 1:
                            await asyncio.to_thread(self.house_data_sheet.update_cell, prop_idx, 3, "") 
                            await asyncio.to_thread(self.house_data_sheet.update_cell, prop_idx, 4, 0)
                        else:
                            await asyncio.to_thread(self.house_data_sheet.update_cell, prop_idx, 4, current_count - 1)
                        await asyncio.to_thread(self.sync_houses_owned, chosen_team)
                        embed_desc = f"🧪 **Mr. Hyde's Rampage!**\n**{chosen_team}** refused to hand over a guam leaf... Mr. Hyde goes berserk! **1 House** on Tile **{target_prop.get('Tile')}** has been completely destroyed!"
                    else:
                        embed_desc = f"🧪 **Mr. Hyde's Rampage!**\nMr. Hyde attacks **{chosen_team}**, but they don't own any houses to destroy! They narrowly escape."

                elif chosen_nerf == "gravedigger":
                    col = headers.index("Roll Penalty") + 1 if "Roll Penalty" in headers else -1
                    if col != -1: await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, col, "3")
                    embed_desc = f"🪦 **The Gravedigger!**\nLeo forces **{chosen_team}** to organize heavy coffins. A heavy fatigue penalty is applied; their next dice roll will receive a strict **-3 penalty**!"

                elif chosen_nerf == "maze":
                    spaces_back = random.randint(1, 12)
                    new_pos = max(0, current_pos - spaces_back)
                    if hasattr(self, "resolve_nonroll_landing_tile"): new_pos = self.resolve_nonroll_landing_tile(new_pos)
                    await asyncio.to_thread(self.log_command, chosen_team, "/card_effect_set_tile", {"team": chosen_team, "tile": new_pos})
                    embed_desc = f"🧩 **The Mysterious Old Man's Maze!**\n**{chosen_team}** is dragged into the maze and completely loses their sense of direction! They eventually stumble out **{spaces_back}** spaces backwards, ending up on Tile **{new_pos}**!"

                elif chosen_nerf == "twin":
                    all_chance = await asyncio.to_thread(self.chance_sheet.get_all_records)
                    all_chest = await asyncio.to_thread(self.chest_sheet.get_all_records)
                    owned_cards = []
                    for idx, r in enumerate(all_chance, start=2):
                        if chosen_team in [t.strip() for t in str(r.get("Held By Team", "")).split(",")]:
                            owned_cards.append({"sheet": self.chance_sheet, "row": idx, "data": r})
                    for idx, r in enumerate(all_chest, start=2):
                        if chosen_team in [t.strip() for t in str(r.get("Held By Team", "")).split(",")]:
                            owned_cards.append({"sheet": self.chest_sheet, "row": idx, "data": r})
                            
                    if owned_cards:
                        card_to_lose = random.choice(owned_cards)
                        teams_holding = [t.strip() for t in str(card_to_lose["data"].get("Held By Team", "")).split(",") if t.strip() != chosen_team]
                        underdogs = [str(r.get("Team", "")) for r in records if float(r.get("Multiplier", 1)) == 1.0 and str(r.get("Team", "")) != chosen_team]
                        beneficiary = random.choice(underdogs) if underdogs else None
                        
                        if beneficiary:
                            teams_holding.append(beneficiary)
                            await asyncio.to_thread(card_to_lose["sheet"].update_cell, card_to_lose["row"], 3, ", ".join(teams_holding))
                            embed_desc = f"👯 **The Evil Twin!**\nMolly's evil twin frames **{chosen_team}**! Their **{card_to_lose['data'].get('Name')}** card is confiscated by the authorities and awarded to **{beneficiary}** as compensation!"
                        else:
                            await asyncio.to_thread(card_to_lose["sheet"].update_cell, card_to_lose["row"], 3, ", ".join(teams_holding))
                            embed_desc = f"👯 **The Evil Twin!**\nMolly's evil twin frames **{chosen_team}**! Their **{card_to_lose['data'].get('Name')}** card is confiscated by the authorities and destroyed!"
                    else:
                        embed_desc = f"👯 **The Evil Twin!**\nMolly's evil twin attempts to frame **{chosen_team}**, but their pockets are completely empty!"

                elif chosen_nerf == "pete":
                    await asyncio.to_thread(self.log_command, chosen_team, "/card_effect_set_tile", {"team": chosen_team, "tile": 10})
                    if hasattr(self, "set_jail_status"): await asyncio.to_thread(self.set_jail_status, chosen_team, "yes")
                    embed_desc = f"🎈 **Prison Pete!**\n**{chosen_team}** is trapped in the balloon animal cage! They are instantly dragged to **Tile 10 (Jail)**!"

                elif chosen_nerf == "bob":
                    if hasattr(self, "set_teleblock_status"): await asyncio.to_thread(self.set_teleblock_status, chosen_team, "yes")
                    embed_desc = f"🐈‍⬛ **Evil Bob!**\n**{chosen_team}** is kidnapped to ScapeRune to catch uncerted fish! They are **Teleblocked** until their next roll!"

                elif chosen_nerf == "mime":
                    col = headers.index("Silenced") + 1 if "Silenced" in headers else -1
                    if col != -1: await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, col, "yes")
                    embed_desc = f"🎭 **The Mime!**\n**{chosen_team}** failed to copy the Mime's emotes! A silencing aura is cast over them. They are **unable to use ANY cards** until they roll the dice again!"

            # ==========================================
            # 🟢 BUFF MECHANICS
            # ==========================================
            else:
                event_title = "✨ A Blessing Appears!"
                buff_pool = ["certers", "arnav", "oldman", "frog", "countcheck", "exam", "genie"]
                chosen_buff = random.choice(buff_pool)

                if chosen_buff == "certers":
                    await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, gp_col, current_gp + 30_000_000)
                    embed_desc = f"📜 **The Certers!**\nNiles, Miles, and Giles uncert some rare items for **{chosen_team}**! They have been granted a massive injection of **30,000,000 GP**!"

                elif chosen_buff == "arnav":
                    all_chest = await asyncio.to_thread(self.chest_sheet.get_all_records)
                    available_cards = [r for r in all_chest if chosen_team not in [t.strip() for t in str(r.get("Held By Team", "")).split(",")]]
                    if available_cards:
                        drawn_card = random.choice(available_cards)
                        card_idx = all_chest.index(drawn_card) + 2
                        current_holders = [t.strip() for t in str(drawn_card.get("Held By Team", "")).split(",") if t.strip()]
                        current_holders.append(chosen_team)
                        await asyncio.to_thread(self.chest_sheet.update_cell, card_idx, 3, ", ".join(current_holders))
                        embed_desc = f"🏴‍☠️ **Capt' Arnav's Chest!**\n**{chosen_team}** successfully cracked the combination! They have been granted a free **{drawn_card.get('Name')}** Chest card!"
                    else:
                        await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, gp_col, current_gp + 10_000_000)
                        embed_desc = f"🏴‍☠️ **Capt' Arnav's Chest!**\n**{chosen_team}** opened the chest but already has all the cards! They found **10,000,000 GP** instead!"

                elif chosen_buff == "oldman":
                    all_chance = await asyncio.to_thread(self.chance_sheet.get_all_records)
                    available_cards = [r for r in all_chance if chosen_team not in [t.strip() for t in str(r.get("Held By Team", "")).split(",")]]
                    if available_cards:
                        drawn_card = random.choice(available_cards)
                        card_idx = all_chance.index(drawn_card) + 2
                        current_holders = [t.strip() for t in str(drawn_card.get("Held By Team", "")).split(",") if t.strip()]
                        current_holders.append(chosen_team)
                        await asyncio.to_thread(self.chance_sheet.update_cell, card_idx, 3, ", ".join(current_holders))
                        embed_desc = f"🎁 **The Mysterious Old Man!**\n**{chosen_team}** successfully solved the Strange Box! They have been granted a free **{drawn_card.get('Name')}** Chance card!"
                    else:
                        await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, gp_col, current_gp + 10_000_000)
                        embed_desc = f"🎁 **The Mysterious Old Man!**\n**{chosen_team}** solved the box but already has all the cards! They found **10,000,000 GP** inside instead!"

                elif chosen_buff == "frog":
                    await asyncio.to_thread(self.increment_rolls_available, chosen_team)
                    embed_desc = f"🐸 **Kiss the Frog!**\n**{chosen_team}** kisses the royal frog and breaks the curse! The Frog Princess has rewarded them with an immediate **Free Dice Roll**!"

                elif chosen_buff == "countcheck":
                    col = headers.index("Double Card") + 1 if "Double Card" in headers else -1
                    if col != -1: await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, col, "yes")
                    embed_desc = f"✅ **Count Check!**\n**{chosen_team}** sets up their Authenticator and Bank PIN! Their account security grants them the ability to use **TWO cards** on their current tile instead of just one!"

                elif chosen_buff == "exam":
                    all_chance = await asyncio.to_thread(self.chance_sheet.get_all_records)
                    all_chest = await asyncio.to_thread(self.chest_sheet.get_all_records)
                    owned_cards_count = sum(1 for r in all_chance + all_chest if chosen_team in [t.strip() for t in str(r.get("Held By Team", "")).split(",")])
                    if owned_cards_count == 0:
                        await asyncio.to_thread(self.increment_rolls_available, chosen_team)
                        embed_desc = f"🍎 **Surprise Exam!**\nMr. Mordaut notices **{chosen_team}** has empty pockets and takes pity on them. He awards them a **Free Dice Roll**!"
                    else:
                        unowned_cards = [
                            {"sheet": self.chance_sheet, "row": all_chance.index(r) + 2, "data": r} for r in all_chance if chosen_team not in [t.strip() for t in str(r.get("Held By Team", "")).split(",")]
                        ] + [
                            {"sheet": self.chest_sheet, "row": all_chest.index(r) + 2, "data": r} for r in all_chest if chosen_team not in [t.strip() for t in str(r.get("Held By Team", "")).split(",")]
                        ]
                        if unowned_cards:
                            drawn_card = random.choice(unowned_cards)
                            current_holders = [t.strip() for t in str(drawn_card["data"].get("Held By Team", "")).split(",") if t.strip()]
                            current_holders.append(chosen_team)
                            await asyncio.to_thread(drawn_card["sheet"].update_cell, drawn_card["row"], 3, ", ".join(current_holders))
                            embed_desc = f"🍎 **Surprise Exam!**\nMr. Mordaut tests **{chosen_team}**, and they score an A+! They are awarded a free **{drawn_card['data'].get('Name')}** card!"
                        else:
                            await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, gp_col, current_gp + 10_000_000)
                            embed_desc = f"🍎 **Surprise Exam!**\nMr. Mordaut tests **{chosen_team}**, but they already know everything! He awards them a **10,000,000 GP** scholarship instead!"

                elif chosen_buff == "genie":
                    boost = int(current_gp * 0.15)
                    await asyncio.to_thread(self.team_data_sheet.update_cell, team_row_idx, gp_col, current_gp + boost)
                    embed_desc = f"🧞 **The Genie!**\n*\"A wish granted!\"* The Genie magically multiplies **{chosen_team}**'s wealth, granting them a permanent **15% boost** to their current GP stack (**+{boost:,} GP**)!"

            # 4. Announce the Chaos to the channel!
            embed = discord.Embed(title=event_title, description=embed_desc, color=embed_color)
            await channel.send(embed=embed)
            await self.mirror_to_game_log(channel, embed=embed)

        except Exception as e:
            print(f"❌ Error in trigger_passive_random_event: {e}")

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Listens for manual Discord role changes and updates the team list automatically."""
        if before.roles == after.roles:
            return

        before_teams = set(r.name for r in before.roles if r.name in ACTIVE_TEAMS)
        after_teams = set(r.name for r in after.roles if r.name in ACTIVE_TEAMS)

        if before_teams != after_teams:
            print(f"🔄 Role change detected for {after.display_name}. Updating live team list...")
            
            # 1. Wait 3 seconds to ensure Discord's database has caught up
            await asyncio.sleep(3.0)
            
            # 2. Force the bot to fetch the freshest version of this user directly from Discord's API
            # This overwrites any stale cache the bot might be holding onto!
            try:
                await after.guild.fetch_member(after.id)
            except discord.HTTPException:
                pass # Ignore if it fails, it will still try to update the board
                
            # 3. Draw the new board
            await self.update_live_team_list(after.guild)
    
    def get_team_captain(self, guild: discord.Guild, team_name: str) -> Optional[discord.Member]:
        """Dynamically finds the Captain of a specific team by checking roles."""
        team_role = discord.utils.get(guild.roles, name=team_name)
        if not team_role:
            return None
            
        for member in team_role.members:
            if self.has_event_captain_role(member):
                return member
        return None

    async def get_team_capacity_limits(self, guild: discord.Guild) -> dict:
        """Calculates dynamic team caps based on the Signups sheet (Row 10 and below)."""
        try:
            # Get raw values to bypass header parsing and slice exactly at Row 10
            values = await asyncio.to_thread(self.signup_sheet.get_all_values)
            
            total_draftable_players = 0
            
            # values[9:] grabs everything from Row 10 downwards (0-indexed)
            if len(values) >= 10:
                for row in values[9:]:
                    # Check if the row actually contains data (a name) to prevent counting empty rows
                    if any(str(cell).strip() for cell in row):
                        total_draftable_players += 1
            
            active_captains = len(ACTIVE_TEAMS)
            if active_captains == 0: 
                active_captains = 1 
                
            max_non_captains_per_team = math.ceil(total_draftable_players / active_captains)
            
            max_team_size = max_non_captains_per_team + 2

            capacity_data = {}
            for team_name in ACTIVE_TEAMS:
                role = discord.utils.get(guild.roles, name=team_name)
                current_size = len(role.members) if role else 0
                
                capacity_data[team_name] = {
                    "current": current_size,
                    "max": max_team_size,
                    "is_full": current_size >= max_team_size
                }
                
            return capacity_data
        except Exception as e:
            print(f"❌ Error calculating capacities: {e}")
            return {team: {"current": 0, "max": 99, "is_full": False} for team in ACTIVE_TEAMS}
            
    class CaptainApprovalView(ui.View):
        def __init__(self, cog, target_member: discord.Member, team_name: str):
            super().__init__(timeout=None)
            self.cog = cog
            self.target_member = target_member
            self.team_name = team_name

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if not self.cog.has_event_captain_role(interaction.user):
                await interaction.response.send_message("❌ Only Captains can use this button.", ephemeral=True)
                return False
            if self.cog.get_team(interaction.user) != self.team_name:
                await interaction.response.send_message(f"❌ You are not the captain of {self.team_name}.", ephemeral=True)
                return False
            return True

        # Note: I removed custom_id so Discord dynamically maps this specific button to this specific player
        @ui.button(label="Accept Player", style=discord.ButtonStyle.success)
        async def accept(self, interaction: discord.Interaction, button: ui.Button):
            role = discord.utils.get(interaction.guild.roles, name=self.team_name)
            if not role:
                await interaction.response.send_message(f"❌ Could not find the {self.team_name} role.", ephemeral=True)
                return

            embed = interaction.message.embeds[0]
            embed.color = discord.Color.green()
            embed.title = "✅ Request Accepted"
            embed.description = f"**{self.target_member.mention}** is now on **{self.team_name}**!"
            
            for child in self.children:
                child.disabled = True
                
            # Instantly update the message so the 3-second timer doesn't fail
            await interaction.response.edit_message(embed=embed, view=self)

            try:
                # Adding the role triggers the on_member_update listener in the background
                await self.target_member.add_roles(role, reason="Captain accepted team request")
            except Exception as e:
                print(f"❌ Error adding role in button click: {e}")

        @ui.button(label="Deny", style=discord.ButtonStyle.danger)
        async def deny(self, interaction: discord.Interaction, button: ui.Button):
            embed = interaction.message.embeds[0]
            embed.color = discord.Color.red()
            embed.title = "❌ Request Denied"
            embed.description = f"The request for **{self.target_member.mention}** to join was denied."
            
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(embed=embed, view=self)
    
    class PlayerAcceptView(ui.View):
        def __init__(self, cog, target_member: discord.Member, captain_member: discord.Member, team_name: str):
            super().__init__(timeout=None)
            self.cog = cog
            self.target_member = target_member
            self.captain_member = captain_member
            self.team_name = team_name

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user.id != self.target_member.id:
                await interaction.response.send_message("❌ This invite is not for you.", ephemeral=True)
                return False
            return True

        @ui.button(label="Accept Invite", style=discord.ButtonStyle.success)
        async def accept(self, interaction: discord.Interaction, button: ui.Button):
            role = discord.utils.get(interaction.guild.roles, name=self.team_name)
            if not role:
                await interaction.response.send_message(f"❌ Could not find the {self.team_name} role.", ephemeral=True)
                return

            embed = interaction.message.embeds[0]
            embed.color = discord.Color.green()
            embed.title = "✅ Invite Accepted"
            embed.description = f"**{self.target_member.mention}** has joined **{self.team_name}**!"
            
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(embed=embed, view=self)

            try:
                await self.target_member.add_roles(role, reason="Player accepted captain's invite")
            except Exception as e:
                print(f"❌ Error adding role in button click: {e}")

        @ui.button(label="Decline", style=discord.ButtonStyle.danger)
        async def deny(self, interaction: discord.Interaction, button: ui.Button):
            embed = interaction.message.embeds[0]
            embed.color = discord.Color.red()
            embed.title = "❌ Invite Declined"
            embed.description = f"**{self.target_member.mention}** declined the invite to {self.team_name}."
            
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(embed=embed, view=self)

    class TeamSelectionView(ui.View):
        def __init__(self, cog, guild: discord.Guild):
            # timeout=None ensures the buttons never expire so anyone can click them anytime!
            super().__init__(timeout=None)
            self.cog = cog
            
            for team in ACTIVE_TEAMS:
                captain = self.cog.get_team_captain(guild, team)
                # Use Captain's display name if found, otherwise default to Team name
                cap_name = captain.display_name if captain else team
                
                # Button is always clickable and only shows the Captain's name
                btn = ui.Button(
                    label=cap_name,
                    style=discord.ButtonStyle.primary,
                    custom_id=f"req_{team}"
                )
                btn.callback = self.make_callback(team, captain, cap_name)
                self.add_item(btn)

        def make_callback(self, team_name, captain: discord.Member, cap_name: str):
            async def callback(interaction: discord.Interaction):
                # 1. Check if the clicker is already on a team
                current_team = self.cog.get_team(interaction.user)
                if current_team:
                    await interaction.response.send_message(f"❌ You are already on **{current_team}**!", ephemeral=True)
                    return
                
                # 2. Check the capacity dynamically AT THE TIME of the click
                capacities = await self.cog.get_team_capacity_limits(interaction.guild)
                team_cap_data = capacities.get(team_name, {"is_full": False})
                
                if team_cap_data["is_full"]:
                    # Private error sent only to the person who clicked
                    await interaction.response.send_message(f"❌ **Action Denied:** {cap_name}'s team is currently at maximum capacity.", ephemeral=True)
                    return
                
                # 3. Success! Send the request to the Captain
                request_channel = self.cog.bot.get_channel(TEAM_REQUEST_CHANNEL_ID)
                if request_channel:
                    embed = discord.Embed(
                        title="📥 New Team Request",
                        description=f"**{interaction.user.mention}** has requested to join **{team_name}**!",
                        color=discord.Color.blue()
                    )
                    view = self.cog.CaptainApprovalView(self.cog, interaction.user, team_name)
                    
                    ping_text = captain.mention if captain else f"Attention {team_name} Captain!"
                    await request_channel.send(content=ping_text, embed=embed, view=view)
                    
                    await interaction.response.send_message(f"✅ Request sent to **{cap_name}**!", ephemeral=True)
                else:
                    await interaction.response.send_message("❌ Team request channel not found.", ephemeral=True)
            return callback

    @app_commands.command(name="team_request", description="Post a public team request board.")
    async def team_request(self, interaction: discord.Interaction):
        # Make the panel public so everyone can see and click the buttons
        await interaction.response.defer(ephemeral=False)
        
        embed = discord.Embed(
            title="🤝 Join a Team",
            description="Click a Captain below to send them a request to join their team. If their team is full, the bot will let you know!",
            color=discord.Color.blurple()
        )
        
        view = self.TeamSelectionView(self, interaction.guild)
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="player_request", description="[Captains Only] Request a player to join your team.")
    @app_commands.describe(player="The player you want to invite to your team")
    async def player_request(self, interaction: discord.Interaction, player: discord.Member):
        if not self.has_event_captain_role(interaction.user):
            await interaction.response.send_message("❌ Only Event Captains can use this command.", ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
        
        captain_team = self.get_team(interaction.user)
        if not captain_team:
            await interaction.followup.send("❌ You are a captain, but you don't have a team role assigned yet!", ephemeral=True)
            return

        target_team = self.get_team(player)
        if target_team:
            await interaction.followup.send(f"❌ **{player.display_name}** is already on **{target_team}**.", ephemeral=True)
            return

        capacities = await self.get_team_capacity_limits(interaction.guild)
        team_cap_data = capacities.get(captain_team)
        
        if team_cap_data and team_cap_data["is_full"]:
            await interaction.followup.send(f"❌ **Action Denied:** Your team is at its maximum capacity ({team_cap_data['max']} players).", ephemeral=True)
            return

        request_channel = self.bot.get_channel(TEAM_REQUEST_CHANNEL_ID)
        if not request_channel:
            await interaction.followup.send("❌ Team request channel not found.", ephemeral=True)
            return

        embed = discord.Embed(
            title="💌 You've been drafted!",
            description=f"**{interaction.user.mention}** wants you to join **{captain_team}**!\n\nDo you accept?",
            color=discord.Color.gold()
        )
        
        view = self.PlayerAcceptView(self, player, interaction.user, captain_team)
        await request_channel.send(content=f"{player.mention}", embed=embed, view=view)
        
        await interaction.followup.send(f"✅ An invite has been sent to **{player.display_name}** in <#{TEAM_REQUEST_CHANNEL_ID}>.", ephemeral=True)

    # ==========================================
    # 📋 LIVE TEAM LIST LOGIC
    # ==========================================

    @app_commands.command(name="signup_list", description="Post a live-updating list of signed-up players.")
    async def signup_list(self, interaction: discord.Interaction):
        if not self.has_event_staff_role(interaction.user):
            await interaction.response.send_message("❌ Only Event Staff can use this command.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=False)
        
        embed = await self.build_signup_list_embed()
        msg = await interaction.followup.send(embed=embed)
        
        self.save_signup_list_config(interaction.channel_id, msg.id)
        
        # We send a tiny private message so the channel doesn't get cluttered
        await interaction.followup.send("✅ Live signup list posted and linked.", ephemeral=True)

    @app_commands.command(name="signup_set_id", description="Link the bot to an existing signup list message.")
    @app_commands.describe(message_id="The ID of the message to update")
    async def signup_set_id(self, interaction: discord.Interaction, message_id: str):
        if not self.has_event_staff_role(interaction.user):
            await interaction.response.send_message("❌ Only Event Staff can use this.", ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
            
        try:
            msg_id_int = int(message_id.strip())
            msg = await interaction.channel.fetch_message(msg_id_int)
            
            self.save_signup_list_config(interaction.channel_id, msg.id)
            
            # Immediately force an update
            embed = await self.build_signup_list_embed()
            await msg.edit(embed=embed)
            
            await interaction.followup.send("✅ Successfully linked and updated the signup list message!", ephemeral=True)
        except discord.NotFound:
            await interaction.followup.send("❌ Message not found in this channel.", ephemeral=True)
        except ValueError:
            await interaction.followup.send("❌ Invalid message ID format.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)
    # ==========================================
    # 📝 LIVE SIGNUP LIST LOGIC
    # ==========================================

    def load_signup_list_config(self):
        """Loads the saved signup list message ID from a local file."""
        import os
        import json
        try:
            if os.path.exists(SIGNUP_LIST_CONFIG_FILE):
                with open(SIGNUP_LIST_CONFIG_FILE, "r") as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ Error loading signup list config: {e}")
        return {"channel_id": None, "message_id": None}

    def save_signup_list_config(self, channel_id: int, message_id: int):
        """Saves the signup list message ID so it survives bot resets."""
        import json
        try:
            with open(SIGNUP_LIST_CONFIG_FILE, "w") as f:
                json.dump({"channel_id": channel_id, "message_id": message_id}, f)
        except Exception as e:
            print(f"❌ Error saving signup list config: {e}")

    async def build_signup_list_embed(self) -> discord.Embed:
        """Fetches the Google Sheet and constructs the signup list embed."""
        values = await asyncio.to_thread(self.signup_sheet.get_all_values)
        rsn_list = []
        
        if len(values) >= 10:
            for row in values[9:]:
                if len(row) > 2:
                    rsn = str(row[2]).strip()
                    if rsn:
                        rsn_list.append(rsn)
                        
        if not rsn_list:
            return discord.Embed(
                title="📝 Current Signups",
                description="No one has signed up yet! Use `/signup` to be the first.",
                color=discord.Color.blue()
            )

        description = ""
        for i, rsn in enumerate(rsn_list, 1):
            line = f"**{i}.** {rsn}\n"
            if len(description) + len(line) > 4000:
                description += "\n*...and more! (List too long for Discord)*"
                break
            description += line
            
        embed = discord.Embed(
            title=f"📝 Current Signups ({len(rsn_list)} Total)",
            description=description,
            color=discord.Color.blue()
        )
        embed.set_footer(text="List updates automatically as players sign up!")
        return embed

    async def update_live_signup_list(self, guild: discord.Guild):
        """Fetches and edits the linked signup list message with fresh data."""
        config = self.load_signup_list_config()
        channel_id = config.get("channel_id")
        message_id = config.get("message_id")
        
        if not channel_id or not message_id:
            return
            
        channel = guild.get_channel(int(channel_id))
        if not channel:
            return
            
        try:
            msg = await channel.fetch_message(int(message_id))
            embed = await self.build_signup_list_embed()
            await msg.edit(embed=embed)
        except discord.NotFound:
            print("❌ Live signup list message was deleted.")
        except Exception as e:
            print(f"❌ Failed to update live signup list: {e}")
    
    @app_commands.command(name="team_list", description="Post a live-updating roster of all teams.")
    async def team_list(self, interaction: discord.Interaction):
        if not self.has_event_staff_role(interaction.user):
            await interaction.response.send_message("❌ Only Event Staff can use this command.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=False)
        
        # Calculate capacities before building the embed
        capacities = await self.get_team_capacity_limits(interaction.guild)
        embed = self.build_team_list_embed(interaction.guild, capacities)
        
        msg = await interaction.followup.send(embed=embed)
        self.save_team_list_config(interaction.channel_id, msg.id)
        
        await interaction.followup.send("✅ Live roster posted and linked. It will update automatically when players join.", ephemeral=True)

    @app_commands.command(name="team_list_set_id", description="Link the bot to an existing team list message.")
    @app_commands.describe(message_id="The ID of the message to update")
    async def team_list_set_id(self, interaction: discord.Interaction, message_id: str):
        if not self.has_event_staff_role(interaction.user):
            await interaction.response.send_message("❌ Only Event Staff can use this.", ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
            
        try:
            msg_id_int = int(message_id.strip())
            msg = await interaction.channel.fetch_message(msg_id_int)
            
            self.save_team_list_config(interaction.channel_id, msg.id)
            
            # Immediately force an update to prove it works
            capacities = await self.get_team_capacity_limits(interaction.guild)
            embed = self.build_team_list_embed(interaction.guild, capacities)
            await msg.edit(embed=embed)
            
            await interaction.followup.send("✅ Successfully linked and updated the team list message!", ephemeral=True)
        except discord.NotFound:
            await interaction.followup.send("❌ Message not found in this channel. You must run this command in the exact same channel as the target message.", ephemeral=True)
        except ValueError:
            await interaction.followup.send("❌ Invalid message ID format.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

    def load_team_list_config(self):
        """Loads the saved team list message ID from a local file."""
        import os
        import json
        try:
            # Make sure this filename matches your TEAM_LIST_CONFIG_FILE constant
            if os.path.exists("team_list_config.json"):
                with open("team_list_config.json", "r") as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ Error loading team list config: {e}")
        return {"channel_id": None, "message_id": None}

    def save_team_list_config(self, channel_id: int, message_id: int):
        """Saves the team list message ID so it survives bot resets."""
        try:
            with open(TEAM_LIST_CONFIG_FILE, "w") as f:
                json.dump({"channel_id": channel_id, "message_id": message_id}, f)
        except Exception as e:
            print(f"❌ Error saving team list config: {e}")

    def build_team_list_embed(self, guild: discord.Guild, capacities: dict) -> discord.Embed:
        """Constructs the roster embed showing all teams, keeping captains at the top."""
        embed = discord.Embed(title="🏆 Official Team Roster", color=discord.Color.gold())
        
        description = ""

        for team_name in ACTIVE_TEAMS:
            role = discord.utils.get(guild.roles, name=team_name)
            cap_data = capacities.get(team_name, {"current": 0, "max": 99, "is_full": False})
            
            cap_status = " 🔴 (FULL)" if cap_data["is_full"] else ""
            
            if role:
                # ---> THE FIX: Manually filter the fresh guild members list
                # instead of relying on the notoriously slow role.members property
                actual_members = [m for m in guild.members if role in m.roles]
                
                description += f"**{team_name} (Size: {len(actual_members)}/{cap_data['max']}){cap_status}**\n"
                
                if actual_members:
                    captains_list = []
                    players_list = []
                    
                    for member in actual_members:
                        if self.has_event_captain_role(member):
                            captains_list.append(member)
                        else:
                            players_list.append(member)
                            
                    for cap in captains_list:
                        description += f"👑 {cap.mention} • **Captain**\n"
                        
                    for player in players_list:
                        description += f"👤 {player.mention}\n"
                else:
                    description += "*No members drafted yet.*\n"
            else:
                description += f"**{team_name} (Size: 0/{cap_data['max']})**\n*Role '{team_name}' not found!*\n"
                
            description += "\n"
                
        embed.description = description
        embed.set_footer(text="Roster updates automatically as players are drafted!")
        return embed

    async def update_live_team_list(self, guild: discord.Guild):
        """Fetches and edits the linked team list message with fresh data."""
        config = self.load_team_list_config()
        channel_id = config.get("channel_id")
        message_id = config.get("message_id")
        
        if not channel_id or not message_id:
            return
            
        channel = guild.get_channel(int(channel_id))
        if not channel:
            return
            
        try:
            # ---> THE FIX: Force the bot to download a fresh member list from Discord 
            # so it doesn't use stale cached data from 3 seconds ago!
            await guild.chunk()
            
            msg = await channel.fetch_message(int(message_id))
            capacities = await self.get_team_capacity_limits(guild)
            embed = self.build_team_list_embed(guild, capacities)
            await msg.edit(embed=embed)
        except discord.NotFound:
            print("❌ Live team list message was deleted.")
        except Exception as e:
            print(f"❌ Failed to update live team list: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(MonopolyCog(bot))
