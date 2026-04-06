import os
import requests
import discord
from flask import Flask
from threading import Thread

# --- إعداد سيرفر Render ---
app = Flask('')
@app.route('/')
def home(): return "Steve Admin OS is Active"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def keep_alive():
    Thread(target=run).start()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ {client.user} جاهز للعمل بنظام المدير والموظف!')

@client.event
async def on_message(message):
    if message.author.bot: return

    # --- معيار الفصل: هل الرسالة "أمر إداري" أم "دردشة عادية"؟ ---
    admin_tokens = ["قرار", "إدارة", "سيرفر", "أمر", "تنظيم", "قانون", "رتبة", "صلاحية"]
    is_admin = any(token in message.content for token in admin_tokens)

    if is_admin:
        # عقل "المدير الإداري" - نستخدم النسخة 7B لأنها متاحة دائماً ومستقرة
        model = "qwen/qwen-2.5-7b-instruct:free"
        system_msg = "أنت المدير الإداري لـ Steve. وظيفتك اتخاذ قرارات حازمة وتنظيمية بأسلوب رسمي."
        label = "👔 **الإدارة (Qwen):**"
    else:
        # عقل "الموظف الودود" للدردشة
        model = "meta-llama/llama-3.1-8b-instruct:free"
        system_msg = "أنت ستيف، صديق مرح للدردشة العادية."
        label = "💬 **ستيف (Llama):**"

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
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": message.content}
                    ]
                }
            )
            
            res = response.json()
            if 'choices' in res:
                content = res['choices'][0]['message']['content']
                await message.channel.send(f"{label}\n{content}")
            else:
                # إذا كان الموديل مشغولاً، سيعطيك السبب فوراً
                err = res.get('error', {}).get('message', 'خطأ تقني')
                await message.channel.send(f"⚠️ فشل الطلب: `{err}`")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    keep_alive()
    client.run(os.getenv('DISCORD_TOKEN'))
    
