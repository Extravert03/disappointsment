from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode

import settings


bot = Bot(settings.TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.MARKDOWN_V2)
dp = Dispatcher(bot, storage=MemoryStorage())
