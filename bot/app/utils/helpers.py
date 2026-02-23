"""Helper utilities for payloads and backend responses."""

from __future__ import annotations

from typing import Any, Iterable

from aiogram.types import Chat, Message, User

from bot.app.keyboards.base import build_menu


def build_user_payload(user: User, chat: Chat | None, partner_id: str | None) -> dict[str, Any]:
    """Serialize Telegram user/chat into a backend-friendly payload."""

    payload: dict[str, Any] = {
        "user": {
            "id": user.id,
            "is_bot": user.is_bot,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "language_code": user.language_code,
        },
        "partner_id": partner_id,
    }
    if chat is not None:
        payload["chat"] = {
            "id": chat.id,
            "type": chat.type,
            "title": chat.title,
            "username": chat.username,
        }
    return payload


def normalize_messages(payload: dict[str, Any] | list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Normalize backend payload into a list of message dicts."""

    if payload is None:
        return []
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("messages"), list):
        return payload["messages"]
    return [payload]


def extract_text(message_payload: dict[str, Any]) -> str:
    """Pick the most likely text field from payload."""

    for key in ("text", "message", "title", "body"):
        value = message_payload.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def extract_menu(message_payload: dict[str, Any]) -> dict[str, Any] | None:
    """Extract menu/keyboard definition from payload."""

    for key in ("menu", "keyboard", "reply_markup"):
        value = message_payload.get(key)
        if isinstance(value, dict):
            return value
    return None


def iter_actions(message_payload: dict[str, Any]) -> Iterable[dict[str, Any]]:
    """Return actions list if present (optional future use)."""

    actions = message_payload.get("actions")
    if isinstance(actions, list):
        for action in actions:
            if isinstance(action, dict):
                yield action


def build_reply_markup(message_payload: dict[str, Any]):
    """Build aiogram reply markup from backend menu spec."""

    menu = extract_menu(message_payload)
    if menu:
        return build_menu(menu)
    return None


async def respond_with_payload(message: Message, payload: dict[str, Any] | list[dict[str, Any]] | None) -> None:
    """Send one or more messages based on backend response."""

    for item in normalize_messages(payload):
        text = extract_text(item)
        reply_markup = build_reply_markup(item)
        if text or reply_markup is not None:
            await message.answer(text or " ", reply_markup=reply_markup)
