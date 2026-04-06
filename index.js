const { Client, GatewayIntentBits, PermissionsBitField } = require('discord.js');
const { GoogleGenerativeAI } = require("@google/generative-ai");
const express = require('express');

// --- 1. خادم ويب صغير للاستضافة ---
const app = express();
app.get('/', (req, res) => res.send('✅ عقل ستيف الإلكتروني يعمل!'));
app.listen(process.env.PORT || 3000);

// --- 2. إعداد ديسكورد ---
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMembers, // ضروري للتحكم بالأعضاء
    ],
});

// --- 3. إعداد الذكاء الاصطناعي مع "أدوات التحكم" ---
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

// تعريف الوظائف التي يمكن للذكاء الاصطناعي استخدامها
const tools = {
    // وظيفة مسح الرسائل
    clearMessages: async (amount, channelId) => {
        const channel = await client.channels.fetch(channelId);
        await channel.bulkDelete(Math.min(amount, 100));
        return `تم مسح ${amount} رسالة بنجاح.`;
    },
    // وظيفة طرد عضو
    kickUser: async (userId, guildId, reason) => {
        const guild = await client.guilds.fetch(guildId);
        const member = await guild.members.fetch(userId);
        await member.kick(reason);
        return `تم طرد المستخدم ${member.user.tag}.`;
    }
};

const model = genAI.getGenerativeModel({ 
    model: "gemini-1.5-flash",
    systemInstruction: "أنت عقل بوت ديسكورد اسمه 'ستيف'. لديك صلاحيات إدارية. إذا طلب منك المستخدم القيام بفعل إداري (مثل المسح أو الطرد)، استخدم الأدوات المتاحة لك. كن مهذباً ولكن حازماً."
});

// --- 4. معالجة الرسائل والتحكم ---
client.on('messageCreate', async (message) => {
    if (message.author.bot || !message.content.startsWith('ستيف')) return;

    const prompt = message.content.replace('ستيف', '').trim();
    
    try {
        await message.channel.sendTyping();

        // إرسال الرسالة للذكاء الاصطناعي
        const chat = model.startChat();
        const result = await chat.sendMessage(prompt);
        const response = result.response.text();

        // هنا نقوم بفحص ما إذا كان الـ AI يريد تنفيذ أمر
        // ملاحظة: لتبسيط الأمر لك، سنجعل الـ AI يرد نصياً ويقوم بالعمل خلف الكواليس
        
        if (prompt.includes('احذف') || prompt.includes('امسح')) {
            const num = prompt.match(/\d+/); // استخراج الرقم من النص
            if (num && message.member.permissions.has(PermissionsBitField.Flags.ManageMessages)) {
                await tools.clearMessages(parseInt(num[0]), message.channelId);
            }
        }

        if (prompt.includes('اطرد')) {
             // منطق استخراج العضو والطرد
             // يمكن تطويره باستخدام Mentions
        }

        await message.reply(response);

    } catch (error) {
        console.error(error);
        await message.reply("واجهت مشكلة في معالجة طلبك الإداري.");
    }
});

client.login(process.env.BOT_TOKEN);
