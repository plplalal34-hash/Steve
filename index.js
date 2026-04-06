import { SlashCommandBuilder } from 'discord.js';

export const data = new SlashCommandBuilder()
  .setName('ai')
  .setDescription('إدارة البوت الذكي')
  .addSubcommand(sub =>
    sub.setName('on').setDescription('تفعيل الردود في هذه القناة')
  )
  .addSubcommand(sub =>
    sub.setName('off').setDescription('إيقاف الردود في هذه القناة')
  )
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
  .addSubcommand(sub =>
    sub.setName('status').setDescription('عرض حالة الإعدادات')
  )
  .addSubcommand(sub =>
    sub.setName('reset').setDescription('مسح ذاكرة هذه القناة')
  );

export async function execute(interaction, helpers) {
  const { getGuildSettings, setGuildSettings, resetChannelMemory } = helpers;

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
    return interaction.reply({
      content: 'تم تفعيل الردود في هذه القناة.',
      ephemeral: true,
    });
  }

  if (sub === 'off') {
    settings.enabledChannels ??= [];
    settings.enabledChannels = settings.enabledChannels.filter(id => id !== channelId);
    await setGuildSettings(guildId, settings);
    return interaction.reply({
      content: 'تم إيقاف الردود في هذه القناة.',
      ephemeral: true,
    });
  }

  if (sub === 'persona') {
    const text = interaction.options.getString('text', true);
    settings.persona = text;
    await setGuildSettings(guildId, settings);
    return interaction.reply({
      content: 'تم حفظ شخصية البوت.',
      ephemeral: true,
    });
  }

  if (sub === 'status') {
    const enabled = settings.enabledChannels?.includes(channelId) ? 'مفعلة' : 'غير مفعلة';
    const persona = settings.persona || 'لم يتم تحديد شخصية بعد.';
    return interaction.reply({
      content: `الحالة الحالية:\n- هذه القناة: ${enabled}\n- الشخصية: ${persona}`,
      ephemeral: true,
    });
  }

  if (sub === 'reset') {
    await resetChannelMemory(channelId);
    return interaction.reply({
      content: 'تم مسح ذاكرة هذه القناة.',
      ephemeral: true,
    });
  }
}
