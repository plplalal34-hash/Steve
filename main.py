import discord
import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- إعداد خادم الويب (Keep-Alive) ---
app = Flask('')
@app.route('/')
def home(): return "Steve is running on Legacy Code!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- إعدادات البوت ---
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# التعريف القديم والمستقر لمكتبة جوجل
genai.configure(api_key=GEMINI_API_KEY)

# استخدام مصفوفة الإعدادات القديمة لضمان عمل 1.5 Flash
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 800,
}

# تعريف الموديل بالصيغة القديمة
model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config
)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ ستيف متصل بالنسخة المستقرة: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user: return

    async with message.channel.typing():
        try:
            # طريقة المناداة الكلاسيكية
            response = model.generate_content(message.content)
            
            # في النسخ القديمة أحياناً نحتاج للتأكد من وجود النص
            if response.text:
                await message.channel.send(response.text[:2000])
            else:
                await message.channel.send("عذراً، لم أستطع الرد حالياً.")

        except Exception as e:
            err = str(e)
            print(f"Error: {err}")
            if "429" in err:
                await message.channel.send("⚠️ ضغط كبير على السيرفر، سأنتظر دقيقة.")
            else:
                await message.channel.send(f"⚠️ خطأ تقني: {err[:50]}")

if __name__ == "__main__":
    keep_alive()
    if DISCORD_TOKEN:
        client.run(DISCORD_TOKEN)
        
