import sys
import types

# خدعة برمجية لتجاوز نقص مكتبة audioop في الإصدارات الحديثة
if 'audioop' not in sys.modules:
    sys.modules['audioop'] = types.ModuleType('audioop')

import discord
import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- تشغيل Flask لبقاء البوت نشطاً ---
app = Flask('')
@app.route('/')
def home(): return "Steve is Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- إعدادات الذكاء الاصطناعي ---
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
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
    async with message.channel.typing():
        try:
            response = model.generate_content(message.content)
            if response and response.text:
                await message.channel.send(response.text[:2000])
        except Exception as e:
            print(f"Error: {e}")
            await message.channel.send("⚠️ حدث خطأ تقني، جرب مرة أخرى.")

if __name__ == "__main__":
    keep_alive()
    client.run(os.getenv('DISCORD_TOKEN'))
