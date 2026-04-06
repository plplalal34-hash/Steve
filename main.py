import os
import requests
import discord
from flask import Flask
from threading import Thread

# --- سيرفر الويب لضمان استمرارية Render ---
app = Flask('')
@app.route('/')
def home(): return "Steve Admin System is Live!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def keep_alive():
    Thread(target=run).start()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True # لتمكين القرارات الإدارية مثل الطرد أو الحظر
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ {client.user} متصل بنظام الإدارة الذكي!')

@client.event
async def on_message(message):
    if message.author.bot: return

    # --- تحديد "النية" إدارية أم عادية ---
    # كلمات تدل على قرارات إدارية أو أوامر للنظام
    admin_keywords = ["طرد", "حظر", "اسكت", "تكلم", "رتب", "نظم", "قرار", "صلاحية", "إدارة", "سيرفر", "إعدادات"]
    is_admin_task = any(word in message.content for word in admin_keywords)

    if is_admin_task:
        # عقل المدير (اتخاذ القرارات)
        selected_model = "qwen/qwen-2.5-7b-instruct:free"
        system_prompt = "أنت المدير الإداري لـ Steve. مهمتك اتخاذ قرارات حازمة، تنظيم السيرفر، والإجابة كمسؤول عن النظام."
        prefix = "👔 **[المدير الإداري - Qwen]:** "
    else:
        # عقل المساعد (الدردشة العادية)
        selected_model = "meta-llama/llama-3.1-8b-instruct:free"
        system_prompt = "أنت ستيف، صديق مرح وودود. دردش مع المستخدمين بلطف وبساطة."
        prefix = "💬 **[ستيف - Llama]:** "

    async with message.channel.typing():
        try:
            api_key = os.getenv("OPENROUTER_API_KEY")
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": selected_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message.content}
                    ],
                    "route": "fallback"
                }
            )
            
            data = response.json()
            if 'choices' in data:
                res_text = data['choices'][0]['message']['content']
                await message.channel.send(f"{prefix}{res_text}"[:2000])
            else:
                await message.channel.send("⚠️ يبدو أن المدير مشغول حالياً، حاول مجدداً.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    keep_alive()
    client.run(os.getenv('DISCORD_TOKEN'))
