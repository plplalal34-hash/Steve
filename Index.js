require('dotenv').config();
const { Client, GatewayIntentBits } = require("discord.js");
const { GoogleGenerativeAI } = require("@google/generative-ai");
const express = require("express");

const app = express();
const port = process.env.PORT || 3000;
app.get("/", (req, res) => res.send("STEVE_IS_READY"));
app.listen(port, "0.0.0.0");

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

const client = new Client({
    intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent]
});

client.on("ready", () => console.log(`✅ Ready! ${client.user.tag}`));

client.on("messageCreate", async (message) => {
    if (message.author.bot || !message.content.includes("ستيف")) return;
    try {
        await message.channel.sendTyping();
        const result = await model.generateContent(message.content);
        const response = await result.response;
        await message.reply(response.text());
    } catch (e) {
        console.error(e);
    }
});

client.login(process.env.DISCORD_BOT_TOKEN);
