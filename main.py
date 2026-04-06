import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OWNER_IDS_RAW = os.getenv("OWNER_IDS", "")

OWNER_IDS = {
    int(x.strip())
    for x in OWNER_IDS_RAW.split(",")
    if x.strip().isdigit()
}

if not DISCORD_BOT_TOKEN:
    raise RuntimeError("DISCORD_BOT_TOKEN is missing")
if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY is missing")

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


def strip_bot_mention(content: str, bot_user_id: int) -> str:
    return (
        content.replace(f"<@{bot_user_id}>", "")
        .replace(f"<@!{bot_user_id}>", "")
        .strip()
    )


async def is_reply_to_bot(message: discord.Message) -> bool:
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


async def should_respond(message: discord.Message) -> bool:
    if message.author.bot:
        return False

    if isinstance(message.channel, discord.DMChannel):
        return True

    if bot.user and bot.user.mentioned_in(message):
        return True

    if await is_reply_to_bot(message):
        return True

    return False


async def ask_ai(user_text: str) -> str:
    def _sync_call():
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "أنت بوت ديسكورد عربي. "
                        "لا تتدخل في أحاديث الناس العادية. "
                        "أجب فقط عندما يكون الكلام موجهاً إليك أو ردًا عليك. "
                        "كن مختصرًا ومفيدًا."
                    ),
                },
                {"role": "user", "content": user_text},
            ],
            temperature=0.4,
        )
        return resp.choices[0].message.content or ""

    return await asyncio.to_thread(_sync_call)


@bot.command()
async def purge(ctx, amount: int = 5):
    if ctx.author.id not in OWNER_IDS:
        return
    amount = max(1, min(amount, 100))
    await ctx.channel.purge(limit=amount + 1)


@bot.command()
async def lock(ctx):
    if ctx.author.id not in OWNER_IDS:
        return
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)


@bot.command()
async def unlock(ctx):
    if ctx.author.id not in OWNER_IDS:
        return
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = None
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    if message.content.lstrip().startswith("!"):
        return

    if not await should_respond(message):
        return

    user_text = message.content.strip()
    if bot.user:
        user_text = strip_bot_mention(user_text, bot.user.id)

    async with message.channel.typing():
        try:
            reply = await ask_ai(user_text)
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
