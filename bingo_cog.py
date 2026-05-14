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
    "Araxxor": ["Araxyte fang", "Nid", "Jar of venom"],
    "Barrows": ["Ahrim's hood", "Ahrim's robetop", "Ahrim's robeskirt", "Ahrim's staff", "Karil's coif", "Karil's leathertop", "Karil's leatherskirt", "Karil's crossbow", "Dharok's helm", "Dharok's platebody", "Dharok's platelegs", "Dharok's greataxe", "Guthan's helm", "Guthan's platebody", "Guthan's chainskirt", "Guthan's warspear", "Torag's helm", "Torag's platebody", "Torag's platelegs", "Torag's hammers", "Verac's helm", "Verac's brassard", "Verac's plateskirt", "Verac's flail"],
    "Callisto": ["Callisto cub", "Voidwaker hilt"],
    "Cerberus": ["Hellpuppy", "Eternal crystal", "Pegasian crystal", "Primordial crystal", "Jar of souls"],
    "Chambers of Xeric": ["Dexterous prayer scroll", "Arcane prayer scroll", "Kodai insignia", "Ancestral hat", "Ancestral robe top", "Ancestral robe bottom", "Elder maul", "Twisted bow", "Olmlet", "Twisted ancestral colour kit", "Metamorphic dust"],
    "Colosseum": ["Dizana's quiver (uncharged)", "Sunfire fanatic cuirass", "Sunfire fanatic chausses", "Sunfire fanatic helm", "Echo crystal", "Tonalztics of ralos (uncharged)"],
    "Commander Zilyana": ["Pet zilyana", "Armadyl crossbow", "Saradomin hilt", "Saradomin's light"],
    "Corporeal Beast": ["Pet dark core", "Elysian sigil", "Spectral sigil", "Arcane sigil", "Jar of spirits", "Spirit shield", "Holy Elixir"],
    "Dagannoth Kings": ["Pet dagannoth supreme", "Pet dagannoth rex", "Pet dagannoth prime", "Archers ring", "Seers ring", "Berserker ring", "Warrior ring"],
    "Demonic Gorilla": ["Zenyte shard"],
    "Doom of Mokhaiotl": ["Avernic treads", "Eye of ayak (uncharged)", "Mokhaiotl cloth"],
    "Duke Sucellus": ["Baron", "Virtus mask", "Virtus robe top", "Virtus robe bottom", "Eye of the duke"],
    "Gauntlet": ["Youngllef", "Crystal armour seed", "Enhanced crystal weapon seed"],
    "General Graardor": ["Pet general graardor", "Bandos hilt", "Bandos chestplate", "Bandos tassets", "Bandos boots"],
    "Giant Mole": ["Baby mole"],
    "Grotesque Guardians": ["Noon/midnight", "Jar of stone"],
    "Hueycoatl": ["Huberte", "Dragon hunter wand"],
    "Kalphite Queen": ["Kalphite princess", "Jar of sand"],
    "Kraken": ["Pet kraken", "Jar of Dirt"],
    "Kree'arra": ["Pet kree'arra", "Armadyl helmet", "Armadyl chestplate", "Armadyl chainskirt", "Armadyl hilt"],
    "K'ril Tsutsaroth": ["Pet K'ril Tsutsaroth", "Staff of the dead", "Zamorak hilt"],
    "King black dragon": ["Prince black dragon"],
    "Moons of Peril": ["Eclipse atlatl", "Eclipse moon helm", "Eclipse moon chestplate", "Eclipse moon tassets", "Dual macuahuitl", "Blood moon helm", "Blood moon chestplate", "Blood moon tassets", "Blue moon spear", "Blue moon helm", "Blue moon chestplate", "Blue moon tassets"],
    "Nightmare": ["Little nightmare/Parasite", "Nightmare staff", "Inquisitor's great helm", "Inquisitor's hauberk", "Inquisitor's plateskirt", "Inquisitor's mace", "Eldritch orb", "Harmonised orb", "Volatile orb", "Jar of dreams"],
    "Nex": ["Nexling", "Ancient hilt", "Nihil horn", "Zaryte vambraces", "Torva full helm (damaged)", "Torva platebody (damaged)", "Torva platelegs (damaged)"],
    "Royal Titans": ["Bran", "Fire element staff crown", "Ice element staff crown"],
    "Sarachnis": ["Sraracha", "Sarachnis cudgel", "Jar of eyes"],
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
    "Misc": ["Gull", "Muphin", "Smolcano", "Pet Drop", "Moxi", "Jar of feathers", "Prince black dragon", "Abyssal orphan"]
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
        
        # Primary drop submission sheet
        self.sheet = main_spreadsheet.sheet1

        # Bingo signup sheet.
        signup_worksheet_name = os.getenv("BINGO_SIGNUP_WORKSHEET", "Buy ins")
        try:
            self.signup_sheet = main_spreadsheet.worksheet(signup_worksheet_name)
            print(f"Bingo Cog: Signup worksheet loaded: {signup_worksheet_name}")
        except Exception as e:
            print(f"Bingo Cog: Could not load signup worksheet '{signup_worksheet_name}': {e}")
            print("Bingo Cog: Falling back to the first worksheet for signup submissions.")
            self.signup_sheet = main_spreadsheet.sheet1
        
        self.rsn_sheet = sheet_client.open_by_key("1ZwJiuVMp-3p8UH0NCVYTV9_UVI26jl5kWu2nvdspl9k").worksheet("Tracker")

        self.SUBMISSION_CHANNEL_ID = 1447066912159830149
        self.REVIEW_CHANNEL_ID = 1504315926017867847
        self.LOG_CHANNEL_ID = 1504315879431864372
        self.REQUIRED_ROLE_NAME = "Event Staff"
        self.REGISTERED_ROLE_NAME = "Registered"

        # Signup sheet layout based on the displayed signup spreadsheet.
        # Solo signups begin under the Solo Signups header at row 18.
        # Duo signups begin under the Duo Signups header at row 132.
        self.SOLO_SIGNUP_START_ROW = int(os.getenv("BINGO_SOLO_SIGNUP_START_ROW", "18"))
        self.SOLO_SIGNUP_END_ROW = int(os.getenv("BINGO_SOLO_SIGNUP_END_ROW", "130"))
        self.DUO_SIGNUP_START_ROW = int(os.getenv("BINGO_DUO_SIGNUP_START_ROW", "132"))
        self.DUO_SIGNUP_END_ROW = int(os.getenv("BINGO_DUO_SIGNUP_END_ROW", "232"))

        # Re-register the persistent panel buttons after bot restarts.
        self.bot.add_view(BingoSignupPanelView(self))
        
        print("Bingo Cog: Initialized successfully.")

    # --- Helpers ---

    def get_team_role_mention(self, member: discord.Member) -> str:
        """Get the team role mention for a member."""
        for role in member.roles:
            if role.name.startswith("Team "):
                return role.mention
        return "*No team*"

    def get_member_rank_name(self, member: discord.Member) -> str:
        """Best-effort rank helper for the signup sheet Rank column."""
        ignored_names = {"@everyone", self.REQUIRED_ROLE_NAME, self.REGISTERED_ROLE_NAME}
        ignored_prefixes = ("Team ",)

        for role in sorted(member.roles, key=lambda r: r.position, reverse=True):
            if role.name in ignored_names:
                continue
            if any(role.name.startswith(prefix) for prefix in ignored_prefixes):
                continue
            if getattr(role, "is_bot_managed", lambda: False)():
                continue
            if getattr(role, "is_integration", lambda: False)():
                continue
            return role.name
        return ""

    def normalize_signup_value(self, value) -> str:
        """Normalize values for matching signup rows."""
        return str(value or "").strip().casefold()

    def get_signup_bounds(self, signup_type: str) -> tuple[int, int]:
        """Return the configured row range for Solo or Duo signups."""
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

    def find_existing_signup_row(self, member: discord.Member, data: dict) -> Optional[int]:
        """Find the row this user should update, prioritizing Discord ID, then RSN."""
        signup_type = data.get("signup_type", "Solo")
        row = self.find_signup_row_by_discord_id(member.id, signup_type)
        if row:
            return row
        return self.find_signup_row_by_rsn(data.get("RSN", ""), signup_type)

    def merge_blank_signup_fields(self, row: int, new_values: list[str]) -> None:
        """Fill only blank cells in A-L, except Discord nickname may refresh and screenshot cells may be filled when empty."""
        current_values = self.get_signup_row_values(row)
        merged = []

        for index, new_value in enumerate(new_values):
            current_value = str(current_values[index]).strip() if index < len(current_values) else ""
            new_value = str(new_value or "").strip()

            # Keep the visible Discord nickname current when the user is the owner of this row.
            if index == 0 and new_value:
                merged.append(new_value)
                continue

            # Fill blanks only. This lets someone who was placeholder-signed-up complete missing fields
            # without accidentally overwriting information captains may already have reviewed.
            if not current_value and new_value:
                merged.append(new_value)
            else:
                merged.append(current_value)

        self.signup_sheet.update(f"A{row}:L{row}", [merged])

    def build_signup_row_values(self, member: Optional[discord.Member], data: dict, buyin_screenshot: str = "") -> list[str]:
        """Build columns A-L for a signup row."""
        signup_type = data.get("signup_type", "Solo")
        is_duo = signup_type == "Duo"

        return [
            member.display_name if member else data.get("Discord Nickname", ""),
            str(member.id) if member else data.get("Discord ID", ""),
            data.get("RSN", ""),
            data.get("Playtime", ""),
            data.get("Timezone/Location", ""),
            buyin_screenshot or data.get("Buy In Screenshot", ""),
            data.get("Comments", ""),
            "Yes" if is_duo else "No",
            data.get("Duo Partner", "") if is_duo else "",
            data.get("Duo Buy In Screenshot", "") if is_duo else "",
            data.get("Ironman", ""),
            self.get_member_rank_name(member) if member else data.get("Rank", ""),
        ]

    def write_or_update_signup_to_sheet(self, member: discord.Member, data: dict, buyin_screenshot: str) -> int:
        """Create a new signup row or fill blanks in an existing row."""
        if self.signup_sheet is None:
            raise RuntimeError("Signup sheet is not configured.")

        row = self.find_existing_signup_row(member, data)
        if row is None:
            row = self.find_next_signup_row(data.get("signup_type", "Solo"))

        row_values = self.build_signup_row_values(member, data, buyin_screenshot)
        self.merge_blank_signup_fields(row, row_values)
        return row

    def ensure_duo_partner_row(self, submitting_member: discord.Member, data: dict) -> int:
        """Make sure the duo partner has their own row, even if most fields are blank."""
        partner_rsn = data.get("Duo Partner", "").strip()
        if not partner_rsn:
            raise RuntimeError("Duo partner RSN is missing.")

        partner_row = self.find_signup_row_by_rsn(partner_rsn, "Duo")
        if partner_row is None:
            partner_row = self.find_next_signup_row("Duo")

        placeholder_data = {
            "signup_type": "Duo",
            "Discord Nickname": "",
            "Discord ID": "",
            "RSN": partner_rsn,
            "Playtime": "",
            "Timezone/Location": "",
            "Buy In Screenshot": "",
            "Comments": "",
            "Duo Partner": data.get("RSN", ""),
            "Duo Buy In Screenshot": data.get("Duo Buy In Screenshot", ""),
            "Ironman": "",
            "Rank": "",
        }
        self.merge_blank_signup_fields(partner_row, self.build_signup_row_values(None, placeholder_data))
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

    def build_signup_embeds(self, member: discord.Member, data: dict, image_urls: list[str]) -> list[discord.Embed]:
        """Build the public New Signup embed or embeds."""
        is_duo = data.get("signup_type") == "Duo"
        colour = discord.Colour.blue() if is_duo else discord.Colour.green()

        if is_duo:
            partner_text = data.get("Duo Partner", "your duo partner")
            title = f"New Signup! {member.display_name} has signed up as a duo with {partner_text}!"
        else:
            title = f"New Signup! {member.display_name} has signed up solo!"

        embeds = []
        first_embed = discord.Embed(title=title, colour=colour)
        first_embed.description = member.mention
        if image_urls:
            first_embed.set_image(url=image_urls[0])
        embeds.append(first_embed)

        # Discord only allows one large image per embed, so the optional second screenshot is shown in a second embed.
        if len(image_urls) > 1:
            second_embed = discord.Embed(title="Partner Buy-In Screenshot", colour=colour)
            second_embed.set_image(url=image_urls[1])
            embeds.append(second_embed)

        return embeds

    async def safe_delete_message(self, message: discord.Message) -> None:
        try:
            await message.delete()
        except discord.Forbidden:
            print("Bingo Cog: Missing permission to delete signup screenshot message.")
        except discord.HTTPException as e:
            print(f"Bingo Cog: Failed to delete signup screenshot message: {e}")

    async def collect_signup_screenshots(self, channel: discord.abc.Messageable, member: discord.Member, data: dict) -> None:
        """Wait for one required screenshot, then optionally a second duo screenshot."""
        signup_type = data.get("signup_type", "Solo")
        is_duo = signup_type == "Duo"

        def check(message: discord.Message) -> bool:
            return (
                message.author.id == member.id
                and message.channel.id == channel.id
                and len(message.attachments) > 0
            )

        try:
            first_message = await self.bot.wait_for("message", check=check, timeout=600)
            first_attachment = first_message.attachments[0]
            first_url = first_attachment.url
            await self.safe_delete_message(first_message)

            submitter_row = self.write_or_update_signup_to_sheet(member, data, first_url)
            partner_row = None
            if is_duo:
                partner_row = self.ensure_duo_partner_row(member, data)

            public_message = await channel.send(
                embeds=self.build_signup_embeds(member, data, [first_url])
            )

            if not is_duo:
                return

            # Optional partner screenshot. The signup is already submitted after the first screenshot.
            try:
                second_message = await self.bot.wait_for("message", check=check, timeout=300)
            except asyncio.TimeoutError:
                return

            second_attachment = second_message.attachments[0]
            second_url = second_attachment.url
            await self.safe_delete_message(second_message)

            self.update_duo_second_screenshot(submitter_row, partner_row, second_url)
            await public_message.edit(
                embeds=self.build_signup_embeds(member, data, [first_url, second_url])
            )

        except asyncio.TimeoutError:
            try:
                await channel.send(
                    f"{member.mention}, your signup timed out because no screenshot was posted.",
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

        await interaction.channel.send(embed=embed, view=BingoSignupPanelView(self))
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
        await interaction.response.send_modal(SoloSignupModal(self.cog))

    @discord.ui.button(
        label="Duo Signup",
        style=discord.ButtonStyle.blurple,
        custom_id="bingo_signup:duo"
    )
    async def duo_signup(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DuoSignupPageOneModal(self.cog))


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
        }

        await interaction.response.send_message(
            "**Step 2/2: Post Buy In Screenshot**\n"
            "Post your buy-in screenshot in this channel now. "
            "I will save it, delete your screenshot message, and post a public signup embed.",
            ephemeral=True
        )
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
        self.duo_partner = discord.ui.TextInput(
            label="Duo RSN",
            placeholder="The RSN of your duo partner.",
            required=True,
            max_length=50
        )
        self.playtime = discord.ui.TextInput(
            label="Playtime",
            placeholder="Estimated playtime for the event duration. Please be accurate.",
            required=True,
            max_length=100
        )

        self.add_item(self.rsn)
        self.add_item(self.duo_partner)
        self.add_item(self.playtime)

    async def on_submit(self, interaction: discord.Interaction):
        data = {
            "signup_type": "Duo",
            "RSN": str(self.rsn.value).strip(),
            "Duo Partner": str(self.duo_partner.value).strip(),
            "Playtime": str(self.playtime.value).strip(),
        }

        await interaction.response.send_message(
            "Page 1 saved. Press **Continue to Page 2** to finish your duo signup details.",
            view=DuoContinueSignupView(self.cog, data),
            ephemeral=True
        )


class DuoContinueSignupView(discord.ui.View):
    def __init__(self, cog: BingoCog, data: dict):
        super().__init__(timeout=600)
        self.cog = cog
        self.data = data

    @discord.ui.button(label="Continue to Page 2", style=discord.ButtonStyle.green)
    async def continue_to_page_two(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DuoSignupPageTwoModal(self.cog, self.data))


class DuoSignupPageTwoModal(discord.ui.Modal, title="Duo Signup - Page 2 of 2"):
    def __init__(self, cog: BingoCog, data: dict):
        super().__init__()
        self.cog = cog
        self.data = data

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

        self.add_item(self.timezone)
        self.add_item(self.comments)
        self.add_item(self.ironman)

    async def on_submit(self, interaction: discord.Interaction):
        self.data.update({
            "Timezone/Location": str(self.timezone.value).strip(),
            "Comments": str(self.comments.value).strip(),
            "Ironman": str(self.ironman.value).strip(),
        })

        await interaction.response.send_message(
            "**Step 3/3: Post Buy In Screenshot (Optionally, post a second screenshot for a partner)**\n"
            "Post your buy-in screenshot in this channel now. The signup submits after the first screenshot. "
            "If you are submitting your partner's buy-in too, post the second screenshot after the first one. "
            "I will save the image links, delete the screenshot messages, and post a public signup embed.",
            ephemeral=True
        )
        asyncio.create_task(self.cog.collect_signup_screenshots(interaction.channel, interaction.user, self.data))


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
                embed.set_image(url=self.image_url)
                await log_channel.send(embed=embed)
            except Exception as e:
                print(f"Bingo Cog: Failed to send to log channel: {e}")
                errors.append("Failed to log to channel")
        else:
            errors.append("Log channel not found")

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
            await asyncio.sleep(1)
            await self.message.delete()
        except Exception as e:
            print(f"Bingo Cog: Failed to delete review message: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(BingoCog(bot))
