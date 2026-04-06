import { Client, GatewayIntentBits, Partials } from 'discord.js';
import { GoogleGenerativeAI } from '@google/generative-ai';
import express from 'express';

const app = express();
app.get('/', (req, res) => res.send('Steve Pro is Monitoring...'));
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
// تجربة الإصدار الأقوى Pro بناءً على طلبك
const model = genAI.getGenerativeModel({ 
    model: "gemini-1.5-pro" 
});

client.once('ready', () => {
    console.log(`✅ تم تفعيل العقل المطور (Pro) لـ: ${client.user.tag}`);
});

client.on('messageCreate', async (message) => {
    if (message.author.bot) return;

    // مراقبة كاملة: منشن، نداء باسمه، أو رد مباشر
    const isMentioned = message.mentions.has(client.user);
    const startsWithSteve = message.content.startsWith('ستيف');
    const isReplyToBot = message.reference && (await message.channel.messages.fetch(message.reference.messageId)).author.id === client.user.id;

    if (!isMentioned && !startsWithSteve && !isReplyToBot) return;

    const prompt = message.content.replace(/<@!?\d+>/g, '').replace('ستيف', '').trim();

    try {
        await message.channel.sendTyping();

        const result = await model.generateContent(prompt);
        const responseText = result.response.text();

        if (responseText) {
            await message.reply(responseText);
        }
    } catch (error) {
        // إظهار سبب الفشل التقني فوراً في الشات
        console.error("DEBUG:", error.message);
        await message.reply(`❌ **تنبيه تقني (Debug):**\n\`\`\`\n${error.message}\n\`\`\``);
    }
});

client.login(process.env.BOT_TOKEN);
