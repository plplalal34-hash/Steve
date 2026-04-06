require('dotenv').config();
const { Client, GatewayIntentBits } = require("discord.js");
const { GoogleGenerativeAI } = require("@google/generative-ai");
const express = require("express");

// إعداد خادم ويب صغير لمنع توقف البوت على Railway
const app = express();
const port = process.env.PORT || 3000;
app.get("/", (req, res) => res.send("Steve Bot is Online!"));
app.listen(port, "0.0.0.0", () => console.log(`Listening on port ${port}`));

// إعداد ذكاء جوجل الاصطناعي (Gemini)
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

// إعداد بوت الديسكورد
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent
    ]
});

client.on("ready", () => {
    console.log(`✅ تم تسجيل الدخول بنجاح باسم: ${client.user.tag}`);
});

client.on("messageCreate", async (message) => {
    // تجاهل رسائل البوتات أو الرسائل التي لا تحتوي على كلمة "ستيف"
    if (message.author.bot || !message.content.includes("ستيف")) return;

    try {
        // إظهار أن البوت "يكتب الآن..."
        await message.channel.sendTyping();

        // إرسال النص إلى Gemini واستلام الرد
        const result = await model.generateContent(message.content);
        const response = await result.response;
        const text = response.text();

        // الرد على المستخدم (تقسيم النص إذا كان طويلاً جداً)
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
        message.reply("⚠️ عذراً، واجهت مشكلة في معالجة طلبك حالياً.");
    }
});

// تشغيل البوت باستخدام التوكن المخزن في المتغيرات
client.login(process.env.DISCORD_BOT_TOKEN);
