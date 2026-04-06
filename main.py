import os
import asyncio
import discord
from discord.ext import commands
from openai import OpenAI

# =========================
# Environment Variables
# =========================
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OWNER_IDS_RAW = os.getenv("OWNER_IDS", "")  # comma-separated Discord user IDs

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
# Models
# =========================
# Free Llama for normal replies
CHAT_MODEL = "meta-llama/llama-3.3-70b-instruct:free"

# Free Qwen for admin commands
ADMIN_MODEL = "qwen/qwen3.6-plus:free"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "https://example.com",
        "X-OpenRouter-Title": "Discord Admin Bot",
    },
)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


def is_owner(user_id: int) -> bool:
    return user_id in OWNER_IDS


def is_admin_command(message: discord.Message) -> bool:
    if message.author.bot:
        return False
    if not is_owner(message.author.id):
        return False

    content = message.content.strip().lower()

    # أي رسالة تبدأ بـ ! من المالك تعتبر أمر إداري
    # مثال: !ban, !role, !purge, !announce ...
    return content.startswith("!")


def should_reply_as_chat(message: discord.Message) -> bool:
    if message.author.bot:
        return False

    # يرد في الخاص
    if isinstance(message.channel, discord.DMChannel):
        return True

    # يرد إذا تم منشن البوت
    if bot.user and bot.user in message.mentions:
        return True

    # يرد على أوامر المالك الإدارية
    if is_admin_command(message):
        return True

    return False


async def ask_openrouter(model: str, system_prompt: str, user_prompt: str) -> str:
    def _sync_call():
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
        )
        return resp.choices[0].message.content or ""

    return await asyncio.to_thread(_sync_call)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if not should_reply_as_chat(message):
        await bot.process_commands(message)
        return

    if is_admin_command(message):
        model = ADMIN_MODEL
        system_prompt = (
            "أنت مساعد إداري لبوت ديسكورد. "
            "هذه الأوامر تصدر من مالك السيرفر فقط. "
            "فهمها بدقة، وقدم ردًا مختصرًا وعمليًا."
        )
    else:
        model = CHAT_MODEL
        system_prompt = (
            "أنت مساعد دردشة عربي طبيعي داخل بوت ديسكورد. "
            "أجب بشكل واضح، مختصر، ومفيد."
        )

    user_prompt = message.content

    async with message.channel.typing():
        try:
            reply = await ask_openrouter(model, system_prompt, user_prompt)
        except Exception as e:
            reply = f"❌ خطأ من المزود: `{e}`"

    if bot.user:
        reply = reply.replace(f"<@{bot.user.id}>", "").strip()

    if not reply:
        reply = "لم أتمكن من توليد رد."

    await message.reply(reply[:2000], mention_author=False)
    await bot.process_commands(message)


bot.run(DISCORD_BOT_TOKEN)
