import os
import asyncio
import discord
from discord.ext import commands
from openai import OpenAI

# =========================
# ENV
# =========================
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OWNER_IDS_RAW = os.getenv("OWNER_IDS", "")  # comma-separated IDs, e.g. 123,456

OWNER_IDS = {
    int(x.strip())
    for x in OWNER_IDS_RAW.split(",")
    if x.strip().isdigit()
}

if not DISCORD_BOT_TOKEN:
    raise RuntimeError("DISCORD_BOT_TOKEN is missing")
if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY is missing")
if not OWNER_IDS:
    raise RuntimeError("OWNER_IDS is missing or empty")

# =========================
# One model only: auto free router
# =========================
MODEL = "openrouter/free"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "https://example.com",
        "X-OpenRouter-Title": "Discord Server Bot",
    },
)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


def owner_only():
    async def predicate(ctx: commands.Context) -> bool:
        return ctx.author.id in OWNER_IDS
    return commands.check(predicate)


def strip_bot_mention(content: str, bot_user_id: int) -> str:
    content = content.replace(f"<@{bot_user_id}>", "")
    content = content.replace(f"<@!{bot_user_id}>", "")
    return content.strip()


async def reply_to_bot(message: discord.Message) -> bool:
    if not bot.user or not message.reference:
        return False

    resolved = message.reference.resolved
    if isinstance(resolved, discord.Message):
        return resolved.author.id == bot.user.id

    if message.reference.message_id:
        try:
            ref_msg = await message.channel.fetch_message(message.reference.message_id)
            return ref_msg.author.id == bot.user.id
        except Exception:
            return False

    return False


async def should_ai_respond(message: discord.Message) -> bool:
    if message.author.bot:
        return False

    # Always respond in DM
    if isinstance(message.channel, discord.DMChannel):
        return True

    # Respond if bot is mentioned
    if bot.user and bot.user.mentioned_in(message):
        return True

    # Respond if the user is replying to the bot
    if await reply_to_bot(message):
        return True

    return False


async def call_openrouter(user_text: str, system_text: str) -> str:
    def _sync_call() -> str:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_text},
                {"role": "user", "content": user_text},
            ],
            temperature=0.4,
        )
        return resp.choices[0].message.content or ""

    return await asyncio.to_thread(_sync_call)


# =========================
# Admin commands (owner only)
# =========================

@bot.command(name="purge")
@owner_only()
@commands.guild_only()
async def purge(ctx: commands.Context, amount: int = 10):
    amount = max(1, min(amount, 100))
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"تم حذف {max(0, len(deleted) - 1)} رسالة.", delete_after=5)


@bot.command(name="slowmode")
@owner_only()
@commands.guild_only()
async def slowmode(ctx: commands.Context, seconds: int = 0):
    seconds = max(0, min(seconds, 21600))
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"تم ضبط السلو مود إلى {seconds} ثانية.", delete_after=5)


@bot.command(name="lock")
@owner_only()
@commands.guild_only()
async def lock(ctx: commands.Context):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("تم قفل القناة.", delete_after=5)


@bot.command(name="unlock")
@owner_only()
@commands.guild_only()
async def unlock(ctx: commands.Context):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = None
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("تم فتح القناة.", delete_after=5)


@bot.command(name="ban")
@owner_only()
@commands.guild_only()
async def ban(ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided"):
    await member.ban(reason=reason)
    await ctx.send(f"تم حظر {member.mention}.", delete_after=5)


@bot.command(name="kick")
@owner_only()
@commands.guild_only()
async def kick(ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided"):
    await member.kick(reason=reason)
    await ctx.send(f"تم طرد {member.mention}.", delete_after=5)


# =========================
# AI chat
# =========================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    # Let commands work first
    await bot.process_commands(message)

    # Ignore command messages here; they are handled above
    if message.content.lstrip().startswith("!"):
        return

    # Only respond when directly addressed
    if not await should_ai_respond(message):
        return

    user_text = message.content.strip()
    if bot.user:
        user_text = strip_bot_mention(user_text, bot.user.id)

    system_text = (
        "أنت بوت ديسكورد عربي واحد فقط. "
        "لا تتدخل في أحاديث الناس العادية. "
        "أجب فقط عندما يكون الكلام موجهاً إليك أو ردًا عليك. "
        "كن مختصرًا ومفيدًا."
    )

    async with message.channel.typing():
        try:
            reply = await call_openrouter(user_text, system_text)
        except Exception as e:
            reply = f"❌ خطأ من المزود: `{e}`"

    if not reply:
        reply = "لم أتمكن من توليد رد مناسب."

    await message.reply(
        reply[:2000],
        mention_author=False,
        allowed_mentions=discord.AllowedMentions.none(),
    )


bot.run(DISCORD_BOT_TOKEN)
