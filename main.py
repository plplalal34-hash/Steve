import os
import requests
import discord
from flask import Flask
from threading import Thread

# --- سيرفر البقاء بنظام Render ---
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
    print(f'✅ ستيف متصل الآن باسم: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user: return

    # نظام ذكي بسيط للرد
    async with message.channel.typing():
        try:
            api_key = os.getenv("OPENROUTER_API_KEY")
            
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "qwen/qwen-2.5-7b-instruct:free", # الموديل المجاني
                    "messages": [{"role": "user", "content": message.content}]
                }
            )
            
            res_data = response.json()
            
            if 'choices' in res_data:
                answer = res_data['choices'][0]['message']['content']
                await message.channel.send(answer[:2000])
            else:
                # طباعة الخطأ في السجلات لمعرفته
                error_msg = res_data.get('error', {}).get('message', 'خطأ غير معروف')
                print(f"API Error: {error_msg}")
                await message.channel.send(f"⚠️ مشكلة في الـ API: `{error_msg}`")

        except Exception as e:
            print(f"Error: {e}")
            await message.channel.send("⚙️ واجهت تداخلاً في الأفكار، حاول مجدداً!")

if __name__ == "__main__":
    keep_alive()
    # تأكد من وضع التوكن الصحيح في Render
    client.run(os.getenv('DISCORD_TOKEN'))
    
