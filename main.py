import os
import discord
from groq import Groq
from openai import OpenAI # ديب سيك يستخدم مكتبة أوبن أي آي للتوافق
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- خادم البقاء ---
app = Flask('')
@app.route('/')
def home(): return "Steve Hybrid is Live!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

load_dotenv()

# --- إعداد المحركات ---
client_llama = Groq(api_key=os.getenv("GROQ_API_KEY"))
client_deepseek = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

intents = discord.Intents.default()
intents.message_content = True
client_discord = discord.Client(intents=intents)

@client_discord.event
async def on_ready():
    print(f'✅ ستيف الهجين جاهز! المتصل: {client_discord.user}')

@client_discord.event
async def on_message(message):
    if message.author == client_discord.user: return

    # نظام الذكاء الهجين
    scientific_keywords = ["حل", "اشرح", "مسألة", "برمج", "كود", "لماذا", "كيف"]
    is_scientific = any(word in message.content for word in scientific_keywords)

    async with message.channel.typing():
        try:
            if is_scientific:
                # استخدام DeepSeek للمهام المعقدة
                response = client_deepseek.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": message.content}],
                    stream=False
                )
                answer = "🧠 [DeepSeek]: " + response.choices[0].message.content
            else:
                # استخدام Llama 3 للدردشة السريعة
                response = client_llama.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": message.content}]
                )
                answer = "⚡ [Llama 3]: " + response.choices[0].message.content

            await message.channel.send(answer[:2000])

        except Exception as e:
            print(f"Error: {e}")
            await message.channel.send("⚙️ واجهت تداخلاً في الأفكار، حاول مجدداً!")

if __name__ == "__main__":
    keep_alive()
    client_discord.run(os.getenv('DISCORD_TOKEN'))
    
