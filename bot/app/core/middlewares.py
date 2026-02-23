"""Custom middlewares for logging, context, rate limiting, and errors."""

from __future__ import annotations

import logging
import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Update
from redis.asyncio import Redis

from bot.app.api.backend_client import BackendClient
from bot.app.services.partner import PartnerService
from bot.app.services.user import UserService
from bot.app.utils.exceptions import BackendError


logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Structured logging of incoming updates."""

    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        started = time.perf_counter()
        user_id = _extract_user_id(event)
        chat_id = _extract_chat_id(event)
        event_type = _event_type(event)
        logger.info("update_received", extra={"user_id": user_id, "chat_id": chat_id, "event": event_type})
        try:
            return await handler(event, data)
        finally:
            duration_ms = int((time.perf_counter() - started) * 1000)
            logger.info(
                "update_processed",
                extra={"user_id": user_id, "chat_id": chat_id, "event": event_type, "duration_ms": duration_ms},
            )


class BackendContextMiddleware(BaseMiddleware):
    """Attach backend services and partner context to handler data."""

    def __init__(self, backend: BackendClient, partner_service: PartnerService, user_service: UserService) -> None:
        self._backend = backend
        self._partner_service = partner_service
        self._user_service = user_service

    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        partner_id = await self._partner_service.resolve_partner_id()
        data["partner_id"] = partner_id
        data["backend"] = self._backend
        data["user_service"] = self._user_service
        return await handler(event, data)


class RateLimitMiddleware(BaseMiddleware):
    """Redis-backed rate limiting per user."""

    def __init__(self, redis_client: Redis, rate_limit_seconds: float, prefix: str) -> None:
        self._redis = redis_client
        self._rate_limit = rate_limit_seconds
        self._prefix = prefix

    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        user_id = _extract_user_id(event)
        if user_id is None or self._rate_limit <= 0:
            return await handler(event, data)

        ttl_ms = int(self._rate_limit * 1000)
        key = f"{self._prefix}:rate:{user_id}"
        try:
            allowed = await self._redis.set(key, "1", px=ttl_ms, nx=True)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Rate limit redis error", extra={"error": str(exc)})
            return await handler(event, data)

        if not allowed:
            return None

        return await handler(event, data)


class ErrorHandlingMiddleware(BaseMiddleware):
    """Catch unhandled exceptions and notify the user."""

    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except BackendError as exc:
            logger.warning("Backend error", extra={"error": str(exc)})
            message = _extract_message(event)
            if message:
                await message.answer("Backend error. Please try again later.")
            return None
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unhandled exception", extra={"error": str(exc)})
            raise


def _event_type(event: Update) -> str:
    if event.message:
        return "message"
    if event.callback_query:
        return "callback_query"
    if event.inline_query:
        return "inline_query"
    return "update"


def _extract_user_id(event: Update) -> int | None:
    if event.message and event.message.from_user:
        return event.message.from_user.id
    if event.callback_query and event.callback_query.from_user:
        return event.callback_query.from_user.id
    if event.inline_query and event.inline_query.from_user:
        return event.inline_query.from_user.id
    return None


def _extract_chat_id(event: Update) -> int | None:
    if event.message:
        return event.message.chat.id
    if event.callback_query and event.callback_query.message:
        return event.callback_query.message.chat.id
    return None


def _extract_message(event: Update):
    if event.message:
        return event.message
    if event.callback_query and event.callback_query.message:
        return event.callback_query.message
    return None
