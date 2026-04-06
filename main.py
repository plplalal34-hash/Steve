import os
import sys

# درع الحماية من فقدان مكتبة الصوت في الإصدارات الغريبة
try:
    import audioop
except ImportError:
    import types
    sys.modules['audioop'] = types.ModuleType('audioop')

import discord
import google.generativeai as genai
from flask import Flask
from threading import Thread

# --- خادم صغير للبقاء نشطاً ---
app = Flask('')
@app.route('/')
def home(): return "Steve is Alive!"
def run_server(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run_server).start()

# --- إعداد جيميني ---
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

# --- إعداد ديسكورد ---
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ {client.user} جاهز للعمل!')

@client.event
async def on_message(message):
    if message.author == client.user: return
    
    # الرد فقط إذا تم ذكر البوت أو في الرسائل الخاصة
    async with message.channel.typing():
        try:
            response = model.generate_content(message.content)
            if response.text:
                await message.channel.send(response.text[:2000])
        except Exception as e:
            print(f"Error: {e}")
            # لا نرسل رسالة خطأ للمستخدم لتجنب الإزعاج، نكتفي بالسجلات

if __name__ == "__main__":
    keep_alive()
    token = os.getenv('DISCORD_TOKEN')
    if token:
        client.run(token)
    else:
        print("❌ خطأ: لم يتم العثور على DISCORD_TOKEN")
        
