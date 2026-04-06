import { Client, GatewayIntentBits, PermissionFlagsBits } from 'discord.js';
import { GoogleGenerativeAI } from '@google/generative-ai';
import express from 'express';

// --- إعداد خادم الويب (لضمان عمل الخطة المجانية) ---
const app = express();
app.get('/', (req, res) => res.send('Steve Bot is Online! ✅'));
app.listen(process.env.PORT || 3000);

// --- إعداد ديسكورد ---
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMembers,
    ],
});

// --- إعداد الذكاء الاصطناعي ---
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ 
    model: "gemini-1.5-flash",
    systemInstruction: "أنت ستيف، مدير سيرفر ذكي. وظيفتك الإجابة على الأسئلة والتحكم في السيرفر. إذا طلب منك شخص مسح رسائل، أخبره أنك ستقوم بذلك."
});

client.once('ready', () => {
    console.log(`✅ تم تشغيل الجسد (ستيف) بنجاح باسم: ${client.user.tag}`);
});

client.on('messageCreate', async (message) => {
    if (message.author.bot || !message.content.startsWith('ستيف')) return;

    const prompt = message.content.replace('ستيف', '').trim();

    try {
        await message.channel.sendTyping();

        // --- ميزة التحكم في السيرفر (مسح الرسائل) ---
        if (prompt.includes('امسح') || prompt.includes('احذف')) {
            if (!message.member.permissions.has(PermissionFlagsBits.ManageMessages)) {
                return message.reply("ليس لديك صلاحية لمسح الرسائل يا صديقي.");
            }
            const amount = parseInt(prompt.match(/\d+/)?.[0]) || 5;
            await message.channel.bulkDelete(amount + 1);
            return message.channel.send(`🧹 نفذت الأمر! تم مسح ${amount} رسالة بنجاح.`);
        }

        // --- الرد الذكي عبر AI ---
        const result = await model.generateContent(prompt);
        const response = await result.response;
        await message.reply(response.text());

    } catch (error) {
        console.error(error);
        await message.reply("عذراً، واجه 'عقلي' مشكلة في المعالجة!");
    }
});

client.login(process.env.BOT_TOKEN);
