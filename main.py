import os
import requests
import discord
from flask import Flask
from threading import Thread

# --- سيرفر البقاء بنظام Render الجديد ---
app = Flask('')
@app.route('/')
def home(): return "Steve Hybrid is Live!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# --- إعدادات ديسكورد ---
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ ستيف الهجين انطلق باسم: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user: return

    # نظام تمييز الأسئلة الدراسية (للسادس العلمي)
    study_words = ["حل", "اشرح", "كيف", "لماذا", "ما هي", "عرف", "وضح"]
    is_study = any(word in message.content for word in study_words)
    
    # اختيار الموديلات المجانية من OpenRouter
    # Qwen 2.5 جبار في الأحياء والكيمياء والعربية
    # Llama 3.3 رائع في الدردشة والمزاح
    model = "qwen/qwen-2.5-72b-instruct:free" if is_study else "meta-llama/llama-3.3-70b-instruct:free"

    async with message.channel.typing():
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                    "HTTP-Referer": "https://render.com", # اختياري لـ OpenRouter
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "أنت ستيف، مساعد ذكي ومرح. تستخدم أسلوباً علمياً دقيقاً عند الشرح."},
                        {"role": "user", "content": message.content}
                    ]
                }
            )
            
            res_data = response.json()
            if 'choices' in res_data:
                answer = res_data['choices'][0]['message']['content']
                icon = "🧠" if is_study else "⚡"
                await message.channel.send(f"{icon} {answer[:1950]}")
            else:
                print(f"Error from API: {res_data}")
                await message.channel.send("⚠️ هناك مشكلة في معالجة الطلب، تأكد من رصيد OpenRouter المجاني.")

        except Exception as e:
            print(f"Error: {e}")
            await message.channel.send("⚙️ واجهت تداخلاً في الأفكار، حاول مجدداً!")

if __name__ == "__main__":
    keep_alive()
    client.run(os.getenv('DISCORD_TOKEN'))
