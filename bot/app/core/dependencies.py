"""Dependency container for backend clients and services."""

from __future__ import annotations

from dataclasses import dataclass

import redis.asyncio as redis

from bot.app.api.backend_client import BackendClient
from bot.app.config import Settings
from bot.app.services.partner import PartnerService
from bot.app.services.user import UserService


@dataclass
class Dependencies:
    """Container for shared dependencies."""

    backend: BackendClient
    partner_service: PartnerService
    user_service: UserService
    redis: redis.Redis

    async def close(self) -> None:
        await self.backend.close()
        await self.redis.close()
        await self.redis.connection_pool.disconnect()


def build_dependencies(settings: Settings) -> Dependencies:
    backend = BackendClient(settings)
    partner_service = PartnerService(backend, settings)
    user_service = UserService(backend, settings)
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return Dependencies(
        backend=backend,
        partner_service=partner_service,
        user_service=user_service,
        redis=redis_client,
    )
