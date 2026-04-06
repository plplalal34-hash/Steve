import sys
import types

# تجاوز مشكلة مكتبة الصوت
if 'audioop' not in sys.modules:
    sys.modules['audioop'] = types.ModuleType('audioop')

import discord
import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- Keep Alive ---
app = Flask('')
@app.route('/')
def home(): return "Steve is Ready!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- Config ---
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# إعدادات الأمان (تعطيل الحظر التلقائي)
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    safety_settings=safety_settings
)

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
            # محاولة توليد المحتوى
            response = model.generate_content(message.content)
            
            # التحقق من وجود نص في الرد
            if response.candidates and response.candidates[0].content.parts:
                await message.channel.send(response.text[:2000])
            else:
                await message.channel.send("⚠️ جوجل حظر الرد لأسباب تتعلق بالسياسة، حاول صياغة السؤال بشكل مختلف.")

        except Exception as e:
            error_str = str(e)
            print(f"Error Log: {error_str}")
            
            if "429" in error_str:
                await message.channel.send("⏳ ضغط كبير على الرسائل، سأرتاح قليلاً.")
            elif "API_KEY_INVALID" in error_str:
                await message.channel.send("🔑 مفتاح الـ API غير صالح، تأكد منه في Render.")
            else:
                await message.channel.send(f"⚠️ خطأ تقني: {error_str[:100]}")

if __name__ == "__main__":
    keep_alive()
    client.run(os.getenv('DISCORD_TOKEN'))
    
