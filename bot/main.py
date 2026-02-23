"""Bot entrypoint."""

from __future__ import annotations

import asyncio
import logging

from bot.app.config import get_settings
from bot.app.core.bot import build_app


logger = logging.getLogger(__name__)


async def main() -> None:
    settings = get_settings()
    bot, dispatcher, deps = build_app(settings)

    logger.info("bot_starting")
    try:
        await dispatcher.start_polling(bot, allowed_updates=dispatcher.resolve_used_update_types())
    finally:
        logger.info("bot_shutdown")
        await deps.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
