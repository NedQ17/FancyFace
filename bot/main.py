import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import BOT_TOKEN
from bot.database.pool import init_pool, close_pool
from bot.database import ensure_default_styles, ensure_default_sessions
from bot.data.styles import DEFAULT_STYLES
from bot.data.sessions import DEFAULT_SESSIONS
from bot.services.subscription import is_bot_admin

from bot.handlers import (
    start, menu, styles, photo_session, custom_prompt, payment, profile, admin,
)
from bot.middlewares.auth import AuthMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    await init_pool()
    await ensure_default_styles(DEFAULT_STYLES)
    await ensure_default_sessions(DEFAULT_SESSIONS)

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Проверим, что бот администратор канала
    if not await is_bot_admin(bot):
        logger.error("Bot is not admin in the channel! Subscription checking will not work.")
        # Можно продолжить работу, но с предупреждением

    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(styles.router)
    dp.include_router(photo_session.router)
    dp.include_router(custom_prompt.router)
    dp.include_router(payment.router)
    dp.include_router(profile.router)
    dp.include_router(admin.router)

    asyncio.create_task(_paywall_reminder_loop(bot))

    logger.info("Bot started")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await close_pool()
        await bot.session.close()


async def _paywall_reminder_loop(bot: Bot) -> None:
    """Sends a single reminder to users who saw the paywall >24h ago and haven't paid."""
    from bot.database import get_pending_paywall_reminders, mark_paywall_reminder_sent
    from bot.keyboards.builders import paywall_reminder_kb

    while True:
        await asyncio.sleep(3600)
        try:
            user_ids = await get_pending_paywall_reminders()
            for uid in user_ids:
                try:
                    await bot.send_message(
                        uid,
                        "Привет! Ты смотрел(а) наши тарифы, но так и не пополнил(а) баланс.\n\n"
                        "Возвращайся — первые 3 генерации за подписку на канал уже ждут!",
                        reply_markup=paywall_reminder_kb(),
                    )
                    await mark_paywall_reminder_sent(uid)
                except Exception:
                    pass
                await asyncio.sleep(0.05)
        except Exception as e:
            logger.warning(f"Paywall reminder loop error: {e}")
