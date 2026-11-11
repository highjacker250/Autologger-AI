import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def create_task(platform, phone, email, password):
    res = supabase.table('tasks').insert({
        "platform": platform, "phone": phone, "email": email, 
        "password": password, "status": "pending"
    }).execute()
    return res.data[0]['id']

def update_task_status(task_id, status, extra_data=None):
    up = {"status": status}
    if extra_data: 
        up.update(extra_data)
    supabase.table('tasks').update(up).eq('id', task_id).execute()

def get_pending_otp(phone):
    res = supabase.table('otp_logs').select('*').eq('phone', phone).eq('used', False).order('id', desc=True).limit(1).execute()
    if res.data:
        otp = res.data[0]['otp']
        supabase.table('otp_logs').update({"used": True}).eq('id', res.data[0]['id']).execute()
        return otp
    return None

def get_accounts(platform):
    res = supabase.table('tasks').select('*').eq('platform', platform).order('id', desc=True).execute()
    return res.data

def get_stats():
    otps = supabase.table('otp_logs').select('id', count='exact').execute()
    accounts = supabase.table('tasks').select('id', count='exact').eq('status', 'success').execute()
    return {
        "otps": otps.count if otps.count else 0,
        "accounts": accounts.count if accounts.count else 0
    }
