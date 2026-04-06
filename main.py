import discord
import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- الحفاظ على تشغيل السيرفر ---
app = Flask('')
@app.route('/')
def home(): return "Steve is Active!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- الإعدادات ---
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# إعداد المكتبة
genai.configure(api_key=GEMINI_API_KEY)

# استخدام موديل 1.5 Flash مع إعدادات السلامة الافتراضية
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash"
)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ متصل الآن باسم: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user: return

    async with message.channel.typing():
        try:
            # طريقة جلب الرد الأكثر استقراراً
            response = model.generate_content(message.content)
            
            # معالجة الرد والتأكد من عدم وجود حظر (Safety Filters)
            if response.parts:
                reply = response.text
                await message.channel.send(reply[:2000])
            else:
                await message.channel.send("⚠️ لم أتمكن من الرد، قد يكون المحتوى محظوراً من فلاتر الأمان.")

        except Exception as e:
            err = str(e)
            print(f"Error Log: {err}")
            
            if "429" in err:
                await message.channel.send("⏳ ضغط كبير، سأنتظر دقيقة للراحة.")
            elif "API_KEY_INVALID" in err or "403" in err:
                await message.channel.send("🔑 مشكلة في مفتاح الـ API، يرجى التأكد منه في إعدادات Render.")
            else:
                await message.channel.send("⚙️ واجهت عائقاً تقنياً، جرب إرسال الرسالة مرة أخرى.")

if __name__ == "__main__":
    keep_alive()
    if DISCORD_TOKEN:
        client.run(DISCORD_TOKEN)
