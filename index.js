import { Client, GatewayIntentBits } from 'discord.js';
import { GoogleGenerativeAI } from '@google/generative-ai';
import express from 'express';

// خادم ويب بسيط للبقاء متصلاً على Render
const app = express();
app.get('/', (req, res) => res.send('Steve AI is running!'));
app.listen(process.env.PORT || 3000);

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
    ],
});

// إعداد Gemini
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

// الحل هنا: تحديد الموديل بالإصدار الكامل لضمان عدم حدوث خطأ 404
const model = genAI.getGenerativeModel({ 
    model: "gemini-1.5-flash-latest" 
});

client.once('ready', () => {
    console.log(`✅ تم تشغيل الجسد بنجاح باسم: ${client.user.tag}`);
});

client.on('messageCreate', async (message) => {
    if (message.author.bot || !message.content.startsWith('ستيف')) return;

    const prompt = message.content.replace('ستيف', '').trim();

    try {
        await message.channel.sendTyping();
        
        // استخدام generateContent بطريقة متوافقة مع المكتبة الحديثة
        const result = await model.generateContent(prompt);
        const response = await result.response;
        const text = response.text();
        
        await message.reply(text);

    } catch (error) {
        console.error("خطأ في العقل:", error);
        await message.reply("عذراً، واجه 'عقلي' مشكلة في المعالجة! تأكد من أن مفتاح الـ API صحيح.");
    }
});

client.login(process.env.BOT_TOKEN);
