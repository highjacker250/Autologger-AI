from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from db import supabase, get_accounts, get_stats
from ai_parser import extract_otp
from tg_login import send_tg_otp, verify_tg_otp
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# --- TELEGRAM LOGIN MODELS ---
class TGLoginRequest(BaseModel):
    phone: str

class TGVerifyRequest(BaseModel):
    phone: str
    otp: str

# --- WEBHOOK (SMS Receive) ---
@app.post("/webhook")
async def receive_sms(request: Request):
    payload = await request.json()
    data = payload.get("data", {})
    phone = data.get("num")
    sms = data.get("sms")
    
    if phone and sms:
        otp = extract_otp(sms)
        if otp:
            supabase.table('otp_logs').insert({
                "phone": phone, "otp": otp, "raw_sms": sms, "used": False
            }).execute()
            return {"status": "success", "otp": otp}
    return {"status": "ignored"}

# --- TELEGRAM LOGIN ROUTES ---
@app.get("/telegram_login", response_class=HTMLResponse)
async def telegram_login_page(request: Request):
    return templates.TemplateResponse(request=request, name="telegram_login.html", context={})

@app.post("/api/tg/send_otp")
async def tg_send_otp_endpoint(req: TGLoginRequest):
    return await send_tg_otp(req.phone)

@app.post("/api/tg/verify_otp")
async def tg_verify_endpoint(req: TGVerifyRequest):
    return await verify_tg_otp(req.phone, req.otp)

# --- DASHBOARD ROUTES ---
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    stats = get_stats()
    return templates.TemplateResponse(request=request, name="index.html", context={"stats": stats})

@app.get("/accounts/{platform}", response_class=HTMLResponse)
async def accounts_list(request: Request, platform: str):
    accounts = get_accounts(platform)
    return templates.TemplateResponse(request=request, name="accounts.html", context={"platform": platform, "accounts": accounts})

@app.get("/live/{task_id}", response_class=HTMLResponse)
async def live_view(request: Request, task_id: int):
    res = supabase.table('tasks').select('status').eq('id', task_id).execute()
    step = res.data[0]['status'] if res.data else "unknown"
    return templates.TemplateResponse(request=request, name="live.html", context={"task_id": task_id, "step": step})

@app.get("/api/stats")
async def api_stats():
    return get_stats()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)a
