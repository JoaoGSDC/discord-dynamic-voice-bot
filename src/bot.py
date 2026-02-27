import logging
import discord
from discord.ext import commands

from .config import DISCORD_TOKEN, TRIGGER_CHANNEL_NAME
from .dynamic_voice import (
    setup_dynamic_voice_async,
    create_temporary_channel,
    delete_if_empty,
    start_cleanup_task,
    temporary_channels,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("bot")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)
cleanup_task_started = False


@bot.event
async def on_ready():
    logger.info(f"Bot conectado como {bot.user} (ID: {bot.user.id})")
    logger.info(f"Conectado em {len(bot.guilds)} servidor(es)")

    for guild in bot.guilds:
        await setup_dynamic_voice_async(guild)

    global cleanup_task_started
    if not cleanup_task_started:
        start_cleanup_task(bot)
        cleanup_task_started = True
        logger.info("Task de limpeza preventiva iniciada (intervalo: 1 hora)")


@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.channel.name == TRIGGER_CHANNEL_NAME:
        logger.info(f"{member.display_name} entrou no canal '{TRIGGER_CHANNEL_NAME}'")
        await create_temporary_channel(member, after.channel)
        return

    if before.channel and before.channel.id in temporary_channels:
        logger.info(f"{member.display_name} saiu da sala {before.channel.name}")
        await delete_if_empty(before.channel)


def main():
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN não configurado! Configure no arquivo .env")
        return

    try:
        bot.run(DISCORD_TOKEN)
    except discord.LoginFailure:
        logger.error("Token inválido. Verifique o DISCORD_TOKEN no .env")
    except Exception as e:
        logger.error(f"Erro ao iniciar o bot: {e}")


if __name__ == "__main__":
    main()
