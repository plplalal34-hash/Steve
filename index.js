import { Client, GatewayIntentBits } from 'discord.js';
import { GoogleGenerativeAI } from '@google/generative-ai';
import express from 'express';

// إبقاء البوت متصلاً على Render
const app = express();
app.get('/', (req, res) => res.send('Steve Bridge is Active! ✅'));
app.listen(process.env.PORT || 3000);

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
    ],
});

// إعداد الاتصال بـ Gemini
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ 
    model: "gemini-1.5-flash" // هذا الإصدار هو الأكثر استقراراً لتجنب خطأ 404
});

client.once('ready', () => {
    console.log(`✅ تم تشغيل الجسد بنجاح باسم: ${client.user.tag}`);
});

client.on('messageCreate', async (message) => {
    // تجاهل رسائل البوتات أو الرسائل التي لا تبدأ بكلمة "ستيف"
    if (message.author.bot || !message.content.startsWith('ستيف')) return;

    // استخراج النص المرسل بعد كلمة "ستيف"
    const userPrompt = message.content.replace('ستيف', '').trim();
    if (!userPrompt) return message.reply("تفضل، ماذا تريد أن أرسل لـ Gemini؟");

    try {
        // إظهار أن البوت يكتب الآن في الديسكورد
        await message.channel.sendTyping();
        
        // 1. إرسال الكلام إلى جيميناي
        const result = await model.generateContent(userPrompt);
        
        // 2. أخذ الكلام الناتج من جيميناي
        const geminiResponse = result.response.text();
        
        // 3. وضع الكلام نفسه في الديسكورد كرد على المستخدم
        if (geminiResponse) {
            await message.reply(geminiResponse);
        } else {
            throw new Error("Empty Response from AI");
        }

    } catch (error) {
        console.error("خطأ في نقل البيانات:", error);
        await message.reply("عذراً، حدث خطأ أثناء محاولة جلب الرد من Gemini. تأكد من إعدادات الـ API Key.");
    }
});

client.login(process.env.BOT_TOKEN);
