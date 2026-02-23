**Telegram Bot Starter-Kit**

**Run Locally**
1. Copy `bot/.env.example` to `bot/.env` and fill values.
2. Ensure Redis is running and update `REDIS_URL` if needed.
3. Run `python -m bot.main`.

**Run With Docker**
1. Create `bot/.env` with production values.
2. Set `REDIS_URL=redis://redis:6379/0` in `bot/.env`.
3. Run `docker compose up --build`.

**Backend Contract**
See `docs/backend_api.md`.
