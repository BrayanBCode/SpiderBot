import { ButtonInteraction, ChatInputCommandInteraction } from "discord.js";
import { Track, UnresolvedTrack } from "lavalink-client";

export interface IQueuePaginator {
    interaction: ChatInputCommandInteraction<"cached"> | ButtonInteraction<"cached">;
    items: (Track | UnresolvedTrack)[];
    pageSize?: number;
    time?: number;
}