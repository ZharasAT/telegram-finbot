from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from dotenv import load_dotenv
import pdfplumber

from app.parser import parse_transactions
from app.ai_analysis import analyze_transactions_with_gpt
from app.utils.excel_exporter import save_transactions_to_excel

load_dotenv()

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import F
import os
import logging

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

from aiogram.client.default import DefaultBotProperties

bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

user_sessions = {}

@dp.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer("Привет! Я бот для обработки PDF-выписок 😊")

@dp.message(lambda message: message.document and message.document.mime_type == 'application/pdf')
async def handle_pdf(message: Message):
    file = await bot.download(message.document.file_id)
    file_path = f"temp/{message.document.file_name}"

    with open(file_path, "wb") as f:
        f.write(file.read())

    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    with open("temp/raw_text.txt", "w", encoding="utf-8") as debug_file:
        debug_file.write(text)

    if not text:
        await message.answer("Не удалось извлечь текст из PDF 😔")
        return

    pdf_path = file_path
    transactions = parse_transactions(text=text, pdf_path=pdf_path)

    if not transactions:
        await message.answer("Не удалось найти транзакции в PDF 😔")
        return

    user_id = message.from_user.id
    user_sessions.setdefault(user_id, []).extend(transactions)

    await message.answer(
        f"✅ Файл {message.document.file_name} добавлен в сессию.\n"
        f"Всего транзакций в сессии: {len(user_sessions[user_id])}"
    )

    # Кнопки: объединить и очистить
    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📄 Объединить выписки", callback_data="merge_done")],
            [InlineKeyboardButton(text="🗑 Очистить сессию", callback_data="clear_session")]
        ]
    )
    await message.answer("Если вы загрузили все выписки, нажмите кнопку ниже:", reply_markup=buttons)

import os
from datetime import datetime

async def send_merged_excel(user_id: int, target):
    transactions = user_sessions.get(user_id)
    if not transactions:
        await target.answer("❌ Нет транзакций для экспорта.")
        return

    await target.answer(f"✅ Найдено {len(transactions)} транзакций.")

    # Формируем путь
    filename = f"merged_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    excel_path = os.path.join("temp", filename)

    # Сохраняем Excel-файл
    save_transactions_to_excel(transactions, output_path=excel_path)

    # Отправляем
    excel_file = FSInputFile(excel_path)
    await target.answer_document(excel_file, caption="📊 Вот ваша объединённая выписка")

    await target.answer("Если нужно — повторите операцию 😊")

@dp.callback_query(lambda c: c.data == "merge_done")
async def handle_merge_callback(callback: CallbackQuery):
    await send_merged_excel(callback.from_user.id, callback.message)

@dp.message(lambda message: message.text.lower() in ["/done_merge"])
async def handle_done_merge(message: Message):
    await send_merged_excel(message.from_user.id, message)

@dp.callback_query(lambda c: c.data == "clear_session")
async def handle_clear_session(callback: CallbackQuery):
    user_sessions[callback.from_user.id] = []
    await callback.message.answer("🗑 Сессия очищена! Вы можете загрузить новые выписки.")

@dp.message(lambda message: message.text.lower() in ["да", "анализ", "go"])
async def handle_analysis(message: Message):
    user_id = message.from_user.id
    transactions = user_sessions.get(user_id)

    if not transactions:
        await message.answer("Сессия пуста. Нечего анализировать 😔")
        return

    await message.answer("📊 Отправляю данные на анализ в GPT...")
    try:
        result = await analyze_transactions_with_gpt(transactions)
        await message.answer(result)
    except Exception as e:
        logging.exception("GPT analysis failed")
        await message.answer("Произошла ошибка при анализе с GPT 😢")

    user_sessions[user_id] = []  # очистка сессии

@dp.message(lambda message: message.text.lower() in ["нет", "no"])
async def handle_cancel_analysis(message: Message):
    await message.answer("Ок! Если передумаете — просто напишите `да`, и я проведу анализ ✨")

@dp.message()
async def echo_message(message: Message):
    await message.answer("Привет! Отправь мне PDF-выписку, и я проанализирую ее")

async def start_bot():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)