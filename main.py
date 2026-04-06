import os
import requests
import discord
from flask import Flask
from threading import Thread

# --- سيرفر البقاء ---
app = Flask('')
@app.route('/')
def home(): return "Steve is Live!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# --- إعداد ديسكورد ---
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ ستيف جاهز! المتصل: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user: return

    async with message.channel.typing():
        try:
            # استخدام OpenRouter مع الموديل المجاني Qwen 2.5
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                },
                json={
                    "model": "qwen/qwen-2.5-7b-instruct:free", # الموديل المجاني اللي فتحته في الصورة
                    "messages": [{"role": "user", "content": message.content}]
                }
            )
            
            res_json = response.json()
            
            # فحص إذا كان المفتاح شغال أو فيه خطأ
            if 'choices' in res_json:
                answer = res_json['choices'][0]['message']['content']
                await message.channel.send(answer[:2000])
            else:
                # هذا السطر سيخبرك بالضبط ما هي المشكلة في السجلات
                print(f"API Error: {res_json}")
                await message.channel.send(f"⚠️ خطأ في المفتاح: `{res_json.get('error', {}).get('message', 'Unknown Error')}`")

        except Exception as e:
            await message.channel.send("⚙️ واجهت مشكلة في الاتصال.")

if __name__ == "__main__":
    keep_alive()
    client.run(os.getenv('DISCORD_TOKEN'))
    
