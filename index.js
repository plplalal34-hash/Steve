import { Client, GatewayIntentBits, PermissionFlagsBits } from 'discord.js';
import { GoogleGenerativeAI } from '@google/generative-ai';
import express from 'express';

// --- خادم ويب للبقاء مستيقظاً (لـ Render) ---
const app = express();
app.get('/', (req, res) => res.send('✅ Steve AI is Online and Ready!'));
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

// --- إعداد أحدث نسخة من Gemini AI ---
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
// استخدمنا "gemini-1.5-flash" مباشرة مع تهيئة النظام
const model = genAI.getGenerativeModel({ 
    model: "gemini-1.5-flash",
    systemInstruction: "أنت 'ستيف'، بوت ذكي ومساعد في سيرفر ديسكورد. يمكنك الإجابة على الأسئلة العلمية وإدارة السيرفر. إذا طلب منك شخص حذف رسائل، فقم بذلك برمجياً."
});

client.once('ready', () => {
    console.log(`✅ تم تشغيل الجسد بنجاح باسم: ${client.user.tag}`);
});

client.on('messageCreate', async (message) => {
    // تجاهل رسائل البوتات أو الرسائل التي لا تبدأ بـ "ستيف"
    if (message.author.bot || !message.content.startsWith('ستيف')) return;

    const prompt = message.content.replace('ستيف', '').trim();

    try {
        await message.channel.sendTyping();

        // --- ميزة التحكم: مسح الرسائل ---
        if (prompt.includes('امسح') || prompt.includes('احذف')) {
            if (message.member.permissions.has(PermissionFlagsBits.ManageMessages)) {
                const amount = parseInt(prompt.match(/\d+/)?.[0]) || 5;
                await message.channel.bulkDelete(amount + 1);
                return message.channel.send(`🧹 تم تنظيف المكان! مسحت ${amount} رسالة.`);
            } else {
                return message.reply("ليس لديك الصلاحية لاستخدام هذه القوة!");
            }
        }

        // --- الرد الذكي باستخدام أحدث API ---
        const result = await model.generateContent(prompt);
        const text = result.response.text();
        
        if (text) {
            await message.reply(text);
        } else {
            throw new Error("Empty Response");
        }

    } catch (error) {
        console.error("خطأ في العقل:", error);
        // رسالة تنبيه إذا فشل الـ AI في الاتصال
        await message.reply("عذراً، يبدو أن هناك مشكلة في اتصالي بمزود الذكاء الاصطناعي. تأكد من صلاحية الـ API Key.");
    }
});

client.login(process.env.BOT_TOKEN);
