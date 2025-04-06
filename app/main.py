import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.bot import start_bot

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(start_bot())
    yield

app = FastAPI(lifespan=lifespan)