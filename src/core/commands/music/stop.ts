import { SlashCommand } from "@/structures/commands/SlashCommand.js";
import { createEmptyEmbed } from "@/utils/tools.js";


export default new SlashCommand()
    .setName("stop")
    .setDescription("Detiene y borra la cola de reprodución")
    .setCategory("Music")
    .setExecute(async (client, interaction) => {
        const guildID = interaction.guildId;
        const player = client.getPlayer(guildID);
        const embErr = createEmptyEmbed()
            .setDescription("No hay nada que parar de reproducir, utiliza /play para agregar canciones")
            .setColor("Red");

        if (!player?.queue.current) return await interaction.reply({ embeds: [embErr] })

        const StopedSong = player.queue.current
        await player.stopPlaying(false)

        setTimeout(() => {
            const player = client.getPlayer(guildID);
            if (player && player.queue.tracks.length === 0) {
                player.disconnect()
            }
        }, 15000)

        await interaction.reply({
            embeds: [
                createEmptyEmbed()
                    .setAuthor({ iconURL: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Stop_it.jpg/603px-Stop_it.jpg", name: "Se a detenido la reprodución" })
                    .setDescription(`De ${StopedSong.info.title}`)
                    .setColor("Green")
            ]
        })
    })