"""Bot and dispatcher initialization."""

from __future__ import annotations

import logging
from typing import Tuple

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage

from bot.app.config import Settings
from bot.app.core.dependencies import Dependencies, build_dependencies
from bot.app.core.middlewares import (
    BackendContextMiddleware,
    ErrorHandlingMiddleware,
    LoggingMiddleware,
    RateLimitMiddleware,
)
from bot.app.handlers import errors_router, start_router
from bot.app.utils.logging import configure_logging


logger = logging.getLogger(__name__)


def create_bot(settings: Settings) -> Bot:
    """Create aiogram Bot instance."""

    default = DefaultBotProperties(parse_mode=settings.PARSE_MODE)
    return Bot(token=settings.BOT_TOKEN, default=default)


def create_dispatcher(settings: Settings, deps: Dependencies) -> Dispatcher:
    """Create dispatcher with routers and middlewares."""

    key_builder = DefaultKeyBuilder(prefix=settings.REDIS_PREFIX, with_destiny=True)
    storage = RedisStorage(deps.redis, key_builder=key_builder)
    dispatcher = Dispatcher(storage=storage)

    dispatcher.update.middleware(ErrorHandlingMiddleware())
    dispatcher.update.middleware(LoggingMiddleware())
    dispatcher.update.middleware(
        RateLimitMiddleware(
            redis_client=deps.redis,
            rate_limit_seconds=settings.RATE_LIMIT_SECONDS,
            prefix=settings.REDIS_PREFIX,
        )
    )
    dispatcher.update.middleware(
        BackendContextMiddleware(
            backend=deps.backend,
            partner_service=deps.partner_service,
            user_service=deps.user_service,
        )
    )

    dispatcher.include_router(start_router)
    dispatcher.include_router(errors_router)

    return dispatcher


def build_app(settings: Settings) -> Tuple[Bot, Dispatcher, Dependencies]:
    """Build bot, dispatcher, and dependencies."""

    configure_logging(settings.LOG_LEVEL)
    deps = build_dependencies(settings)
    bot = create_bot(settings)
    dispatcher = create_dispatcher(settings, deps)
    return bot, dispatcher, deps
