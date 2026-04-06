import 'dotenv/config';
import fs from 'node:fs/promises';
import path from 'node:path';
import { Client, GatewayIntentBits, Events, REST, Routes, SlashCommandBuilder } from 'discord.js';
import { GoogleGenAI } from '@google/genai';

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
  ],
});

const ai = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY,
});

const MODEL = process.env.GEMINI_MODEL || 'gemini-2.5-flash';
const DATA_DIR = path.join(process.cwd(), 'data');
const SETTINGS_FILE = path.join(DATA_DIR, 'settings.json');
const MEMORY_FILE = path.join(DATA_DIR, 'memory.json');

const BASE_SYSTEM_PROMPT = `
أنت مساعد داخل ديسكورد.
تكلم بالعربية الطبيعية وبأسلوب بشري ودود ومختصر.
لا تذكر أنك روبوت إلا إذا سُئلت مباشرة.
لا تكثر الكلام بلا حاجة.
إذا كانت الرسالة غامضة، اسأل سؤالًا واحدًا فقط للتوضيح.
`.trim();

async function ensureFiles() {
  await fs.mkdir(DATA_DIR, { recursive: true });

  try {
    await fs.access(SETTINGS_FILE);
  } catch {
    await fs.writeFile(SETTINGS_FILE, JSON.stringify({}, null, 2), 'utf8');
  }

  try {
    await fs.access(MEMORY_FILE);
  } catch {
    await fs.writeFile(MEMORY_FILE, JSON.stringify({}, null, 2), 'utf8');
  }
}

async function readJson(file, fallback = {}) {
  await ensureFiles();
  try {
    const raw = await fs.readFile(file, 'utf8');
    return raw.trim() ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

async function writeJson(file, data) {
  await ensureFiles();
  await fs.writeFile(file, JSON.stringify(data, null, 2), 'utf8');
}

async function getGuildSettings(guildId) {
  const all = await readJson(SETTINGS_FILE, {});
  return all[guildId] ?? { enabledChannels: [], persona: '' };
}

async function setGuildSettings(guildId, settings) {
  const all = await readJson(SETTINGS_FILE, {});
  all[guildId] = settings;
  await writeJson(SETTINGS_FILE, all);
}

async function getChannelMemory(channelId) {
  const all = await readJson(MEMORY_FILE, {});
  return all[channelId] ?? [];
}

async function pushChannelMemory(channelId, message) {
  const all = await readJson(MEMORY_FILE, {});
  const history = all[channelId] ?? [];
  history.push(message);
  all[channelId] = history.slice(-12);
  await writeJson(MEMORY_FILE, all);
}

async function resetChannelMemory(channelId) {
  const all = await readJson(MEMORY_FILE, {});
  delete all[channelId];
  await writeJson(MEMORY_FILE, all);
}

function splitDiscordMessage(text, limit = 2000) {
  const parts = [];
  let remaining = text.trim();

  while (remaining.length > limit) {
    let cut = remaining.lastIndexOf('\n', limit);
    if (cut < limit * 0.5) cut = remaining.lastIndexOf(' ', limit);
    if (cut < 1) cut = limit;

    parts.push(remaining.slice(0, cut).trim());
    remaining = remaining.slice(cut).trim();
  }

  if (remaining) parts.push(remaining);
  return parts;
}

async function generateReply({ persona = '', history = [], prompt }) {
  const systemInstruction = persona
    ? `${BASE_SYSTEM_PROMPT}\n\nشخصية السيرفر:\n${persona}`
    : BASE_SYSTEM_PROMPT;

  const contents = [
    ...history,
    { role: 'user', parts: [{ text: prompt }] },
  ];

  const response = await ai.models.generateContent({
    model: MODEL,
    contents,
    config: {
      systemInstruction,
      temperature: 0.8,
      maxOutputTokens: 500,
    },
  });

  return (response.text || '').trim();
}

const aiCommand = new SlashCommandBuilder()
  .setName('ai')
  .setDescription('إدارة البوت الذكي')
  .addSubcommand(sub => sub.setName('on').setDescription('تفعيل الردود في هذه القناة'))
  .addSubcommand(sub => sub.setName('off').setDescription('إيقاف الردود في هذه القناة'))
  .addSubcommand(sub =>
    sub
      .setName('persona')
      .setDescription('تغيير شخصية البوت في هذا السيرفر')
      .addStringOption(opt =>
        opt
          .setName('text')
          .setDescription('اكتب وصف الشخصية')
          .setRequired(true)
      )
  )
  .addSubcommand(sub => sub.setName('status').setDescription('عرض حالة الإعدادات'))
  .addSubcommand(sub => sub.setName('reset').setDescription('مسح ذاكرة هذه القناة'));

async function deployCommands() {
  const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN);
  await rest.put(
    Routes.applicationGuildCommands(process.env.CLIENT_ID, process.env.GUILD_ID),
    { body: [aiCommand.toJSON()] }
  );
  console.log('Slash commands deployed.');
}

client.once(Events.ClientReady, async c => {
  console.log(`Logged in as ${c.user.tag}`);
  try {
    await deployCommands();
  } catch (err) {
    console.error('Failed to deploy commands:', err);
  }
});

client.on(Events.InteractionCreate, async interaction => {
  try {
    if (!interaction.isChatInputCommand()) return;
    if (interaction.commandName !== 'ai') return;

    const guildId = interaction.guildId;
    const channelId = interaction.channelId;
    const sub = interaction.options.getSubcommand();

    const settings = await getGuildSettings(guildId);

    if (sub === 'on') {
      settings.enabledChannels ??= [];
      if (!settings.enabledChannels.includes(channelId)) {
        settings.enabledChannels.push(channelId);
      }
      await setGuildSettings(guildId, settings);
      return interaction.reply({ content: 'تم تفعيل الردود في هذه القناة.', ephemeral: true });
    }

    if (sub === 'off') {
      settings.enabledChannels ??= [];
      settings.enabledChannels = settings.enabledChannels.filter(id => id !== channelId);
      await set
