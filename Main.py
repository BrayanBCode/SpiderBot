import os, sys, re, asyncio, discord
from discord.ext import commands
from discord import Embed, FFmpegPCMAudio, Activity, ActivityType, Status
from youtubesearchpython import VideosSearch
from pytube import Playlist, YouTube

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix = "=", intents=intents, help_command=None)

Servidores_PlayList = {}
inactive_timers = {}
CurrentlyPlaying = {}
ActiveLoop = {}

def clearMusicFolder():
    archivos = os.listdir('./Musica')
    if archivos:
        for archivo in archivos:
            try:                
                os.remove(os.path.join('./Musica', archivo))
                print(f"Archivo '{archivo}' eliminado correctamente.")
            except Exception as e:
                continue  # Pasar al siguiente archivo si no se puede eliminar

async def addListServer(guild):
    global Servidores_PlayList
    Servidores_PlayList[guild.id] = []

def check_folder_contents():
    folder_path = './Musica'  # Ruta a la carpeta

    # Lista los archivos en la carpeta
    files_in_folder = os.listdir(folder_path)

    # Comprueba si hay algún archivo en la carpeta
    if files_in_folder:
        print("La carpeta contiene archivos.")
        return True
    else:
        print("La carpeta está vacía.")
        return False
    
@bot.command() #Reinicia el bot con un comando
async def restart(ctx):
    await ctx.send('Reiniciando...')
    os.execv(sys.executable, ['python'] + ['"{}"'.format(arg) for arg in sys.argv])

@bot.command()
async def help(ctx):
    
    embed = Embed(title="Guia de de comandos", description="En esta guia se nombraran los comandos implementados en el Bot.", color=0x7289DA)
    embed.add_field(name=f"**{bot.command_prefix}play**", value=f"Para reproducir música, simplemente escribe **{bot.command_prefix}play** seguido del nombre de la canción, el artista o la URL de la canción que desees escuchar.", inline=False)
    embed.add_field(name=f"**{bot.command_prefix}stop**", value=f"Para pausar la musica utilize **{bot.command_prefix}stop** una vez para reanudar la musica utilize **{bot.command_prefix}stop** nuevamente", inline=False)
    embed.add_field(name=f"**{bot.command_prefix}skip**", value=f"Para saltear una cancion utilize **{bot.command_prefix}skip**, para saltear varias agrege un numero, ejemplo: **{bot.command_prefix}skip 3**", inline=False)
    embed.add_field(name=f"**{bot.command_prefix}queue**", value=f"Muestra la playlist y la cancion que se esta reproduciendo actualmente", inline=False)
    embed.add_field(name=f"**{bot.command_prefix}remove**", value=f"Quita de la playlist la cancion que el usuario desee ejemplo: **{bot.command_prefix}remove 5**", inline=False)
    embed.add_field(name=f"**{bot.command_prefix}clear**", value=f"Limpia la playlist", inline=False)
    #embed.add_field(name=f"**{bot.command_prefix}loop**", value=" ", inline=False)
    #embed.add_field(name=f"**{bot.command_prefix}clear**", value=" ", inline=False)

    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f"Ya estoy activo {bot.user} al servicio")
    
    await startup()


async def startup():

    status = 12

    if status == 1:
        custom_status = Activity(name='Music Player "=help"', type=ActivityType.playing)
        await bot.change_presence(status=Status.online, activity=custom_status)
        
    else:
        custom_status = Activity(name="Fuera de Servicio", type=ActivityType.playing)
        await bot.change_presence(activity=custom_status, status=Status.do_not_disturb)

    ids_servidores = bot.guilds
    for servidor_id in ids_servidores:
        Servidores_PlayList[servidor_id.id] = []
        ActiveLoop[servidor_id.id] = False

@bot.command()
async def loop(ctx):
    GuildActual = ctx.guild.id
    ActiveLoop[GuildActual] = not ActiveLoop[GuildActual]
    Status = 'Activado' if ActiveLoop[GuildActual] else 'Desactivado'
    await ctx.send(f"Loop: {Status}")

@bot.command()
async def remove(ctx, command):
    try:
        command = int(command)
        
        GuildActual = ctx.guild.id

        if len(Servidores_PlayList[GuildActual]) == 1 and command == 1:
            video = YouTube(Servidores_PlayList[GuildActual][command])
            Servidores_PlayList[GuildActual].pop(command - 1)
            return
        
        video = YouTube(Servidores_PlayList[GuildActual][command - 1])
        Servidores_PlayList[GuildActual].pop(command - 1)
        duartion = video.length
        mins, secs = divmod(duartion, 60)
        hours, mins = divmod(mins, 60)
        duration_formatted = '{:02d}:{:02d}:{:02d}'.format(hours, mins, secs)

        embed = Embed(title="Cancion removida", color=0x7289DA)
        thumbnail = video.thumbnail_url
        embed.set_thumbnail(url=thumbnail)
        embed.add_field(name="Canción eliminada", value=f"[{video.title}] | [{video.author}]")
        embed.add_field(name="Duración", value=duration_formatted)

        await ctx.send(embed=embed)
    except (ValueError, IndexError):
        print("command no es un int o es un índice inválido")
        await ctx.send("Por favor, proporciona un número válido para remover una canción.")

@bot.command()
async def clear(ctx):
    GuildActual = ctx.guild.id
    if GuildActual in Servidores_PlayList and len(Servidores_PlayList[GuildActual]) > 0:
        Servidores_PlayList[GuildActual].clear()
        await ctx.send(f"Playlist borrada con exito.")
    else:
        await ctx.send(f"Error: La playlist esta vacia")

# Esta función verificará si el bot está inactivo en un canal de voz durante 2 minutos y lo desconectará
async def check_voice_activity(guild):
    while True:
        voice_client = guild.voice_client

        if voice_client and voice_client.channel:
            # Verificar si el bot está solo en el canal de voz
            if len(voice_client.channel.members) == 1 and voice_client.channel.members[0] == guild.me:
                await asyncio.sleep(120)  # Esperar 2 minutos para verificar la inactividad
                if len(voice_client.channel.members) == 1 and voice_client.channel.members[0] == guild.me:
                    await voice_client.disconnect()
                    print(f"El bot ha sido desconectado del canal de voz en '{guild.name}' debido a la inactividad.")
                    if check_folder_contents():
                        clearMusicFolder()
                    # Verificar si la clave existe antes de intentar eliminarla
                    if guild.id in inactive_timers:
                        inactive_timers.pop(guild.id)  # Eliminar el temporizador de inactividad para este servidor
        await asyncio.sleep(10)  # Verificar la inactividad cada 10 segundos

@bot.event # Ejecutar la función cuando el bot se una a un canal de voz en un servidor
async def on_voice_state_update(member, before, after):
    if member == bot.user and after.channel:
        afterguild = after.channel.guild

        if afterguild.id not in inactive_timers:
            inactive_timers[afterguild.id] = bot.loop.create_task(check_voice_activity(afterguild))
    try:
        beforeguild = before.channel.guild
        if before.channel and not after.channel and member == bot.user:  # Se desconectó de un canal de voz
            Servidores_PlayList[beforeguild.id].clear()  # Borrar la lista de reproducción del servidor
            print(f"La lista de reproducción para el servidor {beforeguild.name} ha sido limpiada.")
    except:
        print(f"Evento de Voz detectado - Usuario: {member}")

@bot.command()
async def skip(ctx, num=None):
    GuildActual = ctx.guild.id
    voice_client = ctx.guild.voice_client

    if num is None:
        num = 1

    if num == 1:
        voice_client.stop()
        await play_next(ctx)
        return
    
    try:
        num = int(num)
    except ValueError:
        await ctx.send("Por favor, proporciona un número válido de canciones para saltar.")
        return

    if num < 1:
        await ctx.send("Por favor, proporciona un número positivo de canciones para saltar.")
        return

    for _ in range(num-1):
        if len(Servidores_PlayList[GuildActual]) > 0:
            voice_client.stop()
            Servidores_PlayList[GuildActual].pop(0)
        else:
            await ctx.send("No hay más canciones en la lista de reproducción para saltar.")
            break

    if voice_client.is_playing() or voice_client.is_paused():
        await play_next(ctx)
    
@bot.command()
async def queue(ctx):
    GuildActual = ctx.guild.id
    if GuildActual in Servidores_PlayList:
        songs = Servidores_PlayList[GuildActual]

        if len(songs) > 0:
            max_videos_to_display = 5  # Número máximo de videos para mostrar en una página
            total_duration = sum(YouTube(song_url).length for song_url in songs)  # Duración total de la lista de reproducción en segundos

            total_mins, total_secs = divmod(total_duration, 60)
            total_hours, total_mins = divmod(total_mins, 60)
            total_duration_formatted = '{:02d}:{:02d}:{:02d}'.format(total_hours, total_mins, total_secs)

            embed = Embed(title="Lista de Reproducción", color=0x6a0dad)
            embed.set_footer(text=f"Duración total de la lista de reproducción: {total_duration_formatted}")

            message = None
            page = 1

            async def show_queue():
                nonlocal message, page

                start_idx = (page - 1) * max_videos_to_display
                end_idx = page * max_videos_to_display
                songs_to_display = songs[start_idx:end_idx]

                embed.clear_fields()

                for idx, song_url in enumerate(songs_to_display, start=start_idx + 1):
                    video = YouTube(song_url)
                    duration = video.length
                    mins, secs = divmod(duration, 60)
                    hours, mins = divmod(mins, 60)
                    duration_formatted = '{:02d}:{:02d}:{:02d}'.format(hours, mins, secs)

                    embed.add_field(
                        name=f"{idx}. [{video.title}] | [{video.author}]",
                        value=f"Duración: {duration_formatted}\n[Ver en YouTube]({song_url})",
                        inline=False
                    )

                embed.set_footer(text=f"Página {page} - Duración total de la lista de reproducción: {total_duration_formatted}")

                if message:
                    await message.edit(embed=embed)
                else:
                    message = await ctx.send(embed=embed)

                if len(songs) > max_videos_to_display:
                    await message.add_reaction('◀️')  # Flecha izquierda
                    await message.add_reaction('▶️')  # Flecha derecha

                    def check(reaction, user):
                        return user == ctx.author and str(reaction.emoji) in ['◀️', '▶️']

                    while True:
                        try:
                            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)

                            if str(reaction.emoji) == '▶️' and end_idx < len(songs):
                                page += 1
                            elif str(reaction.emoji) == '◀️' and start_idx > 0:
                                page -= 1

                            await reaction.remove(user)
                            await show_queue()

                        except asyncio.TimeoutError:
                            break

            await show_queue()

        else:
            embed = Embed(description="La lista de reproducción está vacía.", color=0x6a0dad)
            await ctx.send(embed=embed)
    else:
        await ctx.send("No hay lista de reproducción para este servidor.")

@bot.command()
async def stop(ctx):
    voice_client = ctx.guild.voice_client

    if voice_client.is_playing():
        voice_client.pause()
        await ctx.send("Canción pausada")
    elif voice_client.is_paused():
        voice_client.resume()
        await ctx.send("Canción reanudada")
    else:
        await ctx.send("No hay ninguna canción en reproducción para pausar o reanudar.")

@bot.command()
async def play(ctx, *, command):
    await AddSongs(ctx, command)

@bot.command()
async def p(ctx, *, command):
    await AddSongs(ctx, command)

@bot.command()
async def AddSongs(ctx, command):
    voice_client = ctx.guild.voice_client
    channel = ctx.author.voice.channel
    GuildActual = ctx.guild
    print(f'\nComando emitido por [{ctx.author.name}] en ({ctx.guild.name}) - command: {bot.command_prefix}play {command}\n')

    clearMusicFolder()
    songs_added = []

    if channel:  # Verifica si el canal es válido
        voice_client = ctx.guild.voice_client
            
        if voice_client:  # Si el bot ya está en un canal, muévelo si es necesario
            await voice_client.move_to(channel)
        else:  # Si el bot no está en un canal, conéctalo al canal
            try:
                voice_client = await channel.connect()
            except Exception as e:
                print(f'Error al conectar al canal de voz: {e}')
                return

        url_pattern = r'(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[^\s]+)'
        urls = re.findall(url_pattern, command)

        if GuildActual.id not in Servidores_PlayList:
            await addListServer(GuildActual)

        if urls:           
            for url in urls:
                if 'list' in url.lower():
                    playlist = Playlist(url)
                    for video_url in playlist.video_urls:
                        video = YouTube(video_url)
                        Servidores_PlayList[GuildActual.id].append((video_url))

                        # Obtener la duración del video
                        duration = video.length
                        mins, secs = divmod(duration, 60)
                        hours, mins = divmod(mins, 60)
                        duration_formatted = '{:02d}:{:02d}:{:02d}'.format(hours, mins, secs)

                        # Obtener la miniatura del video
                        thumbnail = video.thumbnail_url

                        songs_added.append({
                            'title': video.title,
                            'duration': duration_formatted,
                            'thumbnail': thumbnail,
                            'artist': video.author
                        })
                else:                    
                    video = YouTube(url)
                    Servidores_PlayList[GuildActual.id].append((url))

                    duration = video.length
                    mins, secs = divmod(duration, 60)
                    hours, mins = divmod(mins, 60)
                    duration_formatted = '{:02d}:{:02d}:{:02d}'.format(hours, mins, secs)

                    thumbnail = video.thumbnail_url

                    songs_added.append({
                        'title': video.title,
                        'duration': duration_formatted,
                        'thumbnail': thumbnail,
                        'artist': video.author
                    })

        else:
            videos = VideosSearch(command, limit = 1)
            results = videos.result()

            if len(results['result']) > 0:
                video_url = results['result'][0]['link']
                video = YouTube(video_url)
                Servidores_PlayList[GuildActual.id].append((video_url))
                
                duration = video.length
                mins, secs = divmod(duration, 60)
                hours, mins = divmod(mins, 60)
                duration_formatted = '{:02d}:{:02d}:{:02d}'.format(hours, mins, secs)

                thumbnail = video.thumbnail_url

                songs_added.append({
                    'title': video.title,
                    'duration': duration_formatted,
                    'thumbnail': thumbnail,
                    'artist': video.author
                })
            else:
                ctx.send('No se encontraron busquedas validas.')
                return
            
        if check_folder_contents():
            last_song = songs_added[-1]
            embed = Embed(title="Canción agregada a la playlist", color=0x6a0dad)
            embed.add_field(
                name=f"{last_song['title']} - {last_song['artist']}",
                value=f"Duración: {last_song['duration']}",
                inline=False
            )
            embed.set_thumbnail(url=last_song['thumbnail'])
            await ctx.send(embed=embed)

        
        # este if era un elif del de arriba
        elif len(songs_added) > 1:
            embed = Embed(title="Canciones agregadas a la playlist", color=0x6a0dad)
            for song in songs_added:
                embed.add_field(
                    name=f"{song['title']} - {song['artist']}",
                    value=f"Duración: {song['duration']}",
                    inline=False
                )
                embed.set_thumbnail(url=song['thumbnail'])

            await ctx.send(embed=embed)

        if not voice_client.is_playing():
            await play_next(ctx)

    else:
        await ctx.send("¡Debes estar en un canal de voz para reproducir música!")
    
    ##print(f'Lista de reproducción actual en Guild {GuildActual}: {Servidores_PlayList[GuildActual]}')


async def play_next(ctx):
    GuildActual = ctx.guild.id
    voice_client = ctx.voice_client

    if len(Servidores_PlayList[GuildActual]) > 0:
        if not voice_client.is_playing():
            video_url = Servidores_PlayList[GuildActual].pop(0)
            try:
                video = YouTube(video_url)
                best_audio = video.streams.get_audio_only()
                filename = best_audio.default_filename
                best_audio.download(filename=filename, output_path='Musica')

                audio_source = FFmpegPCMAudio(os.path.join('Musica', filename))
                voice_client.play(audio_source, after=lambda e: (
                    bot.loop.create_task(play_next(ctx)),
                    clearMusicFolder()
                ))

                # Enviar mensaje con la canción que está siendo reproducida
                duration = video.length
                mins, secs = divmod(duration, 60)
                hours, mins = divmod(mins, 60)
                duration_formatted = '{:02d}:{:02d}:{:02d}'.format(hours, mins, secs)

                embed = Embed(title="Reproduciendo", description=f"{video.title} - {video.author}\n[Ver en Youtube]({video_url})\nDuración: {duration_formatted}", color=0x6a0dad)

                embed.set_thumbnail(url=video.thumbnail_url)
                await ctx.send(embed=embed)

                CurrentlyPlaying[GuildActual] = {
                    'title': video.title,
                    'artist': video.author,
                    'duration': duration_formatted,
                    'url': video_url,
                    'thumbnail': video.thumbnail_url
                }

                await asyncio.sleep(30)
            except Exception as e:
                await ctx.send(f'Error al descargar la canción: {str(e)}')
                print(f'Error al descargar la canción: {str(e)}')
                


bot.run("")