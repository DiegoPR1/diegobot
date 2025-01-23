import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Opciones de youtube-dl/yt-dlp
ytdl_format_options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}
ffmpeg_options = {
    'options': '-vn',
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@bot.command(name="join")
async def join(ctx):
    """Conecta el bot al canal de voz"""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("¡Debes estar en un canal de voz para usar este comando!")

@bot.command(name="play")
async def play(ctx, *, url):
    """Reproduce música de YouTube"""
    if not ctx.voice_client:
        await ctx.invoke(join)

    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=bot.loop)
        ctx.voice_client.play(player, after=lambda e: print(f"Error: {e}") if e else None)
        await ctx.send(f"Reproduciendo: **{player.title}**")

@bot.command(name="leave")
async def leave(ctx):
    """Desconecta el bot del canal de voz"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("No estoy en ningún canal de voz.")

@bot.command(name="stop")
async def stop(ctx):
    """Detiene la música"""
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("La música se ha detenido.")
    else:
        await ctx.send("No hay nada que detener.")




bot.run("MTIzMTU0MDU3MDM0NzAxMjEyNg.Gw3g_2.DDPhE2mysKl76aBHVhqMomXO8Q0QCpl0jieqW0")
