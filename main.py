import os
import sys
import types

# حل مشكلة مكتبة الصوت audioop في بايثون 3.13+
if 'audioop' not in sys.modules:
    sys.modules['audioop'] = types.ModuleType('audioop')

import discord
from groq import Groq
from openai import OpenAI
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

# --- إعداد سيرفر Flask للبقاء نشطاً ---
app = Flask('')
@app.route('/')
def home(): return "Steve Hybrid is Live!"

def run():
    # Render يحدد المنفذ تلقائياً عبر متغير PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

load_dotenv()

# --- إعداد محركات الذكاء الاصطناعي ---
# Llama 3 عبر Groq (للسرعة)
client_llama = Groq(api_key=os.getenv("GROQ_API_KEY"))
# DeepSeek عبر الموقع الرسمي (للمسائل العلمية)
client_deepseek = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"), 
    base_url="https://api.deepseek.com"
)

# --- إعداد Discord ---
intents = discord.Intents.default()
intents.message_content = True
client_discord = discord.Client(intents=intents)

@client_discord.event
async def on_ready():
    print(f'✅ تم تسجيل الدخول باسم: {client_discord.user}')

@client_discord.event
async def on_message(message):
    if message.author == client_discord.user: return

    # نظام التبديل الذكي: كلمات مفتاحية تجعل البوت يستخدم DeepSeek
    scientific_keywords = ["حل", "اشرح", "مسألة", "لماذا", "كيف", "برمج"]
    is_scientific = any(word in message.content for word in scientific_keywords)

    async with message.channel.typing():
        try:
            if is_scientific:
                # استخدام DeepSeek
                response = client_deepseek.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": message.content}]
                )
                answer = "🧠 **[DeepSeek]:** " + response.choices[0].message.content
            else:
                # استخدام Llama 3
                response = client_llama.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": message.content}]
                )
                answer = "⚡ **[Llama 3]:** " + response.choices[0].message.content

            # إرسال الرد (بحد أقصى 2000 حرف لديسكورد)
            await message.channel.send(answer[:2000])

        except Exception as e:
            print(f"Error: {e}")
            await message.channel.send(f"⚠️ واجهت مشكلة تقنية: `{str(e)[:50]}`")

if __name__ == "__main__":
    keep_alive()
    client_discord.run(os.getenv('DISCORD_TOKEN'))
