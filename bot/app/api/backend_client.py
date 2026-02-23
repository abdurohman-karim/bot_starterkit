"""Async HTTP client for the Laravel backend API."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from bot.app.config import Settings
from bot.app.utils.exceptions import (
    BackendAuthError,
    BackendBadResponse,
    BackendError,
    BackendTimeout,
    BackendUnavailable,
)


logger = logging.getLogger(__name__)


class BackendClient:
    """Unified backend client with retries and error mapping."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = httpx.AsyncClient(
            base_url=settings.API_URL.rstrip("/"),
            headers={
                "Authorization": f"Bearer {settings.API_TOKEN}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=settings.REQUEST_TIMEOUT,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def _sleep_backoff(self, attempt: int) -> None:
        delay = self._settings.RETRY_BACKOFF * (2 ** (attempt - 1))
        await asyncio.sleep(delay)

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        partner_id: str | None = None,
    ) -> dict[str, Any]:
        url = path if path.startswith("/") else f"/{path}"
        headers = {}
        if partner_id:
            headers["X-Partner-Id"] = str(partner_id)

        for attempt in range(1, self._settings.RETRY_COUNT + 1):
            try:
                response = await self._client.request(
                    method,
                    url,
                    json=json,
                    params=params,
                    headers=headers or None,
                )
            except httpx.TimeoutException as exc:
                logger.warning("Backend timeout", extra={"attempt": attempt, "path": url})
                if attempt >= self._settings.RETRY_COUNT:
                    raise BackendTimeout("Backend request timed out") from exc
                await self._sleep_backoff(attempt)
                continue
            except httpx.RequestError as exc:
                logger.warning("Backend request error", extra={"attempt": attempt, "path": url})
                if attempt >= self._settings.RETRY_COUNT:
                    raise BackendUnavailable("Backend unavailable") from exc
                await self._sleep_backoff(attempt)
                continue

            if response.status_code >= 500:
                logger.warning(
                    "Backend server error",
                    extra={"status_code": response.status_code, "attempt": attempt, "path": url},
                )
                if attempt >= self._settings.RETRY_COUNT:
                    raise BackendUnavailable(
                        "Backend server error",
                        status_code=response.status_code,
                    )
                await self._sleep_backoff(attempt)
                continue

            if response.status_code in {401, 403}:
                raise BackendAuthError(
                    "Backend authentication error",
                    status_code=response.status_code,
                )

            if 400 <= response.status_code < 500:
                raise BackendError(
                    "Backend request error",
                    status_code=response.status_code,
                )

            try:
                data = response.json()
            except ValueError as exc:
                raise BackendBadResponse("Backend returned invalid JSON") from exc

            return data

        raise BackendUnavailable("Backend request failed after retries")

    async def start(self, payload: dict[str, Any], partner_id: str | None) -> dict[str, Any]:
        return await self.request("POST", self._settings.START_ENDPOINT, json=payload, partner_id=partner_id)

    async def sync_user(self, payload: dict[str, Any], partner_id: str | None) -> dict[str, Any]:
        return await self.request(
            "POST", self._settings.USER_SYNC_ENDPOINT, json=payload, partner_id=partner_id
        )

    async def get_menu(self, payload: dict[str, Any], partner_id: str | None) -> dict[str, Any]:
        return await self.request("GET", self._settings.MENU_ENDPOINT, params=payload, partner_id=partner_id)

    async def action(self, payload: dict[str, Any], partner_id: str | None) -> dict[str, Any]:
        return await self.request("POST", self._settings.ACTION_ENDPOINT, json=payload, partner_id=partner_id)

    async def resolve_partner(self) -> dict[str, Any]:
        return await self.request("GET", self._settings.PARTNER_ENDPOINT)
