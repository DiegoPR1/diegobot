import random
from discord.ext import commands
from discord import app_commands, Intents, Interaction

# Configuración inicial del bot
intents = Intents.default()
intents.messages = True
intents.message_content = True
intents.dm_messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents, application_id="1231540570347012126")

# Configuración del árbol de comandos
tree = bot.tree

# Evento cuando el bot está listo
@bot.event
async def on_ready():
    print(f"[INFO] Conectado como {bot.user}")
    try:
        # Sincronización global de comandos, incluyendo en DMs
        await tree.sync()
        print("[INFO] Comandos sincronizados exitosamente.")
    except Exception as e:
        print(f"[ERROR] Error al sincronizar comandos: {e}")

# Comando para jugar "Adivina el número"
@tree.command(name="adivina", description="¡Juega a adivinar un número!")
async def adivina(interaction: Interaction):
    numero_secreto = random.randint(1, 100)

    await interaction.response.send_message(
        "¡Estoy pensando en un número entre 1 y 100! Intenta adivinarlo.", ephemeral=False
    )

    def check(m):
        return m.author == interaction.user and m.content.isdigit()

    intentos = 0
    while True:
        try:
            mensaje = await bot.wait_for("message", check=check, timeout=30.0)
            intentos += 1
            adivina = int(mensaje.content)

            if adivina < numero_secreto:
                await interaction.followup.send("El número es más alto. Intenta otra vez.", ephemeral=True)
            elif adivina > numero_secreto:
                await interaction.followup.send("El número es más bajo. Intenta otra vez.", ephemeral=True)
            else:
                await interaction.followup.send(f"🎉 ¡Correcto! El número era {numero_secreto}. Lo adivinaste en {intentos} intentos.", ephemeral=False)
                break
        except Exception:
            await interaction.followup.send("⏳ Se acabó el tiempo. ¡Mejor suerte la próxima vez!", ephemeral=True)
            break

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

# Ejecutar el bot
bot.run("MTIzMTU0MDU3MDM0NzAxMjEyNg.Gw3g_2.DDPhE2mysKl76aBHVhqMomXO8Q0QCpl0jieqW0")
