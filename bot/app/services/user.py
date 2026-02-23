"""Telegram user synchronization service."""

from __future__ import annotations

import time
from typing import Optional

from aiogram.types import Chat, User

from bot.app.api.backend_client import BackendClient
from bot.app.config import Settings
from bot.app.utils.helpers import build_user_payload


class UserService:
    """Sync Telegram users with backend."""

    def __init__(self, backend: BackendClient, settings: Settings) -> None:
        self._backend = backend
        self._settings = settings
        self._last_sync: dict[int, float] = {}

    async def sync_user(
        self,
        user: User,
        chat: Optional[Chat],
        partner_id: Optional[str],
        *,
        force: bool = False,
    ) -> None:
        if not force:
            last_time = self._last_sync.get(user.id)
            if last_time and (time.time() - last_time) < self._settings.USER_SYNC_TTL:
                return

        payload = build_user_payload(user, chat, partner_id)
        await self._backend.sync_user(payload, partner_id)
        self._last_sync[user.id] = time.time()
