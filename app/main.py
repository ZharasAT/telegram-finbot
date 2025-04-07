from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from aiogram.types import Update
from app.bot import bot, dp
import os

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.getenv("WEBHOOK_URL") + WEBHOOK_PATH

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook установлен: {WEBHOOK_URL}")

    yield  # ⬅️ здесь FastAPI запускается

    # shutdown
    await bot.delete_webhook()
    print("Webhook удалён")

app = FastAPI(lifespan=lifespan)

@app.post(WEBHOOK_PATH)
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}