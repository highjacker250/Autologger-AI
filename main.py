from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from db import supabase, get_accounts, get_stats
from ai_parser import extract_otp
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

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

# --- DASHBOARD ROUTES ---
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    stats = get_stats()
    return templates.TemplateResponse("index.html", {"request": request, "stats": stats})

@app.get("/accounts/{platform}", response_class=HTMLResponse)
async def accounts_list(request: Request, platform: str):
    accounts = get_accounts(platform)
    return templates.TemplateResponse("accounts.html", {"request": request, "platform": platform, "accounts": accounts})

@app.get("/live/{task_id}", response_class=HTMLResponse)
async def live_view(request: Request, task_id: int):
    res = supabase.table('tasks').select('status').eq('id', task_id).execute()
    step = res.data[0]['status'] if res.data else "unknown"
    return templates.TemplateResponse("live.html", {"request": request, "task_id": task_id, "step": step})

@app.get("/api/stats")
async def api_stats():
    return get_stats()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
