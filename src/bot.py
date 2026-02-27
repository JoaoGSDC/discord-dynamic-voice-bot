import asyncio
import logging
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


@bot.event
async def on_disconnect():
    logger.warning("Bot desconectado")

@bot.event
async def on_error(event, *args, **kwargs):
    logger.error(f"Erro no evento {event}: {args} {kwargs}")

def main():
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN não configurado! Configure no arquivo .env")
        return

    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            bot.run(DISCORD_TOKEN, reconnect=True)
            break
        except discord.LoginFailure:
            logger.error("Token inválido. Verifique o DISCORD_TOKEN no .env")
            break
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = getattr(e, 'retry_after', 60)
                logger.warning(f"Rate limit atingido (429). Aguardando {retry_after} segundos...")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(retry_after)
                    continue
                else:
                    logger.error("Muitas tentativas de reconexão após rate limit. Encerrando.")
                    break
            else:
                logger.error(f"Erro HTTP {e.status}: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = min(2 ** retry_count, 60)
                    logger.info(f"Aguardando {wait_time} segundos antes de tentar novamente...")
                    time.sleep(wait_time)
                else:
                    break
        except discord.RateLimited as e:
            retry_after = getattr(e, 'retry_after', 60)
            logger.warning(f"Rate limit atingido. Aguardando {retry_after} segundos...")
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(retry_after)
                continue
            else:
                logger.error("Muitas tentativas após rate limit. Encerrando.")
                break
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate limit" in error_msg.lower():
                logger.warning("Rate limit detectado. Aguardando 60 segundos...")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(60)
                    continue
                else:
                    logger.error("Muitas tentativas após rate limit. Encerrando.")
                    break
            else:
                logger.error(f"Erro ao iniciar o bot: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = min(2 ** retry_count, 60)
                    logger.info(f"Aguardando {wait_time} segundos antes de tentar novamente...")
                    time.sleep(wait_time)
                else:
                    logger.error("Muitas tentativas. Encerrando.")
                    break


if __name__ == "__main__":
    main()
