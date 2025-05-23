import { SlashCommandBuilder } from 'discord.js';
import { Command } from '../../class/Commands.js';

import { PlaybackStrategy } from '../../class/commands/PlaybackStrategy.js';
import { Player, Track } from 'lavalink-client/dist/types/index.js';
import logger from '../../class/logger.js';

class PlayNext extends PlaybackStrategy {
    override async addTracks(player: Player, tracks: Track | Track[]): Promise<void> {
        await player.queue.add(tracks, 0)
    }
}

const playnext = new PlayNext()

export default new Command(
    {
        data: {
            command: new SlashCommandBuilder()
                .setName("playnext")
                .setDescription("Agrega una canción que se reproducirá después de la actual. Compatible con YouTube, Spotify y más.")
                .addStringOption(
                    o => o
                        .setName("busqueda")
                        .setDescription("Que ponemos chee?")
                        .setAutocomplete(true)
                        .setRequired(true))
                .addStringOption(
                    o => o.setName("fuente")
                        .setDescription("Desde que fuente quieres reproducir?")
                        .setRequired(false)
                        .setChoices(
                            { name: "Youtube", value: "ytsearch" }, // Requires plugin on lavalink: https://github.com/lavalink-devs/youtube-source
                            { name: "Youtube Music", value: "ytmsearch" }, // Requires plugin on lavalink: https://github.com/lavalink-devs/youtube-source
                            { name: "Spotify", value: "spsearch" }, // Requires plugin on lavalink: https://github.com/topi314/LavaSrc
                            // { name: "Soundcloud", value: "scsearch" },
                            // { name: "Deezer", value: "dzsearch" }, // Requires plugin on lavalink: https://github.com/topi314/LavaSrc
                            // { name: "Apple Music", value: "amsearch" }, // Requires plugin on lavalink: https://github.com/topi314/LavaSrc
                            // { name: "Bandcamp", value: "bcsearch" },
                            // { name: "Cornhub", value: "phsearch" },
                        )),
            category: 'Music'
        },
        execute: async (client, inter) => {
            try {
                await playnext.execute(client, inter)
            } catch (err) {
                logger.error(`[Playnext Command] ${err}`)
            }
        },
        autocomplete: async (client, inter) => {
            try {
                await playnext.autocomplete(client, inter)
            } catch (err) {
                logger.error(`[Playnext Command] ${err}`)
            }
        }
    }
);