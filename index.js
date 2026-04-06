require('dotenv').config();
const { Client, GatewayIntentBits } = require("discord.js");
const { GoogleGenerativeAI } = require("@google/generative-ai");
const express = require("express");

// 1. إعداد خادم ويب بسيط لمنع توقف البوت في Railway
const app = express();
const port = process.env.PORT || 3000;
app.get("/", (req, res) => res.send("Steve Bot is Active and Running!"));
app.listen(port, "0.0.0.0", () => console.log(`Web server listening on port ${port}`));

// 2. إعداد ذكاء جوجل الاصطناعي (Gemini)
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

// 3. إعداد بوت الديسكورد مع الصلاحيات اللازمة
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent // ضروري ليقرأ كلمة "ستيف"
    ]
});

client.on("ready", () => {
    console.log(`✅ تم تشغيل البوت بنجاح باسم: ${client.user.tag}`);
});

client.on("messageCreate", async (message) => {
    // تجاهل رسائل البوتات أو الرسائل التي لا تنادي "ستيف"
    if (message.author.bot || !message.content.includes("ستيف")) return;

    try {
        await message.channel.sendTyping(); // إظهار أن البوت يكتب...

        const result = await model.generateContent(message.content);
        const response = await result.response;
        const text = response.text();

        // تقسيم الرد إذا كان أطول من 2000 حرف (حدود ديسكورد)
        if (text.length > 2000) {
            const chunks = text.match(/[\s\S]{1,2000}/g);
            for (const chunk of chunks) {
                await message.reply(chunk);
            }
        } else {
            await message.reply(text);
        }
    } catch (error) {
        console.error("خطأ في معالجة الرسالة:", error);
        message.reply("⚠️ حدث خطأ أثناء محاولة الرد، تأكد من إعدادات API Key.");
    }
});

// 4. تسجيل الدخول
client.login("Dicord");

