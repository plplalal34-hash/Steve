import { Client, GatewayIntentBits, Partials } from 'discord.js';
import { GoogleGenerativeAI } from '@google/generative-ai';
import express from 'express';

const app = express();
app.get('/', (req, res) => res.send('Steve is Ready!'));
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
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

client.once('ready', () => {
    console.log(`✅ ${client.user.tag} Online`);
});

client.on('messageCreate', async (message) => {
    if (message.author.bot) return;

    const isMentioned = message.mentions.has(client.user);
    const startsWithSteve = message.content.startsWith('ستيف');
    const isReplyToBot = message.reference && (await message.channel.messages.fetch(message.reference.messageId)).author.id === client.user.id;

    if (!isMentioned && !startsWithSteve && !isReplyToBot) return;

    const prompt = message.content.replace(/<@!?\d+>/g, '').replace('ستيف', '').trim();
    if (!prompt && isMentioned) return; // لن يرد إذا كان منشن فارغاً لتقليل الإزعاج

    try {
        // يبدأ بإظهار "يكتب..." فوراً ليأخذ وقته الطبيعي في المعالجة
        await message.channel.sendTyping();

        const result = await model.generateContent(prompt);
        const responseText = result.response.text();

        if (responseText) {
            // يرسل الرد في رسالة واحدة فقط عند اكتمال الجواب
            await message.reply({
                content: responseText,
                allowedMentions: { repliedUser: true }
            });
        }
    } catch (error) {
        // صمت تام في حال حدوث خطأ تقني؛ لن يرسل رسائل اعتذار أو أخطاء برمجية
        console.error("Silent Error Handler");
    }
});

client.login(process.env.BOT_TOKEN);

