import os
import re
import time
import asyncio
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Optional

import discord
from discord.ext import commands

import gspread
from google.oauth2.service_account import Credentials


# ============================================================
# CONFIG
# ============================================================

DROP_LOG_SHEET_ID = "1VjoOx_GdzD0dNP-SnbMDjhKV8M054QQ9JgRbLQeSe-M"
DROP_LOG_TAB_NAME = "Drop Tab"

# Channel the bot watches for drop/pet/clog messages.
WATCH_CHANNEL_ID = 1272875477555482666

# Same review/log channels used by bingo_cog.py.
REVIEW_CHANNEL_ID = 1504315926017867847
LOG_CHANNEL_ID = 1504315879431864372

REQUIRED_ROLE_NAME = "Event Staff"

# Keep this False so ignored non-signup drops do not spam Railway logs.
VERBOSE_IGNORED = False

CST = ZoneInfo("America/Chicago")


# ============================================================
# MESSAGE CLEANUP
# ============================================================

def clean_clan_message(content: str) -> str:
    return (
        str(content or "")
        .replace("\\:", ":")
        .replace("\\(", "(")
        .replace("\\)", ")")
        .replace("\\'", "'")
        .replace('\\"', '"')
        .replace("\\-", "-")
        .replace("\\.", ".")
    )


def clean_player_name(name: str) -> str:
    name = str(name or "").strip()

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
    drop = str(drop or "").strip()
    drop = clean_clan_message(drop)

    # Remove anything from the first parenthesis onward.
    # Example: Imbued heart (101,719,907 coins). -> Imbued heart
    drop = re.sub(r"\s*\(.*$", "", drop).strip()

    # Remove leftover trailing punctuation.
    drop = drop.rstrip(".").strip()

    return drop


def normalize_rsn_name(name: str) -> str:
    """
    Normalizes RSNs for matching parsed Clan Chat names against
    the bingo signup sheet column C.
    """

    name = clean_clan_message(str(name or ""))
    name = clean_player_name(name)
    name = re.sub(r"\s+", " ", name).strip()
    return name.casefold()


# ============================================================
# REGEX PATTERNS
# ============================================================

NORMAL_DROP_PATTERN = re.compile(
    r"^(?:<a?:[^:]+:\d+>\s*)?(?P<player>.+?)\s+received a drop:?\s*(?P<drop>.+)?$",
    re.IGNORECASE,
)

PET_PATTERN = re.compile(
    r"^(?P<player>.+?)\s+has a funny feeling like\s+"
    r"(?:(?:he's|she's|they're)\s+being followed|(?:he|she|they)\s+would have been followed):\s+"
    r"(?P<drop>.+?)\s+at\b",
    re.IGNORECASE,
)

RAID_DROP_PATTERN = re.compile(
    r"^(?:\[.*?\]\s*)?(?:<a?:[^:]+:\d+>\s*|[^\w\s]+\s*)?"
    r"(?P<player>.+?)\s+received special loot from a raid:\s+"
    r"(?P<drop>.+?)\s+\(",
    re.IGNORECASE,
)

COLLECTION_LOG_PATTERN = re.compile(
    r"^(?:<a?:[^:]+:\d+>\s*)?(?P<player>.+?)\s+received a new collection log item:\s+"
    r"(?P<drop>.+?)\s+\(",
    re.IGNORECASE,
)

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
# REVIEW BUTTONS FOR AUTO-LOGGED DROPS
# ============================================================

class AutoLogReviewButtons(discord.ui.View):
    def __init__(
        self,
        cog: "ChannelLogger",
        submitted_for: str,
        drop_received: str,
        source_message_url: str,
        match_types: list[str],
    ):
        super().__init__(timeout=None)
        self.cog = cog
        self.submitted_for = submitted_for
        self.drop_received = drop_received
        self.source_message_url = source_message_url
        self.match_types = match_types
        self.reviewer: Optional[int] = None

    def has_drop_manager_role(self, member: discord.Member) -> bool:
        return any(role.name == REQUIRED_ROLE_NAME for role in member.roles)

    def is_moderator(self, member: discord.Member) -> bool:
        return any(role.name == "Moderators" for role in member.roles)

    @discord.ui.button(label="Review", style=discord.ButtonStyle.blurple)
    async def review(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        if not self.has_drop_manager_role(user) and not self.is_moderator(user):
            await interaction.response.send_message("You do not have permission to review.", ephemeral=True)
            return

        if self.reviewer is None:
            self.reviewer = user.id

            for child in self.children:
                if child.label.startswith("Approve") or child.label.startswith("Reject"):
                    child.disabled = False

            reviewer_label = "Moderator" if self.is_moderator(user) else "Reviewer"

            await interaction.message.edit(
                content=f"Being reviewed by {reviewer_label}: {user.display_name}",
                view=self,
            )
            await interaction.response.defer()
            return

        if self.reviewer == user.id:
            self.reviewer = None

            for child in self.children:
                if child.label.startswith("Approve") or child.label.startswith("Reject"):
                    child.disabled = True

            await interaction.message.edit(
                content="No one is currently reviewing this.",
                view=self,
            )
            await interaction.response.defer()
            return

        await interaction.response.send_message(
            f"This is currently being reviewed by <@{self.reviewer}>.",
            ephemeral=True,
        )

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green, disabled=True)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.reviewer != interaction.user.id:
            await interaction.response.send_message(
                "You are not the reviewer of this submission.",
                ephemeral=True,
            )
            return

        errors = []

        log_channel = self.cog.bot.get_channel(LOG_CHANNEL_ID)

        if log_channel:
            try:
                embed = discord.Embed(title="Drop Approved", colour=discord.Colour.green())
                embed.add_field(name="Approved By", value=interaction.user.display_name, inline=False)
                embed.add_field(name="Drop For", value=self.submitted_for, inline=False)
                embed.add_field(name="Drop", value=self.drop_received, inline=False)
                embed.add_field(name="Submitted By", value="Auto Logger", inline=False)
                embed.add_field(name="Source Message", value=self.source_message_url, inline=False)
                embed.add_field(name="Match Type", value=", ".join(self.match_types), inline=False)

                await log_channel.send(embed=embed)

            except Exception as e:
                print(f"ChannelLogger: Failed to send approval to log channel: {e}")
                errors.append("Failed to log to channel")
        else:
            errors.append("Log channel not found")

        try:
            self.cog.log_approved_autolog_drop_to_sheet(
                reviewer_name=interaction.user.display_name,
                submitted_for=self.submitted_for,
                drop_received=self.drop_received,
                source_message_url=self.source_message_url,
            )
        except Exception as e:
            print(f"ChannelLogger: Failed to write approved auto-log row: {e}")
            errors.append("Failed to log to spreadsheet")

        if errors:
            await interaction.response.send_message(
                f"Approved but with issues: {', '.join(errors)}. Message will be removed.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "Approved and logged. This message will now be removed.",
                ephemeral=True,
            )

        try:
            await asyncio.sleep(1)
            await interaction.message.delete()
        except Exception as e:
            print(f"ChannelLogger: Failed to delete review message: {e}")

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red, disabled=True)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.reviewer != interaction.user.id:
            await interaction.response.send_message(
                "You are not the reviewer of this submission.",
                ephemeral=True,
            )
            return

        await interaction.response.send_modal(AutoLogRejectReasonModal(self.cog, self, interaction))


class AutoLogRejectReasonModal(discord.ui.Modal, title="Reject Auto-Logged Submission"):
    def __init__(
        self,
        cog: "ChannelLogger",
        parent_view: AutoLogReviewButtons,
        interaction: discord.Interaction,
    ):
        super().__init__()
        self.cog = cog
        self.parent_view = parent_view
        self.message = interaction.message

        self.reason = discord.ui.TextInput(
            label="Reason for rejection",
            style=discord.TextStyle.paragraph,
            placeholder="Enter the reason why this drop is being rejected.",
            required=True,
            max_length=500,
        )
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        logged = False

        log_channel = self.cog.bot.get_channel(LOG_CHANNEL_ID)

        if log_channel:
            try:
                embed = discord.Embed(title="Drop Rejected", colour=discord.Colour.red())
                embed.add_field(name="Rejected By", value=interaction.user.display_name, inline=False)
                embed.add_field(name="Drop For", value=self.parent_view.submitted_for, inline=False)
                embed.add_field(name="Drop", value=self.parent_view.drop_received, inline=False)
                embed.add_field(name="Submitted By", value="Auto Logger", inline=False)
                embed.add_field(name="Source Message", value=self.parent_view.source_message_url, inline=False)
                embed.add_field(name="Match Type", value=", ".join(self.parent_view.match_types), inline=False)
                embed.add_field(name="Reason", value=self.reason.value, inline=False)

                await log_channel.send(embed=embed)
                logged = True

            except Exception as e:
                print(f"ChannelLogger: Failed to send rejection to log channel: {e}")

        if logged:
            await interaction.response.send_message(
                "Submission rejected and logged. This message will now be removed.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "Submission rejected but failed to log. This message will now be removed.",
                ephemeral=True,
            )

        try:
            await asyncio.sleep(1)
            await self.message.delete()
        except Exception as e:
            print(f"ChannelLogger: Failed to delete rejected review message: {e}")


# ============================================================
# COG
# ============================================================

class ChannelLogger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sheet = get_sheet()

        # Cache signup RSNs for 60 seconds so every clan-chat message does not
        # hammer Google Sheets.
        self._signup_rsn_cache: set[str] = set()
        self._signup_rsn_cache_time = 0.0

        print("✅ ChannelLogger cog initialized.")

    # --------------------------------------------------------
    # Signup validation
    # --------------------------------------------------------

    def get_bingo_signup_sheet(self):
        """
        Uses the already-loaded BingoCog signup sheet.

        bingo_cog.py stores signup RSNs in column C.
        """

        bingo_cog = self.bot.get_cog("BingoCog")

        if not bingo_cog:
            if VERBOSE_IGNORED:
                print("ChannelLogger: BingoCog is not loaded yet, so signup validation cannot run.")
            return None

        signup_sheet = getattr(bingo_cog, "signup_sheet", None)

        if signup_sheet is None:
            if VERBOSE_IGNORED:
                print("ChannelLogger: BingoCog signup_sheet is not available.")
            return None

        return signup_sheet

    def get_signed_up_rsns(self, force_refresh: bool = False) -> set[str]:
        """
        Reads column C from the Bingo signup spreadsheet and caches it briefly.
        Column C is RSN.
        """

        now = time.time()

        if (
            not force_refresh
            and self._signup_rsn_cache
            and now - self._signup_rsn_cache_time < 60
        ):
            return self._signup_rsn_cache

        signup_sheet = self.get_bingo_signup_sheet()

        if signup_sheet is None:
            return set()

        try:
            rsn_values = signup_sheet.col_values(3)  # Column C: RSN
        except Exception as e:
            print(f"ChannelLogger: Failed to read signup RSN column C: {e}")
            return set()

        normalized_rsns = {
            normalize_rsn_name(rsn)
            for rsn in rsn_values[1:]  # skip header row
            if normalize_rsn_name(rsn)
        }

        self._signup_rsn_cache = normalized_rsns
        self._signup_rsn_cache_time = now

        return normalized_rsns

    def player_is_signed_up(self, player_name: str) -> bool:
        wanted = normalize_rsn_name(player_name)

        if not wanted:
            return False

        signed_up_rsns = self.get_signed_up_rsns()
        return wanted in signed_up_rsns

    # --------------------------------------------------------
    # Drop-log sheet writing after review approval
    # --------------------------------------------------------

    def find_next_drop_log_row(self) -> int:
        start_row = 2
        end_row = 2000

        try:
            values = self.sheet.get(f"A{start_row}:F{end_row}")
        except Exception:
            values = []

        for offset in range(end_row - start_row + 1):
            row_values = values[offset] if offset < len(values) else []
            if not any(str(cell).strip() for cell in row_values[:6]):
                return start_row + offset

        raise RuntimeError(f"No open drop-log rows are available between rows {start_row} and {end_row}.")

    def log_approved_autolog_drop_to_sheet(
        self,
        reviewer_name: str,
        submitted_for: str,
        drop_received: str,
        source_message_url: str,
    ) -> int:
        row = self.find_next_drop_log_row()

        values = [[
            reviewer_name,       # Approved by
            submitted_for,       # Submitted for
            "",                  # Submitted for Discord ID
            drop_received,       # Drop Received
            source_message_url,  # Screenshot / message link
            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        ]]

        self.sheet.update(f"A{row}:F{row}", values)
        return row

    # --------------------------------------------------------
    # Parsing
    # --------------------------------------------------------

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

    def parse_logged_message(self, message: discord.Message, matches: list[str]) -> tuple[str, str]:
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

    # --------------------------------------------------------
    # Discord listener
    # --------------------------------------------------------

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Do not log this bot's own messages.
        if message.author.id == self.bot.user.id:
            return

        # Only watch live-clan-chat.
        if message.channel.id != WATCH_CHANNEL_ID:
            return

        matches = self.get_matches(message.content)

        if not matches:
            return

        submitted_for, drop_received = self.parse_logged_message(message, matches)

        # Only send for verification if the parsed player exists in the bingo
        # signup spreadsheet column C.
        if not self.player_is_signed_up(submitted_for):
            if VERBOSE_IGNORED:
                print(
                    f"ChannelLogger: Ignored {drop_received} for {submitted_for} "
                    f"because the RSN is not signed up in column C."
                )
            return

        review_channel = self.bot.get_channel(REVIEW_CHANNEL_ID)

        if not review_channel:
            print(f"❌ ChannelLogger could not find review channel {REVIEW_CHANNEL_ID}.")
            return

        embed = discord.Embed(
            title="Auto-Logged Drop Submission",
            colour=discord.Colour.blurple(),
        )
        embed.add_field(name="Submitted For", value=submitted_for, inline=False)
        embed.add_field(name="Drop Received", value=drop_received, inline=False)
        embed.add_field(name="Submitted By", value="Auto Logger", inline=False)
        embed.add_field(name="Source Message", value=message.jump_url, inline=False)
        embed.add_field(name="Match Type", value=", ".join(matches), inline=False)
        embed.set_footer(text=f"Detected from #{message.channel.name}")

        await review_channel.send(
            embed=embed,
            view=AutoLogReviewButtons(
                self,
                submitted_for,
                drop_received,
                message.jump_url,
                matches,
            ),
        )

        print(
            f"✅ Sent auto-logged submission to review: "
            f"{drop_received} for {submitted_for} "
            f"with match type(s): {', '.join(matches)}"
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(ChannelLogger(bot))
