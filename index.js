const { Client, GatewayIntentBits } = require('discord.js');
const { GoogleGenerativeAI } = require("@google/generative-ai");

// إعداد البوت وصلاحياته
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
    ],
});

// إعداد الذكاء الاصطناعي (Gemini)
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

client.once('ready', () => {
    console.log(`✅ تم تشغيل البوت بنجاح باسم: ${client.user.tag}`);
});

client.on('messageCreate', async (message) => {
    // تجاهل رسائل البوتات الأخرى
    if (message.author.bot) return;

    // البوت سيرد فقط إذا تم منشنته أو بدأت الرسالة بكلمة "ستيف"
    if (message.content.startsWith('ستيف')) {
        const prompt = message.content.replace('ستيف', '').trim();
        
        if (!prompt) return message.reply("نعم؟ أنا معك، تفضل اسألني أي شيء.");

        try {
            // إظهار أن البوت "يكتب الآن" لمزيد من الواقعية
            await message.channel.sendTyping();

            const result = await model.generateContent(prompt);
            const response = await result.response;
            const text = response.text();

            // إرسال رد الذكاء الاصطناعي
            await message.reply(text);
        } catch (error) {
            console.error("خطأ في الاتصال بالذكاء الاصطناعي:", error);
            await message.reply("عذراً، حدث خطأ أثناء محاولة التفكير. حاول مرة أخرى لاحقاً.");
        }
    }
});

// تسجيل الدخول باستخدام المتغير الذي وضعناه في Northflank
client.login(process.env.BOT_TOKEN);
