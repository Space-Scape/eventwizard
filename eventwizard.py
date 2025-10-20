import os
import discord
from discord.ext import commands, tasks
from discord import app_commands
import gspread
from google.oauth2.service_account import Credentials
import asyncio
import re
from discord.ui import Modal, TextInput, View, Button
from discord import ButtonStyle
from typing import Optional
from datetime import datetime, timedelta, timezone, time
from zoneinfo import ZoneInfo
from gspread.exceptions import CellNotFound
import collections

# ---------------------------
# 🔹 Google Sheets Setup
# ---------------------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials from environment variables
credentials_dict = {
    "type": os.getenv('EVENT_TYPE'),
    "project_id": os.getenv('EVENT_PROJECT_ID'),
    "private_key_id": os.getenv('EVENT_PRIVATE_KEY_ID'),
    "private_key": os.getenv('EVENT_PRIVATE_KEY').replace("\\n", "\n"),
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

# Drop Submission Sheet
sheet_id = "1VjoOx_GdzD0dNP-SnbMDjhKV8M054QQ9JgRbLQeSe-M"
sheet = sheet_client.open_by_key(sheet_id).sheet1

# RSN Tracker Sheet
rsn_sheet = sheet_client.open_by_key("1ZwJiuVMp-3p8UH0NCVYTV9_UVI26jl5kWu2nvdspl9k").worksheet("Tracker")

# Events Sheet
EVENTS_SHEET_ID = "1ycltDSLJeKTLAHzVeYZ6JKwIV5A7md8Lh7IetvVljEc"
events_sheet = sheet_client.open_by_key(EVENTS_SHEET_ID).worksheet("Event Inputs")


# ---------------------------
# 🔹 Discord Bot Setup
# ---------------------------
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ---------------------------
# 🔹 Global State for Schedule
# ---------------------------
current_schedule_message_id = None
last_known_sheet_data = None


# ---------------------------
# 🔹 Configuration
# ---------------------------
# Drop Submissions
SUBMISSION_CHANNEL_ID = 1401523115808526438
REVIEW_CHANNEL_ID = 1401510165764771950
LOG_CHANNEL_ID = 1401514384001601607
REQUIRED_ROLE_NAME = "Event Staff"
REGISTERED_ROLE_NAME = "Registered"

# Event Management
EVENT_SCHEDULE_CHANNEL_ID = 1272646577432825977
STAFF_ROLE_ID = 1272635396991221824
ADMINISTRATOR_ROLE_ID = 1272961765034164318

# Timezones
CST = ZoneInfo("America/Chicago")
TIMEZONE_DATA = {
    "PST": ("America/Los_Angeles", "🇺🇸"), "MST": ("America/Denver", "🇺🇸"),
    "CST": ("America/Chicago", "🇺🇸"), "EST": ("America/New_York", "🇺🇸"),
    "AST": ("America/Halifax", "🇨🇦"), "BRT": ("Brazil", "🇧🇷"),
    "ART": ("Argentina", "🇦🇷"), "GMT": ("Europe/London", "🇬🇧"),
    "CET": ("Europe/Paris", "🇫🇷"), "EET": ("Europe/Helsinki", "🇫🇮"),
    "AWST": ("Australia/Perth", "🇦🇺"), "ACST": ("Australia/Adelaide", "🇦🇺"),
    "AEST": ("Australia/Sydney", "🇦🇺"),
}
INTERNATIONAL_TIMEZONES = {"GMT", "CET", "EET", "BRT", "ART", "AWST", "ACST", "AEST"}

# ---------------------------
# 🔹 Boss-Drop Mapping
# ---------------------------
boss_drops = {
    "Abyssal Sire": ["Abyssal orphan", "Unsired", "Abyssal head", "Bludgeon spine", "Bludgeon claw", "Bludgeon axon", "Jar of miasma", "Abyssal dagger", "Abyssal whip"],
    "Alchemical Hydra": ["Ikkle hydra", "Hydra's claw", "Hydra tail", "Hydra leather", "Hydra's fang", "Hydra's eye", "Hydra's heart", "Jar of chemicals"],
    "Amoxliatl": ["Moxi"],
    "Araxxor": ["Noxious pommel", "Noxious point", "Noxious blade", "Araxyte fang", "Araxyte head", "Aranea boots", "Jar of venom", "Coagulated venom", "Nid"],
    "Barrows": ["Ahrim's hood", "Ahrim's robetop", "Ahrim's robeskirt", "Ahrim's staff", "Karil's coif", "Karil's leathertop", "Karil's leatherskirt", "Karil's crossbow", "Dharok's helm", "Dharok's platebody", "Dharok's platelegs", "Dharok's greataxe", "Guthan's helm", "Guthan's platebody", "Guthan's chainskirt", "Guthan's warspear", "Torag's helm", "Torag's platebody", "Torag's platelegs", "Torag's hammers", "Verac's helm", "Verac's brassard", "Verac's plateskirt", "Verac's flail"],
    "Callisto": ["Callisto cub", "Tyrannical ring", "Dragon pickaxe", "Claws of callisto", "Voidwaker hilt"],
    "Cerberus": ["Hellpuppy", "Eternal crystal", "Pegasian crystal", "Primordial crystal", "Jar of souls"],
    "Chambers of Xeric": ["Dexterous prayer scroll", "Arcane prayer scroll", "Twisted buckler", "Dragon hunter crossbow", "Dinh's bulwark", "Ancestral hat", "Ancestral robe top", "Ancestral robe bottom", "Dragon claws", "Elder maul", "Kodai insignia", "Twisted bow", "Olmlet", "Twisted ancestral colour kit", "Metamorphic dust"],
    "Commander Zilyana": ["Pet zilyana", "Armadyl crossbow", "Saradomin hilt", "Saradomin sword", "Godsword shard 1", "Godsword shard 2", "Godsword shard 3", "Saradomin's light"],
    "Corporeal Beast": ["Pet dark core", "Elysian sigil", "Spectral sigil", "Arcane sigil", "Jar of spirits", "Spirit shield", "Holy Elixir"],
    "Dagannoth Kings": ["Pet dagannoth supreme", "Pet dagannoth rex", "Pet dagannoth prime", "Archers ring", "Seers ring", "Berserker ring", "Warrior ring"],
    "Demonic Gorilla": ["Zenyte shard", "Ballista limbs", "Ballista spring", "Light frame", "Heavy frame", "Monkey tail"],
    "Doom of Mokhaiotl": ["Dom", "Avernic treads", "Eye of ayak (uncharged)", "Mokhaiotl cloth"],
    "Duke Sucellus": ["Baron", "Virtus mask", "Virtus robe top", "Virtus robe bottom", "Magus vestige", "Eye of the duke"],
    "General Graardor": ["Pet general graardor", "Bandos hilt", "Bandos chestplate", "Bandos tassets", "Bandos boots", "Godsword shard 1", "Godsword shard 2", "Godsword shard 3"],
    "Giant Mole": ["Baby mole"],
    "Grotesque Guardians": ["Noon/midnight", "Granite gloves", "Granite hammer", "Granite ring", "Black tourmaline core", "Jar of stone"],
    "Hueycoatl": ["Huberte", "Dragon hunter wand", "Hueycoatl hide", "Tome of earth (empty)"],
    "Kraken": ["Pet kraken", "Kraken tentacle", "Trident of the seas (full)", "Jar of dirt"],
    "Kree'arra": ["Pet kree'arra", "Armadyl helmet", "Armadyl chestplate", "Armadyl chainskirt", "Armadyl hilt", "Godsword shard 1", "Godsword shard 2", "Godsword shard 3"],
    "K'ril Tsutsaroth": ["Pet K'ril Tsutsaroth", "Zamorakian spear", "Staff of the dead", "Zamorak hilt", "Steam battlestaff", "Godsword shard 1", "Godsword shard 2", "Godsword shard 3"],
    "King black dragon": ["Prince black dragon"],
    "Nightmare": ["Little nightmare/Parasite", "Nightmare staff", "Inquisitor's great helm", "Inquisitor's hauberk", "Inquisitor's plateskirt", "Inquisitor's mace", "Eldritch orb", "Harmonised orb", "Volatile orb", "Jar of dreams"],
    "Nex": ["Nexling", "Ancient hilt", "Nihil horn", "Zaryte vambraces", "Torva full helm (damaged)", "Torva platebody (damaged)", "Torva platelegs (damaged)"],
    "Phantom Muspah": ["Muphin", "Venator shard", "Ancient icon", "Charged ice", "Frozen cache", "Ancient essence"],
    "Revenants": ["Thammaron's sceptre", "Viggora's chainmace", "Craw's bow", "Ancient relic", "Ancient effigy", "Ancient medallion", "Ancient statuette", "Ancient totem"],
    "Sarachnis": ["Sraracha", "Sarachnis cudgel", "Jar of eyes"],
    "Tempoross": ["Tome of water (empty)"],
    "The Leviathan": ["Lil'viathan", "Virtus mask", "Virtus robe top", "Virtus robe bottom", "Venator vestige", "Leviathan's lure"],
    "Thermonuclear smoke devil": ["Jar of smoke", "Pet smoke devil"],
    "The Whisperer": ["Wisp", "Virtus mask", "Virtus robe top", "Virtus robe bottom", "Bellator vestige", "Siren's staff"],
    "Theatre of Blood": ["Lil' zik", "Avernic defender hilt", "Ghrazi rapier", "Sanguinesti staff (uncharged)", "Justiciar faceguard", "Justiciar chestguard", "Justiciar legguards", "Scythe of vitur (uncharged)", "Holy ornament kit", "Sanguine ornament kit", "Sanguine dust"],
    "Tombs of Amascut": ["Tumeken's Guardian", "Masori mask", "Masori body", "Masori chaps", "Lightbearer", "Osmumten's fang", "Elidinis' ward", "Tumeken's shadow (uncharged)"],
    "Tormented Demons": ["Tormented synapse", "Burning claw"],
    "Vardorvis": ["Butch", "Virtus mask", "Virtus robe top", "Virtus robe bottom", "Ultor vestige", "Executioner's axe head"],
    "Venenatis": ["Venenatis spiderling", "Fangs of venenatis", "Dragon pickaxe", "Voidwaker gem", "Treasonous ring"],
    "Vet'ion": ["Vet'ion jr.", "Skull of vet'ion", "Dragon pickaxe", "Voidwaker blade", "Ring of the gods", "Skeleton champion scroll"],
    "Vorkath": ["Vorki", "Draconic visage", "Skeletal visage", "Jar of decay", "Dragonbone necklace"],
    "Wintertodt": ["Tome of fire (empty)"],
    "Yama": ["Yami", "Soulflame horn", "Oathplate helm", "Oathplate chest", "Oathplate legs", "Dossier"],
    "Zalcano": ["Smolcano", "Zalcano shard", "Crystal tool seed"],
    "Zulrah": ["Pet snakeling", "Tanzanite mutagen", "Magma mutagen", "Jar of swamp", "Tanzanite fang", "Magic fang", "Serpentine visage", "Uncut onyx"],
    "Misc items": ["Priff rabbit", "Wyvern visage", "Jar of darkness"]
}


# ---------------------------
# 🔹 Drop Submission System
# ---------------------------
@tree.command(name="submitdrop", description="Submit a boss drop for review")
@app_commands.describe(
    screenshot="Attach a screenshot of your drop",
    submitted_for="Optionally specify the user you're submitting this drop for"
)
async def submit_drop(interaction: discord.Interaction, screenshot: discord.Attachment, submitted_for: discord.Member = None):
    if interaction.channel.id != SUBMISSION_CHANNEL_ID:
        await interaction.response.send_message("❌ This command can only be used in the drop submission channel.", ephemeral=True)
        return

    target_user = submitted_for or interaction.user

    await interaction.response.send_message(
        content=f"Submitting drop for {target_user.display_name}. Select the boss you received the drop from:",
        view=BossView(interaction.user, target_user, screenshot),
        ephemeral=True
    )

class BossSelect(discord.ui.Select):
    def __init__(self, submitting_user, target_user, screenshot, page=0):
        self.submitting_user = submitting_user
        self.target_user = target_user
        self.screenshot = screenshot
        self.page = page

        bosses = list(boss_drops.keys())
        max_pages = (len(bosses) - 1) // 25
        page = max(0, min(page, max_pages))

        page_bosses = bosses[page * 25: (page + 1) * 25]
        options = [discord.SelectOption(label=boss) for boss in page_bosses]

        super().__init__(placeholder="Select a boss", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        boss = self.values[0]
        await interaction.response.edit_message(
            content=f"Selected boss: {boss}. Now select the drop you received.",
            view=DropView(self.submitting_user, self.target_user, self.screenshot, boss, page=self.page)
        )


class BossView(discord.ui.View):
    def __init__(self, submitting_user, target_user, screenshot, page=0):
        super().__init__()
        self.add_item(BossSelect(submitting_user, target_user, screenshot, page))
        if page > 0:
            self.add_item(PreviousPageButton(submitting_user, target_user, screenshot, page))
        max_pages = (len(boss_drops) - 1) // 25
        if page < max_pages:
            self.add_item(NextPageButton(submitting_user, target_user, screenshot, page))

class PreviousPageButton(discord.ui.Button):
    def __init__(self, submitting_user, target_user, screenshot, page):
        super().__init__(label="◀️ Previous Page", style=discord.ButtonStyle.secondary)
        self.submitting_user = submitting_user
        self.target_user = target_user
        self.screenshot = screenshot
        self.page = page

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=BossView(self.submitting_user, self.target_user, self.screenshot, self.page - 1))

class NextPageButton(discord.ui.Button):
    def __init__(self, submitting_user, target_user, screenshot, page):
        super().__init__(label="Next Page ▶️", style=discord.ButtonStyle.secondary)
        self.submitting_user = submitting_user
        self.target_user = target_user
        self.screenshot = screenshot
        self.page = page

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=BossView(self.submitting_user, self.target_user, self.screenshot, self.page + 1))

def get_team_role_mention(member: discord.Member) -> str:
    for role in member.roles:
        if role.name.startswith("Team "):
            return role.mention
    return "*No team*"

class DropSelect(discord.ui.Select):
    def __init__(self, submitting_user, target_user, screenshot, boss):
        self.submitting_user = submitting_user
        self.target_user = target_user
        self.screenshot = screenshot
        self.boss = boss
        options = [discord.SelectOption(label=drop) for drop in boss_drops[boss]]
        super().__init__(placeholder=f"Select a drop from {boss}", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        drop_name = self.values[0]
        review_channel = bot.get_channel(REVIEW_CHANNEL_ID)

        embed = discord.Embed(title=f"{self.boss} Drop Submission", colour=discord.Colour.blurple())
        embed.add_field(name="Submitted For", value=f"{self.target_user.mention} ({self.target_user.id})", inline=False)
        embed.add_field(name="Drop Received", value=drop_name, inline=False)
        embed.add_field(name="Submitted By", value=f"{self.submitting_user.mention} ({self.submitting_user.id})", inline=False)
        embed.set_image(url=self.screenshot.url)

        await interaction.response.edit_message(content="✅ Submitted for review.", embed=embed, view=None)

        if review_channel:
            team_mention = get_team_role_mention(self.target_user)
            await review_channel.send(
                embed=embed,
                view=DropReviewButtons(self.target_user, drop_name, self.screenshot.url, self.submitting_user, team_mention)
            )

class DropView(discord.ui.View):
    def __init__(self, submitting_user, target_user, screenshot, boss, page=0):
        super().__init__()
        self.submitting_user = submitting_user
        self.target_user = target_user
        self.screenshot = screenshot
        self.boss = boss
        self.page = page

        self.add_item(DropSelect(submitting_user, target_user, screenshot, boss))
        self.add_item(self.BackButton())

    class BackButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label="⬅️ Back", style=discord.ButtonStyle.secondary)

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.edit_message(
                content=f"Submitting drop for {self.view.target_user.display_name}. Select the boss you received the drop from:",
                view=BossView(
                    self.view.submitting_user,
                    self.view.target_user,
                    self.view.screenshot,
                    page=self.view.page
                )
            )

class DropReviewButtons(discord.ui.View):
    def __init__(self, submitted_user: discord.Member, drop: str, image_url: str, submitting_user: discord.Member, team_mention: str):
        super().__init__(timeout=None)
        self.submitted_user = submitted_user
        self.drop = drop
        self.image_url = image_url
        self.submitting_user = submitting_user
        self.team_mention = team_mention
        self.reviewer: Optional[int] = None

    def has_required_role(self, member: discord.Member) -> bool:
        return any(role.name == REQUIRED_ROLE_NAME for role in member.roles)

    def is_moderator(self, member: discord.Member) -> bool:
        return any(role.name == "Moderators" for role in member.roles)

    @discord.ui.button(label="Review", style=discord.ButtonStyle.blurple)
    async def review(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        if not self.has_required_role(user) and not self.is_moderator(user):
            await interaction.response.send_message("❌ You do not have permission to review.", ephemeral=True)
            return

        # Toggle review status
        if self.reviewer is None:
            self.reviewer = user.id
            for child in self.children:
                if isinstance(child, Button) and (child.label.startswith("Approve") or child.label.startswith("Reject")):
                    child.disabled = False
            await interaction.message.edit(content=f"👤 Being reviewed by: {user.display_name}", view=self)
            await interaction.response.defer()
        elif self.reviewer == user.id:
            self.reviewer = None
            for child in self.children:
                if isinstance(child, Button) and (child.label.startswith("Approve") or child.label.startswith("Reject")):
                    child.disabled = True
            await interaction.message.edit(content="*No one is currently reviewing this.*", view=self)
            await interaction.response.defer()
        else:
            await interaction.response.send_message(f"❌ This is currently being reviewed by <@{self.reviewer}>.", ephemeral=True)


    @discord.ui.button(label="Approve ✅", style=discord.ButtonStyle.green, disabled=True)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.reviewer != interaction.user.id:
            await interaction.response.send_message("❌ You are not the reviewer of this submission.", ephemeral=True)
            return

        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="Drop Approved", colour=discord.Colour.green())
            embed.add_field(name="Approved By", value=interaction.user.display_name, inline=False)
            embed.add_field(name="Drop For", value=self.submitted_user.mention, inline=False)
            embed.add_field(name="Team", value=self.team_mention, inline=False)
            embed.add_field(name="Drop", value=self.drop, inline=False)
            embed.add_field(name="Submitted By", value=self.submitting_user.mention, inline=False)
            embed.set_image(url=self.image_url)
            await log_channel.send(embed=embed)

        sheet.append_row([
            interaction.user.display_name,
            self.submitted_user.display_name,
            str(self.submitted_user.id),
            self.drop,
            self.image_url,
            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        ])

        await interaction.response.send_message("✅ Approved and logged. This message will now be removed.", ephemeral=True)
        await asyncio.sleep(1)
        await interaction.message.delete()

    @discord.ui.button(label="Reject ❌", style=discord.ButtonStyle.red, disabled=True)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.reviewer != interaction.user.id:
            await interaction.response.send_message("❌ You are not the reviewer of this submission.", ephemeral=True)
            return

        modal = RejectReasonModal(self, interaction)
        await interaction.response.send_modal(modal)

class RejectReasonModal(discord.ui.Modal, title="Reject Submission"):
    def __init__(self, parent_view: DropReviewButtons, interaction: discord.Interaction):
        super().__init__()
        self.parent_view = parent_view
        self.message = interaction.message

        self.reason = discord.ui.TextInput(
            label="Reason for rejection", style=discord.TextStyle.paragraph,
            placeholder="Enter the reason why this drop is being rejected.",
            required=True, max_length=500
        )
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="Drop Rejected", colour=discord.Colour.red())
            embed.add_field(name="Rejected By", value=interaction.user.display_name, inline=False)
            embed.add_field(name="Drop For", value=self.parent_view.submitted_user.mention, inline=False)
            embed.add_field(name="Team", value=self.parent_view.team_mention, inline=False)
            embed.add_field(name="Drop", value=self.parent_view.drop, inline=False)
            embed.add_field(name="Submitted By", value=self.parent_view.submitting_user.mention, inline=False)
            embed.add_field(name="Reason", value=self.reason.value, inline=False)
            embed.set_image(url=self.parent_view.image_url)
            await log_channel.send(embed=embed)

        await interaction.response.send_message("❌ Submission rejected and logged. This message will now be removed.", ephemeral=True)
        await asyncio.sleep(1)
        await self.message.delete()

# --------------------------------------------------
# 🔹 Event Management System
# --------------------------------------------------
async def delete_previous_events_post(channel: discord.TextChannel):
    """Deletes the previous @Events post and its linked messages."""
    try:
        async for msg in channel.history(limit=100):
            if msg.author == channel.guild.me and ("@Events" in msg.content or "Today's Event" in msg.content):
                await msg.delete()
    except Exception as e:
        print(f"Error deleting old @Events post: {e}")

def _fmt_no_leading_zero(hour_12: str) -> str:
    return hour_12.lstrip("0") if hour_12.startswith("0") else hour_12

async def find_manual_event_posts_for_times(channel: discord.TextChannel, times_cst: list[datetime]) -> list[discord.Message]:
    patterns = set()
    for dt in times_cst:
        dt_cst = dt.astimezone(CST)
        weekday_long = dt_cst.strftime("%A")
        month_long = dt_cst.strftime("%B")
        day_str = str(dt_cst.day) # Correctly get day as integer
        year = dt_cst.strftime("%Y")
        time_12 = _fmt_no_leading_zero(dt_cst.strftime("%I:%M %p"))
        fmt1 = f"{weekday_long}, {month_long} {day_str}, {year} {time_12}"
        fmt2 = f"{month_long} {day_str}, {year} {time_12}"
        patterns.update([fmt1, fmt2])

    matches = []
    async for msg in channel.history(limit=400):
        text = (msg.content or "").strip()
        if any(p in text for p in patterns):
            matches.append(msg)
    matches.sort(key=lambda m: m.created_at, reverse=False)
    return matches

async def post_todays_event_links(channel: discord.TextChannel):
    """Posts today's links with @Events mention and includes manual events from text posts."""
    if not channel:
        print("❌ post_todays_event_links: No channel provided.")
        return

    today = datetime.now(CST).date()
    guild_events = channel.guild.scheduled_events

    todays_discord_events = [event for event in guild_events if event.start_time.astimezone(CST).date() == today]

    events_role = discord.utils.get(channel.guild.roles, name="Events")
    role_mention = events_role.mention if events_role else "@Events"

    times_to_match = [e.start_time for e in todays_discord_events]
    if not times_to_match:
        for h in (0, 12, 15, 18, 20):
            times_to_match.append(datetime.combine(today, time(hour=h, minute=0, tzinfo=CST)))

    manual_posts = await find_manual_event_posts_for_times(channel, times_to_match)

    if not todays_discord_events and not manual_posts:
        await delete_previous_events_post(channel)
        print("ℹ️ No Discord calendar events or manual posts found for today.")
        return

    await delete_previous_events_post(channel)
    header = "Today's Event:" if (len(todays_discord_events) + len(manual_posts)) == 1 else "Today's Events:"
    
    await channel.send(
        f"""{role_mention}\n{header}""",
        allowed_mentions=discord.AllowedMentions(roles=True)
    )

    for event in sorted(todays_discord_events, key=lambda e: e.start_time):
        await channel.send(event.url)

    for msg in manual_posts:
        try:
            await channel.send(msg.jump_url)
        except Exception:
            snippet = (msg.content or "").splitlines()[0][:100]
            await channel.send(f"(manual) {snippet}…")

async def update_schedule_message(channel: discord.TextChannel, force_new=False):
    """Posts or edits the weekly schedule message."""
    global current_schedule_message_id
    if not channel: return

    embed = await generate_schedule_embed()
    
    if force_new and current_schedule_message_id:
        try:
            old_message = await channel.fetch_message(current_schedule_message_id)
            await old_message.delete()
        except discord.NotFound:
            pass 
        current_schedule_message_id = None

    if current_schedule_message_id:
        try:
            message = await channel.fetch_message(current_schedule_message_id)
            await message.edit(embed=embed)
            print("✅ Edited existing schedule message.")
        except discord.NotFound:
            current_schedule_message_id = None
    
    if not current_schedule_message_id:
        new_message = await channel.send(embed=embed)
        current_schedule_message_id = new_message.id
        print("✅ Posted new schedule message.")

def get_all_event_records():
    """Fetches all event records, adding a row number for identification."""
    try:
        all_values = events_sheet.get_all_values()
        if len(all_values) < 5: return []
        
        headers = all_values[3]
        data_rows = all_values[4:]
        
        records = []
        for i, row in enumerate(data_rows):
            record = {headers[j]: (row[j] if j < len(row) else "") for j in range(len(headers))}
            record['row_number'] = i + 5 # Sheet row numbers are 1-based, data starts on row 5
            
            if any(val for key, val in record.items() if key != 'row_number'):
                records.append(record)
        return records
    except Exception as e:
        print(f"Error fetching and parsing event sheet data: {e}")
        return []

class AddEventModal(Modal):
    def __init__(self, event_type_str: str, is_international: bool = False, existing_data: Optional[dict] = None):
        super().__init__(title="Create/Edit Event")
        self.is_international = is_international
        self.existing_data = existing_data

        date_format_str = "D/M/YYYY" if is_international else "M/D/YYYY"
        date_placeholder = f"e.g., {'29/9/2025' if is_international else '9/29/2025'}"
        
        default_type = existing_data.get("Type of Event", event_type_str) if existing_data else event_type_str
        default_desc = existing_data.get("Event Description", "") if existing_data else ""
        default_owner = existing_data.get("Event Owner", "") if existing_data else ""
        default_comments = existing_data.get("Comments", "") if existing_data else ""
        
        default_dates = ""
        if existing_data:
            start_str = existing_data.get("Start Date", "")
            end_str = existing_data.get("End Date", "")
            if start_str and not is_international:
                try: start_str = datetime.strptime(start_str, "%d/%m/%Y").strftime("%m/%d/%Y")
                except ValueError: pass
            if end_str and not is_international:
                try: end_str = datetime.strptime(end_str, "%d/%m/%Y").strftime("%m/%d/%Y")
                except ValueError: pass

            if start_str and end_str and start_str != end_str:
                default_dates = f"{start_str} - {end_str}"
            else:
                default_dates = start_str

        self.field1 = TextInput(label="Type of Event", default=default_type)
        self.field2 = TextInput(label="Event Description", placeholder="e.g., Learner ToB", default=default_desc)
        self.field3 = TextInput(label="Event Owner (Optional)", placeholder="Leave blank to default to you", default=default_owner, required=False)
        self.field4 = TextInput(label=f"Date(s) ({date_format_str})", placeholder=f"{date_placeholder} or {date_placeholder} - {date_placeholder}", default=default_dates)
        self.field5 = TextInput(label="Comments (Optional)", style=discord.TextStyle.paragraph, default=default_comments, required=False)

        for item in [self.field1, self.field2, self.field3, self.field4, self.field5]: self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        dates_str = self.field4.value
        start_date_str, end_date_str = (dates_str.split(' - ', 1) + [None])[:2] if ' - ' in dates_str else (dates_str, dates_str)
        start_date_str = start_date_str.strip()
        end_date_str = end_date_str.strip() if end_date_str else start_date_str

        expected_format = "%d/%m/%Y" if self.is_international else "%m/%d/%Y"
        try:
            start_date_obj = datetime.strptime(start_date_str, expected_format)
            end_date_obj = datetime.strptime(end_date_str, expected_format)
        except ValueError:
            await interaction.followup.send(f"❌ **Invalid Date.** Use **{expected_format.upper()}** format.", ephemeral=True)
            return

        start_date_for_sheet = start_date_obj.strftime("%m/%d/%Y")
        end_date_for_sheet = end_date_obj.strftime("%m/%d/%Y")

        event_owner = self.field3.value.strip()
        if not event_owner:
            try:
                cell = rsn_sheet.find(str(interaction.user.id))
                event_owner = rsn_sheet.cell(cell.row, 4).value if cell else re.sub(r'^\W+', '', interaction.user.display_name)
            except (CellNotFound, Exception):
                event_owner = re.sub(r'^\W+', '', interaction.user.display_name)

        event_data = [
            self.field1.value, self.field2.value, event_owner, "", "",
            start_date_for_sheet, end_date_for_sheet, "", "", "", self.field5.value or ""
        ]

        try:
            action_verb = "created"
            if self.existing_data:
                row_num = self.existing_data['row_number']
                events_sheet.update(range_name=f"B{row_num}:L{row_num}", values=[event_data], value_input_option='USER_ENTERED')
                action_verb = "edited"
            else:
                next_row = len(events_sheet.col_values(2)) + 1
                events_sheet.update(range_name=f"B{next_row}:L{next_row}", values=[event_data], value_input_option='USER_ENTERED')

            confirm_embed = discord.Embed(title=f"✅ Event {action_verb.capitalize()}!", color=discord.Color.green())
            confirm_embed.add_field(name="Description", value=self.field2.value, inline=False)
            await interaction.followup.send(embed=confirm_embed, ephemeral=True)
        except Exception as e:
            print(f"Error processing event: {e}")
            await interaction.followup.send(f"❌ An error occurred while saving the event: {e}", ephemeral=True)

@tree.command(name="addevent", description="Add a new event to the schedule.")
@app_commands.checks.has_role(REQUIRED_ROLE_NAME)
@app_commands.describe(event_type="The type of event.")
@app_commands.choices(event_type=[
    app_commands.Choice(name=t, value=t) for t in ["BOTW", "SOTW", "Pet Roulette", "Sanguine Sunday", "Mass Event", "Bounty", "Large Event", "Castle Wars", "Wildy Altar", "Discord games", "Hide and seek", "Other Event"]
])
async def addevent(interaction: discord.Interaction, event_type: str):
    user_roles = {r.name for r in interaction.user.roles}
    is_international = bool(user_roles.intersection(INTERNATIONAL_TIMEZONES))
    await interaction.response.send_modal(AddEventModal(event_type, is_international))

@tree.command(name="editevent", description="Edit an existing event by its ID (row number).")
@app_commands.checks.has_role(REQUIRED_ROLE_NAME)
@app_commands.describe(event_id="The ID (row number) of the event to edit.")
async def editevent(interaction: discord.Interaction, event_id: int):
    try:
        if event_id < 5: raise ValueError("Invalid ID")
        
        row_data = events_sheet.row_values(event_id)
        if not any(row_data): raise ValueError("No event found")

        headers = events_sheet.row_values(4)
        event_dict = {headers[i]: (row_data[i] if i < len(row_data) else "") for i in range(len(headers))}
        event_dict['row_number'] = event_id

        user_roles = {r.name for r in interaction.user.roles}
        is_international = bool(user_roles.intersection(INTERNATIONAL_TIMEZONES))
        
        await interaction.response.send_modal(AddEventModal("", is_international, existing_data=event_dict))
    except (IndexError, ValueError, gspread.exceptions.APIError):
        await interaction.response.send_message(f"❌ Could not find event with ID `{event_id}`. Please check the sheet.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

class DeleteConfirmationView(View):
    def __init__(self, event_id: int):
        super().__init__(timeout=60)
        self.event_id = event_id

    @discord.ui.button(label="Confirm Delete", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        try:
            events_sheet.delete_rows(self.event_id)
            await interaction.response.edit_message(content=f"✅ Event ID `{self.event_id}` has been deleted.", view=None)
        except Exception as e:
            await interaction.response.edit_message(content=f"❌ An error occurred during deletion: {e}", view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(content="Deletion canceled.", view=None)

@tree.command(name="deleteevent", description="Delete an event by its ID (row number).")
@app_commands.checks.has_role(REQUIRED_ROLE_NAME)
@app_commands.describe(event_id="The ID (row number) of the event to delete.")
async def deleteevent(interaction: discord.Interaction, event_id: int):
    try:
        if event_id < 5: raise ValueError("Invalid ID")
        row_data = events_sheet.row_values(event_id)
        if not any(row_data): raise ValueError("No event found")
        
        desc, owner, start_date = row_data[1], row_data[2], row_data[5]
        embed = discord.Embed(title="⚠️ Confirm Deletion", description="Are you sure you want to delete this event? This action cannot be undone.", color=discord.Color.red())
        embed.add_field(name="ID", value=f"`{event_id}`").add_field(name="Description", value=desc).add_field(name="Host", value=owner).add_field(name="Date", value=start_date)
        await interaction.response.send_message(embed=embed, view=DeleteConfirmationView(event_id), ephemeral=True)
    except (IndexError, ValueError, gspread.exceptions.APIError):
        await interaction.response.send_message(f"❌ Could not find an event with ID `{event_id}`.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An unexpected error occurred: {e}", ephemeral=True)

@tree.command(name="schedule", description="Manually posts/updates the weekly event schedule.")
@app_commands.checks.has_role(REQUIRED_ROLE_NAME)
async def schedule(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    channel = bot.get_channel(EVENT_SCHEDULE_CHANNEL_ID)
    if channel:
        await update_schedule_message(channel, force_new=True)
        await post_todays_event_links(channel)
        await interaction.followup.send(f"✅ Schedule has been posted in {channel.mention}!", ephemeral=True)
    else:
        await interaction.followup.send("⚠️ Event schedule channel not found.", ephemeral=True)

async def generate_schedule_embed():
    """Fetches event data and generates the weekly schedule embed."""
    try:
        all_events = get_all_event_records()
    except Exception as e:
        print(f"Could not fetch event records: {e}")
        return discord.Embed(title="Error", description="Could not fetch event data from the spreadsheet.", color=discord.Color.red())

    now, today = datetime.now(CST), datetime.now(CST).date()
    start_of_week = today - timedelta(days=today.weekday()) # Monday
    end_of_week = start_of_week + timedelta(days=6) # Sunday

    daily_events = {start_of_week + timedelta(days=i): [] for i in range(7)}
    week_long_events = []

    for event in all_events:
        try:
            start_date = datetime.strptime(event["Start Date"], "%m/%d/%Y").date()
            end_date = datetime.strptime(event["End Date"], "%m/%d/%Y").date() if event.get("End Date") else start_date
            
            # Check if event is week-long and overlaps with the current week
            if (end_date - start_date).days >= 6 and start_date <= end_of_week and end_date >= start_of_week:
                week_long_events.append(event)
            else:
                d = start_date
                while d <= end_date:
                    if start_of_week <= d <= end_of_week:
                        daily_events[d].append(event)
                    d += timedelta(days=1)
        except (ValueError, KeyError):
            continue
    
    embed = discord.Embed(title=f"📅 Weekly Clan Schedule ({start_of_week:%b %d} - {end_of_week:%b %d})", color=discord.Color.gold())

    if week_long_events:
        value = "\n".join([f"• ||{e['row_number']}|| **{e['Event Description']}**・Hosted by {e['Event Owner']}" for e in week_long_events])
        embed.add_field(name="# Week-Long Events", value=value, inline=False)

    for i in range(7):
        current_date = start_of_week + timedelta(days=i)
        day_name = current_date.strftime("%A")
        
        day_lines = []
        day_events_for_day = sorted(daily_events.get(current_date, []), key=lambda x: x['Event Description'])
        
        if day_events_for_day:
            grouped_events = collections.defaultdict(lambda: {'hosts': [], 'ids': []})
            for event in day_events_for_day:
                key = (event.get('Type of Event', ''), event.get('Event Description', 'No Description'))
                grouped_events[key]['hosts'].append(event.get('Event Owner', 'N/A'))
                grouped_events[key]['ids'].append(str(event.get('row_number', 'N/A')))

            for (e_type, desc), data in grouped_events.items():
                if len(data['hosts']) > 1:
                    hosts_str = ' & '.join(sorted(list(set(data['hosts']))))
                else:
                    hosts_str = data['hosts'][0] if data['hosts'] else 'N/A'

                ids_str = ", ".join(sorted(list(set(data['ids']))))
                
                line_base = f"**{e_type}**: {desc}" if e_type and e_type.lower() != desc.lower() else f"**{desc}**"
                line = f"• ||{ids_str}|| {line_base}・Hosted by {hosts_str}"
                day_lines.append(line)

        embed.add_field(name=day_name, value="\n".join(day_lines) if day_lines else "- No events planned.", inline=False)

    embed.set_footer(text=f"Last Updated: {now:%m/%d/%Y %I:%M %p CST}")
    return embed

# --------------------------------------------------
# 🔹 Scheduled Tasks
# --------------------------------------------------

@tasks.loop(minutes=5)
async def check_sheet_for_updates():
    """Periodically checks the sheet for changes and updates the schedule if needed."""
    global last_known_sheet_data
    try:
        channel = bot.get_channel(EVENT_SCHEDULE_CHANNEL_ID)
        if not channel or not current_schedule_message_id:
            return

        current_data = get_all_event_records()
        
        if current_data != last_known_sheet_data:
            print("📝 Sheet change detected, updating schedule...")
            await update_schedule_message(channel)
            last_known_sheet_data = current_data
            print("✅ Schedule updated.")

    except Exception as e:
        print(f"Error in check_sheet_for_updates: {e}")

@tasks.loop(time=time(hour=0, minute=0, tzinfo=CST))
async def daily_schedule_post():
    """Posts a fresh schedule embed every day at 12:00 AM CST."""
    channel = bot.get_channel(EVENT_SCHEDULE_CHANNEL_ID)
    if channel:
        await update_schedule_message(channel, force_new=True)

@tasks.loop(time=time(hour=0, minute=1, tzinfo=CST))
async def daily_event_link_post():
    """Posts links for the current day's events every day at 12:01 AM CST."""
    print("🌅 Posting today's event links...")
    channel = bot.get_channel(EVENT_SCHEDULE_CHANNEL_ID)
    if channel:
        await post_todays_event_links(channel)
        print("✅ Today's event links posted.")


@daily_schedule_post.before_loop
@check_sheet_for_updates.before_loop
async def before_daily_schedule_post():
    await bot.wait_until_ready()

@daily_event_link_post.before_loop
async def before_daily_event_link_post():
    await bot.wait_until_ready()

# --------------------------------------------------
# 🔹 Bot Startup
# --------------------------------------------------
@bot.event
async def on_ready():
    global last_known_sheet_data
    print(f"✅ Logged in as {bot.user}")
    
    # Start the defined tasks
    if not check_sheet_for_updates.is_running():
        check_sheet_for_updates.start()
    if not daily_schedule_post.is_running():
        daily_schedule_post.start()
    if not daily_event_link_post.is_running():
        daily_event_link_post.start()

    try:
        synced = await tree.sync()
        print(f"✅ Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Command sync failed: {e}")

    # Initial post/update on startup
    channel = bot.get_channel(EVENT_SCHEDULE_CHANNEL_ID)
    if channel:
        await update_schedule_message(channel)
        # Initialize the data for the update checker
        last_known_sheet_data = get_all_event_records()


# 🚀 Always last - run the bot
bot.run(os.getenv("BOT_TOKEN"))
