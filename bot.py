import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
from discord import app_commands, Intents, Interaction
import random
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

# Configuración de intents para el bot
intents = Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.guilds = True

# Inicialización del bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Configuración del árbol de comandos
tree = bot.tree

# Configuración de yt_dlp para transmisión
ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'extract_flat': False,
    'force_generic_extractor': True,
}
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
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
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

# Evento cuando el bot está listo
@bot.event
async def on_ready():
    print(f"[INFO] Conectado como {bot.user}")
    try:
        # Sincronización global de comandos
        await tree.sync()
        print("[INFO] Comandos sincronizados exitosamente.")
    except Exception as e:
        print(f"[ERROR] Error al sincronizar comandos: {e}")

# Comando para conectar el bot
@bot.command(name="join")
async def join(ctx):
    """Conecta el bot al canal de voz"""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None or not ctx.voice_client.is_connected():
            try:
                await channel.connect()
                await ctx.send(f"Conectado a {channel}.")
            except Exception as e:
                await ctx.send(f"Error al conectar al canal: {e}")
        else:
            await ctx.send("Ya estoy conectado a un canal de voz.")
    else:
        await ctx.send("¡Debes estar en un canal de voz para usar este comando!")

# Comando para reproducir música
@bot.command(name="play")
async def play(ctx, *, url):
    """Reproduce música de YouTube"""
    if ctx.voice_client is None:
        await ctx.invoke(join)

    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    async with ctx.typing():
        try:
            player = await YTDLSource.from_url(url, loop=bot.loop)
            ctx.voice_client.play(player, after=lambda e: print(f"Error: {e}") if e else None)
            await ctx.send(f"Reproduciendo: **{player.title}**")
        except Exception as e:
            await ctx.send(f"Error al reproducir la música: {str(e)}")

# Comando para desconectar al bot
@bot.command(name="leave")
async def leave(ctx):
    """Desconecta el bot del canal de voz"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Me he desconectado del canal de voz.")
    else:
        await ctx.send("No estoy conectado a ningún canal de voz.")

# Comando para detener la música
@bot.command(name="stop")
async def stop(ctx):
    """Detiene la música y limpia la cola"""
    if ctx.voice_client:
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("La música se ha detenido.")
        else:
            await ctx.send("No hay música reproduciéndose actualmente.")
    else:
        await ctx.send("El bot no está conectado a un canal de voz.")

# Comando de motivación
mensajes_motivacion = [
    "¡Eres increíble y capaz de lograr todo lo que te propongas!",
    "Nunca te rindas. El éxito está a solo un paso de distancia.",
    "Cada día es una nueva oportunidad para mejorar.",
    "Confía en ti mismo, tienes el potencial para lograr cosas asombrosas.",
    "El fracaso es solo una oportunidad para comenzar de nuevo con más experiencia.",
    "Recuerda: los grandes logros requieren tiempo y esfuerzo.",
    "Sigue adelante, incluso cuando sea difícil. ¡Puedes hacerlo!",
    "La única manera de lograrlo es intentándolo. ¡Hazlo ahora!",
    "El futuro pertenece a aquellos que creen en la belleza de sus sueños.",
    "Eres más fuerte de lo que piensas."
]

@tree.command(name="motivame", description="¡Recibe un mensaje de motivación!")
async def motiva(interaction: Interaction):
    mensaje = random.choice(mensajes_motivacion)
    await interaction.response.send_message(mensaje)

# Arranque del bot con el token visible
bot.run("MTIzMTU0MDU3MDM0NzAxMjEyNg.Gw3g_2.DDPhE2mysKl76aBHVhqMomXO8Q0QCpl0jieqW0")
