import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
VOICE_CATEGORY_NAME = "🎙 VOZ"
TRIGGER_CHANNEL_NAME = "➕ Criar Sala"
TEMP_CHANNEL_PREFIX = "🎮 Sala do"
