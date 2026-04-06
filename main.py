import os
import asyncio
import discord
from discord.ext import commands
from openai import OpenAI

# =========================
# الإعدادات
# =========================
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# ضع هنا Discord User ID الخاص بك (أو أكثر من ID)
OWNER_IDS = {
    int(x) for x in os.getenv("OWNER_IDS", "").split(",") if x.strip().isdigit()
}

# Llama للنقاش العام
CHAT_MODEL = os.getenv(
    "CHAT_MODEL",
    "meta-llama/llama-3.1-8b-instruct"
)

# Qwen للأوامر الإدارية
ADMIN_MODEL = os.getenv(
    "ADMIN_MODEL",
    "qwen/qwen3.6-plus:free"
)

# الراوتر التلقائي كـ fallback
AUTO_MODEL = os.getenv(
    "AUTO_MODEL",
    "openrouter/free"
)

# إذا جعلته 1 سيتم استخدام openrouter/free حتى في الرسائل العادية
# لكن هذا لن يضمن Llama أو Qwen بعينهما
USE_AUTO_ROUTER_FOR_ALL = os.getenv("USE_AUTO_ROUTER_FOR_ALL", "0") == "1"

if not DISCORD_BOT_TOKEN:
    raise RuntimeError("DISCORD_BOT_TOKEN is missing")
if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY is missing")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "https://example.com",
        "X-OpenRouter-Title": "Discord Bot",
    },
)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


def is_admin_message(message: discord.Message) -> bool:
    if message.author.bot:
        return False

    if message.author.id in OWNER_IDS:
        # اعتبر أي رسالة تبدأ بـ ! أو / أو admin كأمر إداري
        text = message.content.strip().lower()
        return text.startswith("!") or text.startswith("/") or text.startswith("admin")

    return False


def pick_model(message: discord.Message) -> str:
    if USE_AUTO_ROUTER_FOR_ALL:
        return AUTO_MODEL

    if is_admin_message(message):
        return ADMIN_MODEL

    return CHAT_MODEL


async def ask_openrouter(model: str, user_text: str, system_text: str) -> str:
    def _call_api():
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_text},
                {"role": "user", "content": user_text},
            ],
            temperature=0.4,
        )
        return response.choices[0].message.content or ""

    return await asyncio.to_thread(_call_api)


async def get_reply(message: discord.Message) -> str:
    model = pick_model(message)

    if is_admin_message(message):
        system_text = (
            "أنت مساعد إداري داخل بوت ديسكورد. "
            "رد على أوامر المالك فقط، وكن مختصرًا وواضحًا."
        )
    else:
        system_text = (
            "أنت مساعد دردشة طبيعي داخل بوت ديسكورد. "
            "تحدث بأسلوب عربي واضح ومباشر."
        )

    user_text = message.content

    # المحاولة الأولى: الموديل المخصص
    try:
        return await ask_openrouter(model, user_text, system_text)
    except Exception as e1:
        # fallback 1: الراوتر المجاني التلقائي
        try:
            return await ask_openrouter(AUTO_MODEL, user_text, system_text)
        except Exception as e2:
            return f"تعذر الاتصال بالنموذج المطلوب. الخطأ الأول: {e1}\nالخطأ الثاني: {e2}"


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    # تجاهل الرسائل التي لا تريد التعامل معها
    # مثال: استقبل فقط منشن للبوت أو رسائل خاصة
    should_respond = (
        bot.user in message.mentions
        or isinstance(message.channel, discord.DMChannel)
        or is_admin_message(message)
    )

    if not should_respond:
        await bot.process_commands(message)
        return

    async with message.channel.typing():
        reply = await get_reply(message)

    # احذف منشن البوت من الرد إذا وُجد
    if bot.user:
        reply = reply.replace(f"<@{bot.user.id}>", "").strip()

    if not reply:
        reply = "لم أستطع توليد رد مناسب."

    await message.reply(reply[:2000], mention_author=False)
    await bot.process_commands(message)


bot.run(DISCORD_BOT_TOKEN)
