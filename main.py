import sys
import types
import os

# تجاوز نقص مكتبة الصوت في الإصدارات الحديثة
if 'audioop' not in sys.modules:
    sys.modules['audioop'] = types.ModuleType('audioop')

import discord
import google.generativeai as genai
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

# --- خادم صغير للبقاء نشطاً ---
app = Flask('')
@app.route('/')
def home(): return "Steve is Active!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- إعدادات جيميني ---
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# إعدادات الأمان (إيقاف كافة أنواع الحظر التلقائي)
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    safety_settings=safety_settings
)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ {client.user} جاهز للدردشة!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    async with message.channel.typing():
        try:
            # طلب الرد
            response = model.generate_content(message.content)
            
            # محاولة جلب النص بأكثر من طريقة لضمان النجاح
            res_text = ""
            try:
                res_text = response.text
            except:
                if response.candidates:
                    res_text = response.candidates[0].content.parts[0].text
            
            if res_text:
                await message.channel.send(res_text[:2000])
            else:
                await message.channel.send("⚠️ جوجل لم يرسل نصاً، قد يكون المحتوى حساساً جداً.")

        except Exception as e:
            error_msg = str(e)
            print(f"Error Detail: {error_msg}")
            
            # إرسال تفصيل الخطأ لتعرف ما المشكلة بالضبط
            if "API_KEY_INVALID" in error_msg:
                await message.channel.send("❌ مفتاح الـ API غير صالح.")
            elif "quota" in error_msg.lower():
                await message.channel.send("⏳ انتهت صلاحية الاستخدام المجاني لليوم.")
            else:
                await message.channel.send(f"⚙️ خطأ تقني: `{error_msg[:100]}`")

if __name__ == "__main__":
    keep_alive()
    client.run(os.getenv('DISCORD_TOKEN'))
    
