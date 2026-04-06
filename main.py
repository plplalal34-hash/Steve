import os
import requests
import discord
from flask import Flask
from threading import Thread

# --- سيرفر الويب لمنع Render من إيقاف البوت ---
app = Flask('')
@app.route('/')
def home(): return "Steve Hybrid (Llama + Qwen) is Online!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# --- إعداد ديسكورد ---
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ {client.user} متصل الآن بنظام الهجين الذكي!')

@client.event
async def on_message(message):
    # منع البوت من الرد على نفسه أو على بوتات أخرى لمنع التكرار
    if message.author.bot: 
        return

    # الكلمات المفتاحية التي تستدعي Qwen للأسئلة المعقدة والعلمية
    hard_keywords = ["حل", "اشرح", "كيف", "لماذا", "ما هي", "عرف", "وضح", "مسألة", "علل", "قارن", "فيزياء", "كيمياء", "أحياء", "رياضيات", "وزاري", "برمج", "كود"]
    
    # فحص ما إذا كانت رسالتك تحتوي على إحدى هذه الكلمات
    is_hard = any(word in message.content for word in hard_keywords)

    # توجيه الطلب للعقل المناسب
    if is_hard:
        model_to_use = "qwen/qwen-2.5-72b-instruct:free"
        prefix = "🧠 **[Qwen - للمهام المعقدة]:**\n"
    else:
        model_to_use = "meta-llama/llama-3.3-70b-instruct:free"
        prefix = "⚡ **[Llama - للدردشة]:**\n"

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
                    "model": model_to_use,
                    "messages": [
                        {"role": "system", "content": "أنت ستيف، مساعد ذكي. إذا كان السؤال علمياً أجب بدقة منهجية، وإذا كان دردشة عادية كن مرحاً ولطيفاً."},
                        {"role": "user", "content": message.content}
                    ]
                }
            )
            
            res_json = response.json()
            
            if 'choices' in res_json:
                answer = res_json['choices'][0]['message']['content']
                # دمج الرمز مع الإجابة وقصها إذا تجاوزت حد ديسكورد
                final_reply = f"{prefix}{answer}"
                await message.channel.send(final_reply[:2000])
            else:
                error_info = res_json.get('error', {}).get('message', 'خطأ غير معروف في المفتاح')
                await message.channel.send(f"❌ مشكلة في مفتاح OpenRouter: {error_info}")
                
        except Exception as e:
            print(f"Error: {e}")
            await message.channel.send("⚠️ حدث خطأ في الاتصال بالشبكة.")

if __name__ == "__main__":
    keep_alive()
    client.run(os.getenv('DISCORD_TOKEN'))
    
