from aiogram.types import CallbackQuery

from bot import database as db
from bot.keyboards.builders import paywall_kb

_PAYWALL_LOCKED = (
    "У тебя закончились кредиты. 😔\n\n"
    "Купи любой пакет — и сможешь продолжить создание образов."
)


async def pending_paywall(callback: CallbackQuery) -> bool:
    """Return True and show paywall if user has a pending unlock; caller must return immediately."""
    uid = callback.from_user.id
    if await db.get_pending_unlock(uid):
        try:
            await callback.message.edit_text(_PAYWALL_LOCKED, reply_markup=paywall_kb())
        except Exception:
            await callback.message.answer(_PAYWALL_LOCKED, reply_markup=paywall_kb())
        await callback.answer()
        return True
    return False
