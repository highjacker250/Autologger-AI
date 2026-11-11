# Autologger Service Monitor

Monitoring-only rebuild for Render. It provides a FastAPI dashboard, `GET/HEAD /`, `/health`, and aggregate-only inventory counts from an optional Supabase `inventory` table.

## Render
- Runtime: Docker
- Dockerfile: repository root
- Render supplies `PORT`; the start script uses it automatically (local default `10000`).
- Health check path: `/health`

## Environment variables
- `BOT_TOKEN` (optional; needed only for Telegram monitoring bot)
- `ADMIN_IDS` (comma-separated Telegram numeric user IDs; required to authorize bot commands)
- `SUPABASE_URL`, `SUPABASE_KEY` (optional; use a read-only key/policy)
- `LOG_LEVEL` (optional, default `INFO`)

## Inventory table
Optional Supabase table named `inventory` with columns `id` and `status`. The app reads at most 5,000 rows and displays only aggregate counts. It does not display item identifiers or personal data. Configure Row Level Security so the supplied key can only read this table and only the needed columns.

## Telegram commands
- `/start`
- `/status`
- `/health`

Set `ADMIN_IDS`; without an allowlisted numeric Telegram user ID, bot commands are denied.

## Security changes
This rebuild intentionally removes SMS/OTP extraction and forwarding, third-party login automation, account creation, credential/cookie/session storage, and number acquisition. Old secrets should be rotated before deployment.
