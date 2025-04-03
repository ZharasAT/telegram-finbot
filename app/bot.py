from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os
import logging
from aiogram.client.default import DefaultBotProperties
import pdfplumber
from aiogram.types import FSInputFile

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(lambda message: message.document and message.document.mime_type == 'application/pdf')
async def handle_pdf(message: Message):
    file = await bot.download(message.document)
    file_path = f"temp/{message.document.file_name}"

    with open(file_path, "wb") as f:
        f.write(file.read())

    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    if text:
        await message.answer(f"Вот что я нашел в PDF:\n\n{text[:3000]}")
    else:
        await message.answer("Не удалось извлечь текст из PDF 😔")

@dp.message()
async def echo_message(message: Message):
    await message.answer("Привет! Отправь мне PDF-выписку, и я проанализирую ее")

async def start_bot():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)
