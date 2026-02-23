"""Global error handler."""

from __future__ import annotations

import logging

from aiogram import Router
from aiogram.types import ErrorEvent

from bot.app.utils.exceptions import BackendError


logger = logging.getLogger(__name__)
router = Router()


@router.errors()
async def handle_errors(event: ErrorEvent) -> bool:
    exception = event.exception
    logger.exception("Unhandled error", extra={"exception": str(exception)})

    message = None
    if event.update.message:
        message = event.update.message
    elif event.update.callback_query and event.update.callback_query.message:
        message = event.update.callback_query.message

    if message:
        if isinstance(exception, BackendError):
            await message.answer("Backend error. Please try again later.")
        else:
            await message.answer("Unexpected error. Please try again later.")

    return True
