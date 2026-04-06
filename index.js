import { Client, GatewayIntentBits } from 'discord.js';
import { GoogleGenerativeAI } from '@google/generative-ai';
import express from 'express';

// خادم ويب للبقاء أونلاين على Render
const app = express();
app.get('/', (req, res) => res.send('Steve is Online! ✅'));
app.listen(process.env.PORT || 3000);

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
    ],
});

// ربط الذكاء الاصطناعي
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

// محاولة استخدام الإصدار الذي طلبته
const model = genAI.getGenerativeModel({ 
    model: "gemini-2.5-flash" 
});

client.once('ready', () => {
    console.log(`✅ تم تشغيل الجسد بنجاح باسم: ${client.user.tag}`);
});

client.on('messageCreate', async (message) => {
    if (message.author.bot || !message.content.startsWith('ستيف')) return;

    const prompt = message.content.replace('ستيف', '').trim();

    try {
        await message.channel.sendTyping();
        
        const result = await model.generateContent(prompt);
        const response = result.response.text();
        
        await message.reply(response);

    } catch (error) {
        console.error("خطأ:", error);
        // رسالة تنبيه في حال كان الإصدار غير مدعوم
        await message.reply("عذراً، واجهت مشكلة في الاتصال بـ 'عقلي'. قد يكون إصدار الموديل غير متوفر حالياً.");
    }
});

client.login(process.env.BOT_TOKEN);
