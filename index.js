const { Client, GatewayIntentBits } = require('discord.js');
const { GoogleGenerativeAI } = require("@google/generative-ai");
const express = require('express');

// --- 1. إعداد خادم ويب صغير (لضمان عمل الخطة المجانية) ---
const app = express();
const port = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.send('✅ بوت ستيف يعمل الآن ومستيقظ!');
});

app.listen(port, () => {
  console.log(`📡 خادم الويب يعمل على المنفذ: ${port}`);
});

// --- 2. إعداد ديسكورد وبوت الذكاء الاصطناعي ---
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
    ],
});

// إعداد Gemini AI
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

// --- 3. أحداث البوت (Events) ---
client.once('ready', () => {
    console.log(`✅ تم تسجيل الدخول بنجاح باسم: ${client.user.tag}`);
});

client.on('messageCreate', async (message) => {
    // تجاهل رسائل البوتات لكي لا يدخل في حلقة مفرغة
    if (message.author.bot) return;

    // البوت سيرد إذا بدأت الرسالة بكلمة "ستيف"
    if (message.content.startsWith('ستيف')) {
        const prompt = message.content.replace('ستيف', '').trim();
        
        if (!prompt) {
            return message.reply("نعم؟ أنا معك، تفضل اسألني أي شيء (مثلاً: ستيف ما هي وظيفة الميتوكندريا؟)");
        }

        try {
            // إظهار أن البوت "يكتب الآن"
            await message.channel.sendTyping();

            // إرسال السؤال للذكاء الاصطناعي
            const result = await model.generateContent(prompt);
            const response = await result.response;
            const text = response.text();

            // الرد على المستخدم
            if (text.length > 2000) {
                // إذا كان الرد طويلاً جداً (أكثر من 2000 حرف) يتم تقسيمه
                const chunk = text.substring(0, 1900);
                await message.reply(chunk + "...");
            } else {
                await message.reply(text);
            }
        } catch (error) {
            console.

