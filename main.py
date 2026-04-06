import discord
import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- أولاً: إعداد خادم صغير لبقاء البوت نشطاً على Render ---
app = Flask('')

@app.route('/')
def home():
    return "Steve is Online and Running!"

def run_web_server():
    # Render يستخدم المنفذ 8080 غالباً
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web_server)
    t.start()

# --- ثانياً: إعداد الذكاء الاصطناعي وجسد البوت ---

# تحميل المفاتيح من إعدادات البيئة
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


# تعديل سطر الموديل ليكون أكثر كفاءة:
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="أجب باختصار وتركيز باللغة التي يتحدث بها المستخدم (عربي/إنجليزي)."
)


# إعداد صلاحيات ديسكورد
intents = discord.Intents.default()
intents.message_content = True 
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'-----------------------------------')
    print(f'ستيف (Steve) متصل الآن كـ: {client.user}')
    print(f'يستخدم نموذج: gemini-2.5-flash-lite')
    print(f'-----------------------------------')

@client.event
async def on_message(message):
    # لا يرد على نفسه
    if message.author == client.user:
        return

    # يبدأ "بالتفكير" (Writing...) في الديسكورد
    async with message.channel.typing():
        try:
            # إرسال الرسالة إلى الذكاء الاصطناعي
            response = model.generate_content(message.content)
            
            # معالجة الرد (ديسكورد لا يقبل أكثر من 2000 حرف)
            ai_reply = response.text
            if len(ai_reply) > 2000:
                # تقسيم الرد إذا كان طويلاً جداً
                for i in range(0, len(ai_reply), 2000):
                    await message.channel.send(ai_reply[i:i+2000])
            else:
                await message.channel.send(ai_reply)

        except Exception as e:
            print(f"Error: {e}")
            await message.channel.send("حدث خطأ تقني في معالجة الطلب، يرجى المحاولة لاحقاً.")

# --- ثالثاً: التشغيل النهائي ---

if __name__ == "__main__":
    # تشغيل خادم الويب الوهمي لـ Render
    keep_alive()
    # تشغيل "ستيف"
    if DISCORD_TOKEN:
        client.run(DISCORD_TOKEN)
    else:
        print("خطأ: لم يتم العثور على DISCORD_TOKEN في إعدادات البيئة!")
        
