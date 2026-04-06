import discord
import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- نظام البقاء حياً على Render ---
app = Flask('')
@app.route('/')
def home(): return "Steve is Online with Gemini 1.5 Flash!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- إعدادات الهوية والمفاتيح ---
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# إعداد المكتبة
genai.configure(api_key=GEMINI_API_KEY)

# تعريف الموديل 1.5 Flash بالصيغة المتوافقة مع 0.7.2
model = genai.GenerativeModel(
    model_name="models/gemini-1.5-flash" # إضافة كلمة models/ لضمان التعرف عليه
)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ تم الاتصال بنجاح كـ: {client.user}')
    print(f'العقل الحالي: Gemini 1.5 Flash')

@client.event
async def on_message(message):
    if message.author == client.user: return

    async with message.channel.typing():
        try:
            # إرسال المحادثة
            response = model.generate_content(message.content)
            
            # التأكد من نجاح الرد
            if response and response.text:
                await message.channel.send(response.text[:2000])
            else:
                await message.channel.send("⚠️ تلقيت رداً فارغاً من الذكاء الاصطناعي.")

        except Exception as e:
            err_msg = str(e)
            print(f"Error: {err_msg}")
            
            if "429" in err_msg:
                await message.channel.send("⚠️ وصلت للحد الأقصى للرسائل (Rate Limit)، انتظر دقيقة.")
            elif "400" in err_msg:
                await message.channel.send("⚠️ خطأ في الطلب (قد يكون المحتوى غير مدعوم).")
            else:
                await message.channel.send(f"⚠️ خطأ تقني: {err_msg[:100]}")

if __name__ == "__main__":
    keep_alive()
    if DISCORD_TOKEN:
        client.run(DISCORD_TOKEN)
