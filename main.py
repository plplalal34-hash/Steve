import os
import requests
import discord
from flask import Flask
from threading import Thread

# --- إعداد سيرفر الويب لمنع Render من إيقاف البوت ---
app = Flask('')

@app.route('/')
def home():
    return "Steve Hybrid is Live!"

def run():
    # Render يطلب استخدام المنفذ الممرر في البيئة أو 10000 كافتراضي
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- إعداد ديسكورد ---
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ متصل الآن باسم: {client.user}')

@client.event
async def on_message(message):
    # حماية: لا يرد البوت على نفسه أو على أي بوت آخر
    if message.author.bot:
        return

    # الكلمات المفتاحية العلمية/الصعبة لتحفيز Qwen
    hard_topics = ["حل", "اشرح", "علل", "ما هي وظيفة", "مسألة", "كيمياء", "فيزياء", "أحياء", "رياضيات"]
    is_hard = any(word in message.content for word in hard_topics)

    # اختيار الموديل بناءً على صعوبة السؤال
    # Llama للدردشة و Qwen للمسائل العلمية الصعبة
    selected_model = "qwen/qwen-2.5-72b-instruct:free" if is_hard else "meta-llama/llama-3.3-70b-instruct:free"
    prefix = "🧠 **[Qwen]:** " if is_hard else "⚡ **[Llama]:** "

    async with message.channel.typing():
        try:
            api_key = os.getenv("OPENROUTER_API_KEY")
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": selected_model,
                    "messages": [{"role": "user", "content": message.content}]
                }
            )
            
            res_data = response.json()
            if 'choices' in res_data:
                answer = res_data['choices'][0]['message']['content']
                await message.channel.send(f"{prefix}{answer}"[:2000])
            else:
                error_msg = res_data.get('error', {}).get('message', 'Invalid API Key or Limit reached')
                print(f"API Error: {error_msg}")
                await message.channel.send(f"⚠️ عذراً، واجهت مشكلة في المفتاح: `{error_msg}`")
        
        except Exception as e:
            print(f"Exception: {e}")
            await message.channel.send("⚠️ حدث خطأ تقني في الاتصال.")

if __name__ == "__main__":
    keep_alive() # تشغيل السيرفر الجانبي لـ Render
    client.run(os.getenv('DISCORD_TOKEN'))
    
