import { Client, GatewayIntentBits, Partials } from 'discord.js';
import { GoogleGenerativeAI } from '@google/generative-ai';
import express from 'express';

// خادم الويب للبقاء أونلاين
const app = express();
app.get('/', (req, res) => res.send('Steve 1.0 Monitoring Mode Active!'));
app.listen(process.env.PORT || 3000);

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
    ],
    partials: [Partials.Message, Partials.Channel],
});

// إعداد Gemini 1.0
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ 
    model: "gemini-1.0-pro" 
});

client.once('ready', () => {
    console.log(`✅ ${client.user.tag} يراقب الشات الآن بنسخة 1.0`);
});

client.on('messageCreate', async (message) => {
    if (message.author.bot) return;

    // مراقبة الشات: الرد عند المنشن، أو كلمة ستيف، أو الردود (Replies)
    const isMentioned = message.mentions.has(client.user);
    const startsWithSteve = message.content.startsWith('ستيف');
    const isReplyToBot = message.reference && (await message.channel.messages.fetch(message.reference.messageId)).author.id === client.user.id;

    if (!isMentioned && !startsWithSteve && !isReplyToBot) return;

    const prompt = message.content.replace(/<@!?\d+>/g, '').replace('ستيف', '').trim();

    try {
        // إظهار حالة "يكتب..."
        await message.channel.sendTyping();

        // إرسال البيانات للذكاء الاصطناعي
        const result = await model.generateContent(prompt);
        const responseText = result.response.text();

        if (responseText) {
            await message.reply(responseText);
        }
    } catch (error) {
        // عرض الخطأ التقني فوراً في الديسكورد لمعرفة سبب التوقف
        console.error("DEBUG:", error.message);
        await message.reply(`❌ **تنبيه تقني (Debug):**\n\`\`\`\n${error.message}\n\`\`\``);
    }
});

client.login(process.env.BOT_TOKEN);
