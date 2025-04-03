from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os
import logging
from aiogram.client.default import DefaultBotProperties

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

@dp.message()
async def echo_message(message: Message):
    await message.answer("Привет! Отправь мне PDF-выписку, и я проанализирую ее")

async def start_bot():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)