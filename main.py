import os
import requests
import discord
from flask import Flask
from threading import Thread

# سيرفر الويب لمنع توقف Render
app = Flask('')
@app.route('/')
def home(): return "Steve Hybrid is Live!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def keep_alive():
    Thread(target=run).start()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ {client.user} انطلق بنظام الهجين!')

@client.event
async def on_message(message):
    # رد واحد فقط: تجاهل رسائل البوتات (بما في ذلك نفسه)
    if message.author.bot: return

    # الكلمات المفتاحية الصعبة لاستدعاء Qwen (للدراسة والعلوم)
    hard_keys = ["حل", "اشرح", "علل", "ما هي", "كيف", "لماذا", "عرف", "فيزياء", "كيمياء", "أحياء"]
    use_qwen = any(word in message.content for word in hard_keys)

    # اختيار الموديل
    model = "qwen/qwen-2.5-72b-instruct:free" if use_qwen else "meta-llama/llama-3.3-70b-instruct:free"
    tag = "🧠" if use_qwen else "⚡"

    async with message.channel.typing():
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": message.content}]
                }
            )
            res = response.json()
            answer = res['choices'][0]['message']['content']
            await message.channel.send(f"{tag} {answer}"[:2000])
        except:
            await message.channel.send("⚠️ تأكد من صحة مفتاح API في إعدادات Render.")

if __name__ == "__main__":
    keep_alive()
    client.run(os.getenv('DISCORD_TOKEN'))
    
