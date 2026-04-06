import { Client, GatewayIntentBits, Partials } from 'discord.js';
import { GoogleGenerativeAI } from '@google/generative-ai';
import express from 'express';

const app = express();
app.get('/', (req, res) => res.send('Steve AI is Online! ✅'));
app.listen(process.env.PORT || 3000);

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
    ],
    partials: [Partials.Message, Partials.Channel],
});

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
// استخدم هذا المسمى الدقيق لتجنب خطأ 404
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

client.once('ready', () => {
    console.log(`✅ تم تشغيل الجسد بنجاح باسم: ${client.user.tag}`);
});

client.on('messageCreate', async (message) => {
    if (message.author.bot) return;

    const isMentioned = message.mentions.has(client.user);
    const startsWithSteve = message.content.startsWith('ستيف');
    const isReplyToBot = message.reference && (await message.channel.messages.fetch(message.reference.messageId)).author.id === client.user.id;

    if (!isMentioned && !startsWithSteve && !isReplyToBot) return;

    const prompt = message.content.replace(/<@!?\d+>/g, '').replace('ستيف', '').trim();
    if (!prompt && isMentioned) return;

    try {
        // تفعيل حالة "يكتب..." فوراً
        await message.channel.sendTyping();

        // إرسال الطلب لجيميناي وانتظار الرد (هذا هو وقت التفكير الطبيعي)
        const result = await model.generateContent(prompt);
        const responseText = result.response.text();

        if (responseText) {
            // إرسال الكلام الناتج في رسالة واحدة فقط
            await message.reply({
                content: responseText,
                allowedMentions: { repliedUser: true }
            });
        }
    } catch (error) {
        // إدارة الأخطاء بصمت تام دون إرسال رسائل تقنية للمستخدم
        console.error("Gemini Error:", error.message);
    }
});

client.login(process.env.BOT_TOKEN);
