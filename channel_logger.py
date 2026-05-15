import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands

import gspread
from google.oauth2.service_account import Credentials


# ============================================================
# CONFIG
# ============================================================

DROP_LOG_SHEET_ID = "1VjoOx_GdzD0dNP-SnbMDjhKV8M054QQ9JgRbLQeSe-M"

# Your sheet tab name.
DROP_LOG_TAB_NAME = "Drop Tab"

# Channel the bot watches for drop/pet/clog messages.
WATCH_CHANNEL_ID = 1272875477555482666

CST = ZoneInfo("America/Chicago")


# ============================================================
# MESSAGE CLEANUP
# ============================================================

def clean_clan_message(content: str) -> str:
    """
    Clan Chat messages sometimes escape punctuation when passed through Discord.

    Example:
    collection log item\\: Beekeeper's legs \\(135/1537\\)

    This turns it back into:
    collection log item: Beekeeper's legs (135/1537)
    """

    return (
        content
        .replace("\\:", ":")
        .replace("\\(", "(")
        .replace("\\)", ")")
        .replace("\\'", "'")
        .replace('\\"', '"')
        .replace("\\-", "-")
        .replace("\\.", ".")
    )


def clean_player_name(name: str) -> str:
    """
    Clan Chat names can come through like:
    <:Deputy_owner:1144313595925110857> **SpaceScape**

    This returns:
    SpaceScape
    """

    name = name.strip()

    # Remove custom Discord emojis like <:Deputy_owner:1144313595925110857>
    name = re.sub(r"<a?:[^:]+:\d+>", "", name)

    # If the name is bolded like **SpaceScape**, grab what's inside.
    bold_match = re.search(r"\*\*(.+?)\*\*", name)
    if bold_match:
        name = bold_match.group(1)

    # Remove leftover markdown symbols and whitespace.
    name = name.replace("*", "").strip()

    return name


def clean_drop_name(drop: str) -> str:
    """
    Removes trailing value/progress text from drops.

    Examples:
    Imbued heart (101,719,907 coins). -> Imbued heart
    Beekeeper's legs (135/1537) -> Beekeeper's legs
    """

    drop = drop.strip()

    # Clean escaped Discord punctuation first.
    drop = clean_clan_message(drop)

    # Remove anything from the first parenthesis onward.
    # Example: Imbued heart (101,719,907 coins). -> Imbued heart
    drop = re.sub(r"\s*\(.*$", "", drop).strip()

    # Remove leftover trailing punctuation.
    drop = drop.rstrip(".").strip()

    return drop


# ============================================================
# REGEX PATTERNS
# ============================================================

# Normal drop format:
#
# Player received a drop: Item Name
#
# Example:
# <:Deputy_owner:1144313595925110857> **SpaceScape** received a drop: Imbued heart (101,719,907 coins).
NORMAL_DROP_PATTERN = re.compile(
    r"^(?:<a?:[^:]+:\d+>\s*)?(?P<player>.+?)\s+received a drop:?\s*(?P<drop>.+)?$",
    re.IGNORECASE,
)

# Pet message formats:
#
# Name has a funny feeling like he's being followed: Pet Name at KC.
# Name has a funny feeling like she's being followed: Pet Name at KC.
# Name has a funny feeling like they're being followed: Pet Name at KC.
# Name has a funny feeling like he would have been followed: Pet Name at XP.
# Name has a funny feeling like she would have been followed: Pet Name at XP.
# Name has a funny feeling like they would have been followed: Pet Name at XP.
PET_PATTERN = re.compile(
    r"^(?P<player>.+?)\s+has a funny feeling like\s+"
    r"(?:(?:he's|she's|they're)\s+being followed|(?:he|she|they)\s+would have been followed):\s+"
    r"(?P<drop>.+?)\s+at\b",
    re.IGNORECASE,
)

# Raid drop format:
#
# [Rancour PvM] 🛡 Packn Fudge received special loot from a raid: Dinh's bulwark (16,726,799 coins).
#
# Grabs:
# player = Packn Fudge
# drop = Dinh's bulwark
RAID_DROP_PATTERN = re.compile(
    r"^(?:\[.*?\]\s*)?(?:\S+\s+)?(?P<player>.+?)\s+received special loot from a raid:\s+"
    r"(?P<drop>.+?)\s+\(",
    re.IGNORECASE,
)

# Collection log format:
#
# <:Collectionlog:1147701373455048814> PatrickRobby received a new collection log item: Beekeeper's legs (135/1537)
#
# Grabs:
# player = PatrickRobby
# drop = Beekeeper's legs
COLLECTION_LOG_PATTERN = re.compile(
    r"^(?:<a?:[^:]+:\d+>\s*)?(?P<player>.+?)\s+received a new collection log item:\s+"
    r"(?P<drop>.+?)\s+\(",
    re.IGNORECASE,
)

# Test format:
#
# SpaceScape: Test
# SpaceScape Test
# <:Deputy_owner:1144313595925110857> **SpaceScape** Test
#
# Grabs:
# player = SpaceScape
# drop = Test
TEST_PATTERN = re.compile(
    r"^(?P<player>.+?)(?::)?\s+test\b",
    re.IGNORECASE,
)


# ============================================================
# GOOGLE SHEETS
# ============================================================

def build_credentials_dict() -> dict:
    private_key = os.getenv("EVENT_PRIVATE_KEY")

    if not private_key:
        raise RuntimeError("Missing Railway environment variable: EVENT_PRIVATE_KEY")

    return {
        "type": os.getenv("EVENT_TYPE"),
        "project_id": os.getenv("EVENT_PROJECT_ID"),
        "private_key_id": os.getenv("EVENT_PRIVATE_KEY_ID"),
        "private_key": private_key.replace("\\n", "\n"),
        "client_email": os.getenv("EVENT_CLIENT_EMAIL"),
        "client_id": os.getenv("EVENT_CLIENT_ID"),
        "auth_uri": os.getenv("EVENT_AUTH_URI"),
        "token_uri": os.getenv("EVENT_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("EVENT_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("EVENT_CLIENT_X509_CERT_URL"),
        "universe_domain": os.getenv("EVENT_UNIVERSE_DOMAIN", "googleapis.com"),
    }


def get_sheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = Credentials.from_service_account_info(
        build_credentials_dict(),
        scopes=scope,
    )

    client = gspread.authorize(creds)
    return client.open_by_key(DROP_LOG_SHEET_ID).worksheet(DROP_LOG_TAB_NAME)


# ============================================================
# COG
# ============================================================

class ChannelLogger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sheet = get_sheet()
        print("✅ ChannelLogger cog initialized.")

    def get_matches(self, content: str) -> list[str]:
        content = clean_clan_message(content)
        matches = []

        if PET_PATTERN.search(content):
            matches.append("Pet")

        if RAID_DROP_PATTERN.search(content):
            matches.append("Raid Drop")

        if COLLECTION_LOG_PATTERN.search(content):
            matches.append("Collection Log Item")

        if NORMAL_DROP_PATTERN.search(content):
            matches.append("Drop")

        if TEST_PATTERN.search(content):
            matches.append("Test")

        return matches

    def parse_logged_message(
        self,
        message: discord.Message,
        matches: list[str],
    ) -> tuple[str, str]:
        """
        Returns:
        submitted_for, drop_received

        Auto-logged sheet behavior:
        - Approved by = Auto Logger
        - Submitted for = parsed player name
        - Submitted for Discord ID = blank
        - Drop Received = parsed drop/item/test
        - Screenshot = blank
        - Date/Time = timestamp
        """

        content = clean_clan_message(message.content.strip())

        pet_match = PET_PATTERN.search(content)
        if pet_match:
            submitted_for = clean_player_name(pet_match.group("player"))
            drop_received = clean_drop_name(pet_match.group("drop"))
            return submitted_for, drop_received

        raid_match = RAID_DROP_PATTERN.search(content)
        if raid_match:
            submitted_for = clean_player_name(raid_match.group("player"))
            drop_received = clean_drop_name(raid_match.group("drop"))
            return submitted_for, drop_received

        collection_match = COLLECTION_LOG_PATTERN.search(content)
        if collection_match:
            submitted_for = clean_player_name(collection_match.group("player"))
            drop_received = clean_drop_name(collection_match.group("drop"))
            return submitted_for, drop_received

        normal_drop_match = NORMAL_DROP_PATTERN.search(content)
        if normal_drop_match:
            submitted_for = clean_player_name(normal_drop_match.group("player"))
            drop_received = normal_drop_match.group("drop")

            if drop_received:
                drop_received = clean_drop_name(drop_received)
            else:
                drop_received = "Drop"

            return submitted_for, drop_received

        test_match = TEST_PATTERN.search(content)
        if test_match:
            submitted_for = clean_player_name(test_match.group("player"))
            drop_received = "Test"
            return submitted_for, drop_received

        return message.author.display_name, content

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # IMPORTANT:
        # Clan Chat appears to be a Discord bot/app.
        # Do NOT ignore all bot messages, or Clan Chat logs will never be recorded.
        #
        # This only ignores your own bot so it does not accidentally log itself.
        if message.author.id == self.bot.user.id:
            return

        # Only watch the configured channel.
        # This check is before any logging/printing so other channels do not spam Railway.
        if message.channel.id != WATCH_CHANNEL_ID:
            return

        matches = self.get_matches(message.content)

        if not matches:
            return

        timestamp = datetime.now(CST).strftime("%m/%d/%Y %I:%M %p")

        submitted_for, drop_received = self.parse_logged_message(message, matches)

        row = [
            "Auto Logger",      # Approved by
            submitted_for,      # Submitted for
            "",                 # Submitted for Discord ID
            drop_received,      # Drop Received
            message.jump_url,   # Screenshot / Message Link
            timestamp,          # Date/Time
        ]

        try:
            # Write directly into A:F instead of relying on append_row behavior.
            # Header is row 1, so first log row should be row 2.
            next_row = len(self.sheet.col_values(1)) + 1

            if next_row < 2:
                next_row = 2

            self.sheet.update(
                range_name=f"A{next_row}:F{next_row}",
                values=[row],
                value_input_option="USER_ENTERED",
            )

            print(
                f"✅ Auto-logged {drop_received} for {submitted_for} "
                f"with match type(s): {', '.join(matches)} "
                f"to row {next_row}"
            )

        except Exception as e:
            print(f"❌ ChannelLogger failed to log message: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(ChannelLogger(bot))
