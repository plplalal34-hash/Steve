import os
import requests
import discord
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "Steve Debug Mode is Live!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def keep_alive():
    Thread(target=run).start()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ {client.user} جاهز للفحص!')

@client.event
async def on_message(message):
    if message.author.bot: return

    # التحويل التلقائي لـ Qwen في الأسئلة العلمية (أحياء، كيمياء، إلخ)
    science = ["حل", "اشرح", "علل", "ما", "كيف", "أحياء", "كيمياء", "فيزياء"]
    model = "qwen/qwen-2.5-72b-instruct:free" if any(w in message.content for w in science) else "meta-llama/llama-3.3-70b-instruct:free"

    async with message.channel.typing():
        try:
            api_key = os.getenv("OPENROUTER_API_KEY")
            
            # إرسال الطلب مع Headers كاملة لضمان القبول
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "https://render.com", # مطلوب أحياناً للموديلات المجانية
                    "X-Title": "Steve Bot",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": message.content}]
                }
            )
            
            data = response.json()
            
            if 'choices' in data:
                await message.channel.send(data['choices'][0]['message']['content'][:2000])
            else:
                # سيكشف لك الآن السبب الحقيقي (مثلاً: رصيد غير كافٍ، أو مفتاح خاطئ)
                error_details = data.get('error', {}).get('message', 'Unknown Error')
                await message.channel.send(f"❌ رد OpenRouter: `{error_details}`")
                
        except Exception as e:
            await message.channel.send(f"⚠️ خطأ تقني: `{str(e)}`")

if __name__ == "__main__":
    keep_alive()
    client.run(os.getenv('DISCORD_TOKEN'))
    
