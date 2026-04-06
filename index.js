import { Client, GatewayIntentBits, Partials } from 'discord.js';
import { GoogleGenerativeAI } from '@google/generative-ai';
import express from 'express';

// تشغيل خادم بسيط للبقاء متصلاً على Render
const app = express();
app.get('/', (req, res) => res.send('Steve is thinking...'));
app.listen(process.env.PORT || 3000);

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
    ],
    partials: [Partials.Message, Partials.Channel],
});

// إعداد Gemini
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

client.once('ready', () => {
    console.log(`✅ ${client.user.tag} متصل وجاهز!`);
});

client.on('messageCreate', async (message) => {
    // تجاهل رسائل البوتات
    if (message.author.bot) return;

    // شروط الرد: منشن، كلمة ستيف، أو رد (Reply) على البوت
    const isMentioned = message.mentions.has(client.user);
    const startsWithSteve = message.content.startsWith('ستيف');
    const isReplyToBot = message.reference && (await message.channel.messages.fetch(message.reference.messageId)).author.id === client.user.id;

    if (!isMentioned && !startsWithSteve && !isReplyToBot) return;

    // تنظيف النص
    const prompt = message.content.replace(/<@!?\d+>/g, '').replace('ستيف', '').trim();
    if (!prompt && isMentioned) return; 

    try {
        // إظهار حالة "يكتب..." فوراً
        await message.channel.sendTyping();

        // إرسال الطلب ومعالجته (التأخير هنا يحدث بشكل طبيعي حسب سرعة الرد)
        const result = await model.generateContent(prompt);
        const responseText = result.response.text();

        if (responseText) {
            // إرسال الرد النهائي كاملاً في رسالة واحدة
            await message.reply({
                content: responseText,
                allowedMentions: { repliedUser: true }
            });
        }
    } catch (error) {
        // إدارة الأخطاء بصمت: لن يتم إرسال أي رسالة تقنية مزعجة في الديسكورد
        console.error("Silent Error: Problem connecting to Gemini.");
    }
});

client.login(process.env.BOT_TOKEN);
