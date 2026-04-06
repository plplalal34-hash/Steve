import os
import requests
import discord
from flask import Flask
from threading import Thread

# --- حل مشكلة Render (Port Binding) ---
app = Flask('')
@app.route('/')
def home(): return "Steve Hybrid is Live!"

def run():
    # استخدام المنفذ الذي يحدده Render تلقائياً
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# --- إعدادات البوت ---
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ ستيف متصل الآن باسم: {client.user}')

@client.event
async def on_message(message):
    if message.author.bot: return

    # نظام الهجين: كلمات مفتاحية علمية لتحفيز Qwen
    # تشمل مواضيعك الدراسية كالأحياء والكيمياء
    science_keywords = ["حل", "اشرح", "علل", "ما وظيفة", "مكونات", "أحياء", "خلية", "كيمياء", "فيزياء"]
    use_qwen = any(word in message.content for word in science_keywords)

    model = "qwen/qwen-2.5-72b-instruct:free" if use_qwen else "meta-llama/llama-3.3-70b-instruct:free"
    emoji = "🧠" if use_qwen else "⚡"

    async with message.channel.typing():
        try:
            api_key = os.getenv("OPENROUTER_API_KEY")
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": message.content}]
                }
            )
            res_data = response.json()
            if 'choices' in res_data:
                answer = res_data['choices'][0]['message']['content']
                await message.channel.send(f"{emoji} {answer}"[:2000])
            else:
                # هذا سيعالج خطأ 401 (Invalid API Key) الظاهر في صورتك
                await message.channel.send("⚠️ مشكلة في مفتاح الـ API. تأكد من وضعه بشكل صحيح في Render.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    keep_alive() # تشغيل السيرفر لضمان بقاء البوت حياً على Render
    client.run(os.getenv('DISCORD_TOKEN'))
    
