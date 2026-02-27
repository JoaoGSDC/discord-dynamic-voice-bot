import logging
import sys
import time
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

cleanup_task_started = False


def create_bot():
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        global cleanup_task_started
        logger.info(f"Bot conectado como {bot.user} (ID: {bot.user.id})")
        logger.info(f"Conectado em {len(bot.guilds)} servidor(es)")

        for guild in bot.guilds:
            await setup_dynamic_voice_async(guild)

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

    @bot.event
    async def on_disconnect():
        logger.warning("Bot desconectado")

    @bot.event
    async def on_error(event, *args, **kwargs):
        logger.error(f"Erro no evento {event}: {args} {kwargs}")

    return bot


def main():
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN não configurado! Configure no arquivo .env")
        return 1

    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        bot = create_bot()
        try:
            bot.run(DISCORD_TOKEN, reconnect=True)
            return 0
        except discord.LoginFailure:
            logger.error("Token inválido. Verifique o DISCORD_TOKEN no .env")
            return 1
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = getattr(e, 'retry_after', 60)
                logger.warning(f"Rate limit (429). Aguardando {retry_after}s...")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(retry_after)
                    continue
                logger.error("Muitas tentativas após rate limit.")
                return 1
            logger.error(f"Erro HTTP {e.status}: {e}")
            retry_count += 1
            if retry_count < max_retries:
                wait_time = min(2 ** retry_count, 60)
                logger.info(f"Aguardando {wait_time}s...")
                time.sleep(wait_time)
                continue
            return 1
        except Exception as e:
            error_msg = str(e).lower()
            if "session is closed" in error_msg or "429" in str(e):
                logger.warning(f"Erro de conexão: {e}. Saindo para reinício limpo.")
                sys.exit(1)
            logger.error(f"Erro ao iniciar o bot: {e}")
            retry_count += 1
            if retry_count < max_retries:
                wait_time = min(2 ** retry_count, 60)
                logger.info(f"Aguardando {wait_time}s...")
                time.sleep(wait_time)
                continue
            return 1

    return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
