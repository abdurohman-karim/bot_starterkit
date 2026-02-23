"""Start and dynamic action handlers."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from bot.app.api.backend_client import BackendClient
from bot.app.services.user import UserService
from bot.app.utils.helpers import build_user_payload, respond_with_payload


router = Router()


@router.message(CommandStart())
async def handle_start(
    message: Message,
    backend: BackendClient,
    user_service: UserService,
    partner_id: str | None,
) -> None:
    await user_service.sync_user(message.from_user, message.chat, partner_id)

    start_param = None
    if message.text:
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            start_param = parts[1]

    payload = build_user_payload(message.from_user, message.chat, partner_id)
    if start_param:
        payload["start_param"] = start_param

    response = await backend.start(payload, partner_id)
    await respond_with_payload(message, response)


@router.callback_query()
async def handle_callback(
    query: CallbackQuery,
    backend: BackendClient,
    user_service: UserService,
    partner_id: str | None,
) -> None:
    if not query.data:
        await query.answer()
        return

    if query.from_user:
        await user_service.sync_user(query.from_user, query.message.chat if query.message else None, partner_id)

    payload = build_user_payload(query.from_user, query.message.chat if query.message else None, partner_id)
    payload["action"] = query.data

    response = await backend.action(payload, partner_id)
    if query.message:
        await respond_with_payload(query.message, response)
    await query.answer()


@router.message(F.text & ~F.text.startswith("/"))
async def handle_text_action(
    message: Message,
    backend: BackendClient,
    user_service: UserService,
    partner_id: str | None,
) -> None:
    await user_service.sync_user(message.from_user, message.chat, partner_id)

    payload = build_user_payload(message.from_user, message.chat, partner_id)
    payload["action"] = message.text

    response = await backend.action(payload, partner_id)
    await respond_with_payload(message, response)
