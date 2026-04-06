import discord
import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- إعداد خادم البقاء حياً (Keep-Alive) ---
app = Flask('')
@app.route('/')
def home(): return "Steve is Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- الإعدادات والمفاتيح ---
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# إعداد المكتبة بأحدث إصدار
genai.configure(api_key=GEMINI_API_KEY)

# تعريف الموديل 1.5 Flash (الأكثر استقراراً حالياً)
model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ ستيف متصل الآن باسم: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user: return

    # تفعيل مؤشر الكتابة في ديسكورد
    async with message.channel.typing():
        try:
            # طلب الرد من جيميني
            response = model.generate_content(message.content)
            
            # التأكد من وجود نص في الرد (بسبب فلاتر الأمان)
            if response and response.text:
                await message.channel.send(response.text[:2000])
            else:
                await message.channel.send("⚠️ لم أتمكن من الرد على هذه الرسالة تحديداً.")

        except Exception as e:
            err_msg = str(e)
            print(f"Error: {err_msg}")
            
            if "429" in err_msg:
                await message.channel.send("⚠️ وصلت للحد الأقصى من الرسائل، سأنتظر دقيقة للراحة.")
            elif "API_KEY_INVALID" in err_msg:
                await message.channel.send("🔑 خطأ في مفتاح الـ API، تأكد منه في إعدادات Render.")
            else:
                await message.channel.send("⏳ واجهت عائقاً تقنياً، حاول مرة أخرى بعد قليل.")

if __name__ == "__main__":
    keep_alive()
    if DISCORD_TOKEN:
        client.run(DISCORD_TOKEN)
        
