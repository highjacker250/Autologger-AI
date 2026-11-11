import asyncio
import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from db import get_monitoring_stats, check_database

load_dotenv()
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
log = logging.getLogger('autologger.bot')
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = {int(x.strip()) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip().isdigit()}

if not TOKEN:
    raise RuntimeError('BOT_TOKEN is missing')
bot = Bot(token=TOKEN)
dp = Dispatcher()


def is_admin(message: Message) -> bool:
    return bool(message.from_user and message.from_user.id in ADMIN_IDS)

@dp.message(Command('start'))
async def start(message: Message):
    if not is_admin(message):
        await message.answer('Access denied.')
        return
    await message.answer('Service Monitor is online. Commands: /status, /health')

@dp.message(Command('status'))
async def status(message: Message):
    if not is_admin(message):
        await message.answer('Access denied.')
        return
    s = get_monitoring_stats()
    total = 'not configured' if s['inventory_total'] is None else str(s['inventory_total'])
    available = 'not configured' if s['inventory_available'] is None else str(s['inventory_available'])
    await message.answer(f"Database: {s['database']}\nInventory total: {total}\nAvailable: {available}\n{ s['note'] }")

@dp.message(Command('health'))
async def health(message: Message):
    if not is_admin(message):
        await message.answer('Access denied.')
        return
    await message.answer('Database: ' + ('OK' if check_database() else 'Unavailable'))

async def main():
    log.info('Monitoring bot starting')
    await dp.start_polling(bot, drop_pending_updates=True)

if __name__ == '__main__':
    asyncio.run(main())
