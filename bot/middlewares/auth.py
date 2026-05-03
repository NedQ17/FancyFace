from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from bot.database import get_user


class AuthMiddleware(BaseMiddleware):
    """Blocks messages from users marked as is_blocked in the database."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user:
            db_user = await get_user(user.id)
            if db_user and db_user.get("is_blocked"):
                return
        return await handler(event, data)
