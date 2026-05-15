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

# Change this if your tab name is different.
DROP_LOG_TAB_NAME = "Drop Tab"

# Put the channel ID you want the bot to watch here.
WATCH_CHANNEL_ID = 1272875477555482666

CST = ZoneInfo("America/Chicago")


LOG_PATTERNS = {
    r"received a new collection log item:": "Collection Log Item",
    r"received a drop": "Drop",
    r"has a funny feeling like (he's|she's|they're) being followed:": "Pet",
    r"\btest\b": "Test",
}


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

        for pattern, label in LOG_PATTERNS.items():
            if re.search(pattern, content, flags=re.IGNORECASE):
                matches.append(label)

        return matches

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore bots so the bot does not log itself or other bots.
        if message.author.bot:
            return

        # Only watch the configured channel.
        if message.channel.id != WATCH_CHANNEL_ID:
            return

        matches = self.get_matches(message.content)

        if not matches:
            return

        timestamp = datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S")

        attachment_urls = "\n".join(a.url for a in message.attachments)

        row = [
            timestamp,
            str(message.author),
            str(message.author.id),
            message.author.display_name,
            str(message.channel),
            str(message.channel.id),
            ", ".join(matches),
            message.content,
            attachment_urls,
            message.jump_url,
        ]

        try:
            self.sheet.append_row(row, value_input_option="USER_ENTERED")
            print(
                f"✅ Logged message from {message.author} "
                f"with match type(s): {', '.join(matches)}"
            )
        except Exception as e:
            print(f"❌ ChannelLogger failed to log message: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(ChannelLogger(bot))
