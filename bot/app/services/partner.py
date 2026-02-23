"""Partner resolution logic."""

from __future__ import annotations

import asyncio
from typing import Optional

from bot.app.api.backend_client import BackendClient
from bot.app.config import Settings


class PartnerService:
    """Resolve partner context using settings or backend call."""

    def __init__(self, backend: BackendClient, settings: Settings) -> None:
        self._backend = backend
        self._settings = settings
        self._lock = asyncio.Lock()
        self._cached: Optional[str] = settings.PARTNER_ID

    async def resolve_partner_id(self) -> Optional[str]:
        if self._cached:
            return self._cached

        async with self._lock:
            if self._cached:
                return self._cached
            response = await self._backend.resolve_partner()
            partner_id = response.get("partner_id") or response.get("id")
            if partner_id is not None:
                self._cached = str(partner_id)
            return self._cached
