import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
import os
from worker import run_automation
from sms_api import get_number

load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# Range IDs: Apne TempNumbers panel se dekh ke yahan alag alag range IDs daal
RANGES = {"instagram": 12, "facebook": 14, "telegram": 15}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🤖 **AI Auto Logger Ready**\n\n/insta - Instagram\n/fb - Facebook\n/status - View Panel Link", parse_mode="Markdown")

@dp.message(Command("insta"))
async def cmd_insta(message: types.Message):
    await message.answer("⏳ Instagram ke liye number le raha hu...")
    phone = get_number(RANGES["instagram"])
    if not phone:
        await message.answer("❌ Number out of stock!")
        return
        
    await message.answer(f"📱 Number mila: `{phone}`\nAb browser chalu ho raha hai...", parse_mode="Markdown")
    success, email, password = await run_automation("instagram", phone, RANGES["instagram"])
    
    if success:
        await message.answer(f"✅ **Login Success!**\n\n📧 Email: `{email}`\n🔑 Pass: `{password}`\n📱 Phone: `{phone}`", parse_mode="Markdown")
    else:
        await message.answer(f"❌ Failed: {email}")

@dp.message(Command("fb"))
async def cmd_fb(message: types.Message):
    await message.answer("⏳ Facebook ke liye number le raha hu...")
    phone = get_number(RANGES["facebook"])
    if not phone:
        await message.answer("❌ Number out of stock!")
        return
    await message.answer(f"📱 Number mila: `{phone}`\nAb browser chalu ho raha hai...", parse_mode="Markdown")
    success, email, password = await run_automation("facebook", phone, RANGES["facebook"])
    
    if success:
        await message.answer(f"✅ **Login Success!**\n\n📧 Email: `{email}`\n🔑 Pass: `{password}`\n📱 Phone: `{phone}`", parse_mode="Markdown")
    else:
        await message.answer(f"❌ Failed: {email}")

async def main():
    print("Bot Started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
