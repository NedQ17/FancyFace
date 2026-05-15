from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from bot.config import CHANNEL_URL, FREE_CREDITS_FOR_SUBSCRIPTION
from bot.database import get_user, set_channel_unsubscribed
from bot.keyboards.builders import subscribe_kb
from bot.services.subscription import is_subscribed

SUBSCRIBE_TEXT = (
    "Для использования бота нужно подписаться на наш канал.\n\n"
    f"🎁 После подписки ты получишь <b>{FREE_CREDITS_FOR_SUBSCRIPTION} бесплатную генерацию</b>!"
)

RESUBSCRIBE_TEXT = (
    "Для использования бота нужно подписаться на наш канал."
)


_EXEMPT_CALLBACKS = {"subscribe:check", "menu:info"}


def _is_exempt(event: TelegramObject) -> bool:
    if isinstance(event, Message) and event.text:
        return event.text.startswith("/start")
    if isinstance(event, CallbackQuery):
        return event.data in _EXEMPT_CALLBACKS
    return False


async def _send_subscribe_prompt(event: TelegramObject, bot, is_first_time: bool) -> None:
    if isinstance(event, Message):
        chat_id = event.chat.id
    elif isinstance(event, CallbackQuery):
        chat_id = event.message.chat.id
        try:
            await event.answer()
        except Exception:
            pass
    else:
        return
    text = SUBSCRIBE_TEXT if is_first_time else RESUBSCRIBE_TEXT
    await bot.send_message(
        chat_id,
        text,
        parse_mode="HTML",
        reply_markup=subscribe_kb(),
    )


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user = data.get("event_from_user")
        if not tg_user:
            return await handler(event, data)

        db_user = await get_user(tg_user.id)
        if not db_user:
            return await handler(event, data)

        if db_user.get("is_blocked"):
            return

        if _is_exempt(event):
            return await handler(event, data)

        bot = data.get("bot")

        is_first_time = not db_user.get("subscription_bonus_claimed")

        if not db_user.get("channel_subscribed"):
            if bot:
                await _send_subscribe_prompt(event, bot, is_first_time)
            return

        # Re-verify with Telegram to catch unsubscriptions
        if bot and not await is_subscribed(bot, tg_user.id):
            await set_channel_unsubscribed(tg_user.id)
            await _send_subscribe_prompt(event, bot, is_first_time=False)
            return

        return await handler(event, data)
