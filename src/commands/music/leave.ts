import { Channel, SlashCommandBuilder, VoiceChannel } from "discord.js";
import { Command } from "../../class/Commands.js";
import logger from "../../class/logger.js";

export default new Command({
    data: {
        command: new SlashCommandBuilder()
            .setName("leave")
            .setDescription("Me desconecta del canal de voz"),
        category: "Music"
    },

    execute: async (client, interaction) => {
        if (!interaction.guildId) return;

        const guildID = interaction.guildId;
        const player = client.Tools.getPlayer(guildID);

        const embErr = client.Tools.createEmbedTemplate()
            .setDescription("No estoy conectado a ningun canal, utiliza /play para agregar canciones.")
            .setColor("Red");

        if (!player || !player.connected) return interaction.reply({ embeds: [embErr] })

        const channel = client.channels.cache.get(player.voiceChannelId!) as VoiceChannel | undefined;

        // player.disconnect()
        await player.destroy("Destoyed by Inactivity", true)
            .then(async () => {
                await interaction.reply({
                    embeds: [
                        client.Tools.createEmbedTemplate()
                            .setDescription(`Me desconecte del canal de voz \`${channel ? channel.name : "Channel not found"}\``)
                            .setColor("Green")
                    ]
                })
            })
            .catch((err) => {
                if (err instanceof Error) {
                    logger.error(err)
                    logger.error(`Stack Trace: ${err.stack}`);
                } else {
                    logger.error('Ocurrió un error desconocido al registrar los comandos');
                }
            })




    }
})