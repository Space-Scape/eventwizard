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
# REGEX PATTERNS
# ============================================================

# Simple message checks.
LOG_PATTERNS = {
    r"received a new collection log item:": "Collection Log Item",
    r"received a drop": "Drop",
    r"\btest\b": "Test",
}

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
        matches = []

        if PET_PATTERN.search(content):
            matches.append("Pet")

        if RAID_DROP_PATTERN.search(content):
            matches.append("Raid Drop")

        for pattern, label in LOG_PATTERNS.items():
            if re.search(pattern, content, flags=re.IGNORECASE):
                matches.append(label)

        return matches

    def parse_logged_message(
        self,
        message: discord.Message,
        matches: list[str],
    ) -> tuple[str, str]:
        """
        Returns:
        submitted_for, drop_received

        For pet messages:
        - submitted_for = name before "has"
        - drop_received = text after ":" and before "at"

        For raid special loot messages:
        - submitted_for = name before "received special loot from a raid"
        - drop_received = text after ":" and before the coin value

        For other messages:
        - submitted_for = message author's display name
        - drop_received = full message text
        """

        content = message.content.strip()

        pet_match = PET_PATTERN.search(content)
        if pet_match:
            submitted_for = pet_match.group("player").strip()
            drop_received = pet_match.group("drop").strip()
            return submitted_for, drop_received

        raid_match = RAID_DROP_PATTERN.search(content)
        if raid_match:
            submitted_for = raid_match.group("player").strip()
            drop_received = raid_match.group("drop").strip()
            return submitted_for, drop_received

        return message.author.display_name, content

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Do not log this bot's own messages.
        if message.author.id == self.bot.user.id:
            return

        # Only watch the configured channel.
        if message.channel.id != WATCH_CHANNEL_ID:
            return

        matches = self.get_matches(message.content)

        if not matches:
            return

        timestamp = datetime.now(CST).strftime("%m/%d/%Y %I:%M %p")

        submitted_for, drop_received = self.parse_logged_message(message, matches)

        row = [
            "Auto Logger",   # Approved by
            submitted_for,   # Submitted for
            "",              # Submitted for Discord ID
            drop_received,   # Drop Received
            "",              # Screenshot
            timestamp,       # Date/Time
        ]

        try:
            self.sheet.append_row(row, value_input_option="USER_ENTERED")
            print(
                f"✅ Auto-logged {drop_received} for {submitted_for} "
                f"with match type(s): {', '.join(matches)}"
            )
        except Exception as e:
            print(f"❌ ChannelLogger failed to log message: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(ChannelLogger(bot))
