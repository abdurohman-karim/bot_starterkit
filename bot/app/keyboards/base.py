"""Keyboard construction based on backend menu definitions."""

from __future__ import annotations

from typing import Any

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)


def _inline_button(payload: dict[str, Any]) -> InlineKeyboardButton | None:
    text = str(payload.get("text", "")).strip()
    if not text:
        return None
    if "url" in payload:
        return InlineKeyboardButton(text=text, url=str(payload["url"]))
    action = payload.get("action") or payload.get("callback_data") or text
    return InlineKeyboardButton(text=text, callback_data=str(action))


def _reply_button(payload: dict[str, Any]) -> KeyboardButton | None:
    text = str(payload.get("text", "")).strip()
    if not text:
        return None
    return KeyboardButton(text=text)


def build_menu(menu: dict[str, Any]) -> InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | None:
    """Build inline/reply keyboard from backend menu spec."""

    menu_type = str(menu.get("type", "inline")).lower()

    if menu_type in {"remove", "remove_keyboard"}:
        return ReplyKeyboardRemove()

    buttons = menu.get("buttons", [])
    if not isinstance(buttons, list):
        return None

    if menu_type == "reply":
        rows: list[list[KeyboardButton]] = []
        for row in buttons:
            row_buttons: list[KeyboardButton] = []
            for item in row if isinstance(row, list) else [row]:
                if isinstance(item, str):
                    row_buttons.append(KeyboardButton(text=item))
                elif isinstance(item, dict):
                    btn = _reply_button(item)
                    if btn:
                        row_buttons.append(btn)
            if row_buttons:
                rows.append(row_buttons)
        if not rows:
            return None
        return ReplyKeyboardMarkup(
            keyboard=rows,
            resize_keyboard=bool(menu.get("resize", True)),
            one_time_keyboard=bool(menu.get("one_time", False)),
            input_field_placeholder=menu.get("placeholder"),
        )

    rows_inline: list[list[InlineKeyboardButton]] = []
    for row in buttons:
        row_buttons_inline: list[InlineKeyboardButton] = []
        for item in row if isinstance(row, list) else [row]:
            if isinstance(item, str):
                row_buttons_inline.append(InlineKeyboardButton(text=item, callback_data=item))
            elif isinstance(item, dict):
                btn = _inline_button(item)
                if btn:
                    row_buttons_inline.append(btn)
        if row_buttons_inline:
            rows_inline.append(row_buttons_inline)
    if not rows_inline:
        return None
    return InlineKeyboardMarkup(inline_keyboard=rows_inline)
