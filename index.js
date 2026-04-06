const { Client, GatewayIntentBits } = require('discord.js');

// 1. إعداد البوت والصلاحيات (Intents) اللازمة
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent // ضروري جداً لقراءة محتوى الرسائل
    ]
});

// 2. رسالة تأكيد عند تشغيل البوت بنجاح
client.once('ready', () => {
    console.log(`✅ البوت يعمل الآن بنجاح باسم: ${client.user.tag}`);
});

// 3. كود معالجة الرسائل (بما في ذلك الكود الخاص بك لتقسيم الرسائل الطويلة)
client.on('messageCreate', async (message) => {
    // تجاهل رسائل البوتات الأخرى لتجنب التكرار اللانهائي
    if (message.author.bot) return;

    // مثال بسيط للتجربة: إذا كتب شخص "مرحبا"، سيرد عليه البوت
    if (message.content === 'مرحبا') {
        const text = 'أهلاً بك يا صديقي!';
        
        try {
            // كود الحماية الخاص بك من الرسائل الطويلة
            if (text.length > 2000) {
                const chunks = text.match(/[\s\S]{1,1999}/g) || [];
                for (const chunk of chunks) {
                    await message.reply(chunk);
                }
            } else {
                await message.reply(text);
            }
        } catch (error) {
            console.error("خطأ في معالجة الرسالة:", error);
            message.reply("⚠️ حدث خطأ أثناء محاولة الرد، تأكد من إعدادات البوت.");
        }
    }
});

// 4. تسجيل الدخول باستخدام المتغير البيئي (بدون أي علامات تنصيص)
client.login(process.env.BOT_TOKEN);
