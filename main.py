import os
import sys
import types

# خدعة برمجية لإيقاف مطالبات مكتبة الصوت نهائياً
sys.modules['audioop'] = types.ModuleType('audioop')

import discord
import google.generativeai as genai
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

# --- خادم صغير للبقاء نشطاً ---
app = Flask('')
@app.route('/')
def home(): return "Steve is Alive!"

def run_server():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_server)
    t.start()

# --- إعدادات Gemini 1.5 Flash ---
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

# --- إعدادات Discord ---
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ {client.user} متصل وجاهز!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    async with message.channel.typing():
        try:
            # محاولة توليد الرد
            response = model.generate_content(message.content)
            if response and response.text:
                await message.channel.send(response.text[:2000])
            else:
                await message.channel.send("⚠️ لم أتمكن من صياغة رد، جرب سؤالاً آخر.")
        except Exception as e:
            print(f"Error: {e}")
            await message.channel.send("⚙️ عذراً، واجهت مشكلة تقنية بسيطة.")

if __name__ == "__main__":
    keep_alive()
    client.run(os.getenv('DISCORD_TOKEN'))
