import asyncio
import logging
import time
from discord import PermissionOverwrite

from .config import VOICE_CATEGORY_NAME, TRIGGER_CHANNEL_NAME, TEMP_CHANNEL_PREFIX

temporary_channels = {}
MAX_CHANNEL_AGE_SECONDS = 24 * 60 * 60

logger = logging.getLogger(__name__)


async def setup_dynamic_voice_async(guild):
    category = None
    for cat in guild.categories:
        if cat.name == VOICE_CATEGORY_NAME:
            category = cat
            break

    if not category:
        logger.warning(f"Categoria '{VOICE_CATEGORY_NAME}' não encontrada no servidor {guild.name}")
        return None

    trigger_channel = None
    for channel in guild.voice_channels:
        if channel.name == TRIGGER_CHANNEL_NAME and channel.category_id == category.id:
            trigger_channel = channel
            break

    if not trigger_channel:
        overwrites = {
            guild.default_role: PermissionOverwrite(
                view_channel=True,
                connect=True,
                speak=False,
            )
        }
        trigger_channel = await guild.create_voice_channel(
            TRIGGER_CHANNEL_NAME,
            category=category,
            overwrites=overwrites,
        )
        logger.info(f"Canal '{TRIGGER_CHANNEL_NAME}' criado na categoria '{VOICE_CATEGORY_NAME}'")

    return trigger_channel


async def create_temporary_channel(member, trigger_channel):
    guild = member.guild
    category = trigger_channel.category

    if not category:
        logger.error("Canal gatilho não possui categoria")
        return

    overwrites = {
        guild.default_role: PermissionOverwrite(
            view_channel=True,
            connect=True,
            speak=True,
        ),
        member: PermissionOverwrite(
            manage_channels=True,
            mute_members=True,
            deafen_members=True,
        ),
    }

    channel_name = f"{TEMP_CHANNEL_PREFIX} {member.display_name}"
    new_channel = await guild.create_voice_channel(
        channel_name,
        category=category,
        overwrites=overwrites,
    )

    temporary_channels[new_channel.id] = {
        "owner_id": member.id,
        "created_at": time.time(),
    }

    await member.move_to(new_channel)
    logger.info(f"Sala '{channel_name}' criada para {member.display_name} (ID: {new_channel.id})")


async def delete_if_empty(channel):
    await asyncio.sleep(1)

    if channel.id not in temporary_channels:
        return

    try:
        channel = await channel.guild.fetch_channel(channel.id)
    except Exception:
        return

    if len(channel.members) == 0:
        try:
            await channel.delete()
            del temporary_channels[channel.id]
            logger.info(f"Sala temporária {channel.name} (ID: {channel.id}) removida - estava vazia")
        except Exception as e:
            logger.error(f"Erro ao deletar canal {channel.id}: {e}")


async def cleanup_old_channels(guild):
    current_time = time.time()
    to_remove = []

    for channel_id, data in list(temporary_channels.items()):
        age = current_time - data["created_at"]
        if age > MAX_CHANNEL_AGE_SECONDS:
            to_remove.append(channel_id)

    for channel_id in to_remove:
        try:
            channel = guild.get_channel(channel_id)
            if channel and len(channel.members) == 0:
                await channel.delete()
                del temporary_channels[channel_id]
                logger.info(f"Sala temporária {channel_id} removida na limpeza (24h+)")
        except Exception as e:
            logger.error(f"Erro na limpeza do canal {channel_id}: {e}")


def start_cleanup_task(bot):
    async def cleanup_loop():
        await bot.wait_until_ready()
        while not bot.is_closed():
            await asyncio.sleep(3600)
            for guild in bot.guilds:
                await cleanup_old_channels(guild)
            logger.info("Limpeza preventiva de salas antigas executada")

    return bot.loop.create_task(cleanup_loop())
