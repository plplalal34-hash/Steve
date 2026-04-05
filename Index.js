const { Client, GatewayIntentBits } = require('discord.js');
const { GoogleGenerativeAI } = require('@google/generative-ai');

// إعداد ديسكورد
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent
    ]
});

// إعداد Gemini
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

client.on('messageCreate', async (message) => {
    // تجاهل رسائل البوتات
    if (message.author.bot) return;

    // إظهار حالة "يكتب..." في ديسكورد
    await message.channel.sendTyping();

    try {
        const result = await model.generateContent(message.content);
        const response = await result.response;
        await message.reply(response.text());
    } catch (error) {
        console.error("Gemini Error:", error);
        await message.reply("عذراً، حدث خطأ في الاتصال. تأكد من صلاحية مفتاح Gemini.");
    }
});

client.once('ready', () => {
    console.log(`✅ Bot is online as ${client.user.tag}`);
});

client.login(process.env.DISCORD_BOT_TOKEN);
