import os
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from db import get_monitoring_stats, check_database

logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger('autologger')
app = FastAPI(title='Autologger Service Monitor', version='2.0.0')
templates = Jinja2Templates(directory='templates')

@app.get('/', response_class=HTMLResponse)
@app.head('/')
async def dashboard(request: Request):
    stats = get_monitoring_stats()
    if request.method == 'HEAD':
        return HTMLResponse(content='', status_code=200)
    return templates.TemplateResponse(request=request, name='index.html', context={'stats': stats})

@app.get('/health')
@app.head('/health')
async def health():
    db_ok = check_database()
    payload = {'status': 'ok' if db_ok else 'degraded', 'service': 'autologger-monitor',
               'database': 'ok' if db_ok else 'unavailable',
               'timestamp': datetime.now(timezone.utc).isoformat()}
    return JSONResponse(payload, status_code=200 if db_ok else 503)

@app.get('/api/stats')
async def api_stats():
    return get_monitoring_stats()

@app.get('/api/ready')
async def ready():
    return {'ready': True}

@app.exception_handler(Exception)
async def unhandled_error(request: Request, exc: Exception):
    logger.exception('Unhandled request error on %s', request.url.path)
    return JSONResponse({'detail': 'Internal server error'}, status_code=500)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=int(os.getenv('PORT', '10000')))
