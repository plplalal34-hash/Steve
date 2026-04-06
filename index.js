import { Client, GatewayIntentBits, Partials } from 'discord.js';
import { GoogleGenerativeAI } from '@google/generative-ai';
import express from 'express';

const app = express();
app.get('/', (req, res) => res.send('Steve Debug Mode Active!'));
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
// محاولة استخدام إصدار 1.0 كما طلبت
const model = genAI.getGenerativeModel({ model: "gemini-1.0-pro" });

client.once('ready', () => {
    console.log(`✅ ${client.user.tag} متصل في وضع كشف الأخطاء`);
});

client.on('messageCreate', async (message) => {
    if (message.author.bot) return;

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
        // إظهار المشكلة التقنية بالتفصيل في الديسكورد
        console.error("DEBUG ERROR:", error);
        await message.reply(`❌ **خطأ تقني مكتشف:**\n\`\`\`\n${error.message}\n\`\`\``);
    }
});

client.login(process.env.BOT_TOKEN);
