import os
import requests
import discord
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "Llama Test is Online!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def keep_alive():
    Thread(target=run).start()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ متصل لاختبار Llama باسم: {client.user}')

@client.event
async def on_message(message):
    if message.author.bot: return

    async with message.channel.typing():
        try:
            api_key = os.getenv("OPENROUTER_API_KEY")
            # استخدام موديل Llama 3.1 8B المجاني والأكثر استقراراً
            model = "meta-llama/llama-3.1-8b-instruct:free"
            
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": message.content}]
                }
            )
            
            data = response.json()
            if 'choices' in data:
                await message.channel.send(f"⚡ **[Llama]:** {data['choices'][0]['message']['content']}")
            else:
                # طباعة الخطأ القادم من OpenRouter مباشرة
                error_info = data.get('error', {}).get('message', 'Unknown Error')
                await message.channel.send(f"❌ خطأ من المزود: `{error_info}`")
                
        except Exception as e:
            await message.channel.send(f"⚠️ خطأ في الكود: `{str(e)}`")

if __name__ == "__main__":
    keep_alive()
    client.run(os.getenv('DISCORD_TOKEN'))
    
