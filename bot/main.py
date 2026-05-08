import asyncio
import contextlib
import logging
import logging.handlers
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from aiohttp import web

from bot.config import BOT_TOKEN, ADMIN_IDS, WEBHOOK_PORT, SUPABASE_URL, SUPABASE_SERVICE_KEY
from bot.webhook_server import create_app
from bot.database.pool import init_pool, close_pool
from bot.database import ensure_default_styles, ensure_default_sessions
from bot.data.styles import DEFAULT_STYLES
from bot.data.sessions import DEFAULT_SESSIONS
from bot.services.subscription import is_bot_admin

from bot.handlers import (
    start, menu, styles, photo_session, custom_prompt, payment, profile, admin,
)
from bot.middlewares.auth import AuthMiddleware

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.handlers.RotatingFileHandler(
            "logs/bot.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        ),
    ],
)
logging.getLogger("aiogram.event").setLevel(logging.WARNING)
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

    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        logger.warning("SUPABASE_URL or SUPABASE_SERVICE_KEY is not set — storage for pending unlocks will not work!")
    else:
        logger.info("Supabase Storage configured: %s", SUPABASE_URL)

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

    await bot.set_my_commands([
        BotCommand(command="start",   description="Начать / главное меню"),
        BotCommand(command="menu",    description="Главное меню"),
        BotCommand(command="profile", description="Мой профиль и кредиты"),
        BotCommand(command="pay",     description="Пополнить баланс"),
    ])

    webhook_app = create_app(bot)
    runner = web.AppRunner(webhook_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", WEBHOOK_PORT)
    await site.start()
    logger.info("Robokassa webhook server started on port %d", WEBHOOK_PORT)

    await _cleanup_expired_unlocks()
    reminder_task = asyncio.create_task(_paywall_reminder_loop(bot))
    cleanup_task = asyncio.create_task(_cleanup_loop())

    logger.info("Bot started")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        reminder_task.cancel()
        cleanup_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await reminder_task
        with contextlib.suppress(asyncio.CancelledError):
            await cleanup_task
        await runner.cleanup()
        await close_pool()
        await bot.session.close()
        logger.info("Bot stopped")


async def _cleanup_expired_unlocks() -> None:
    from bot.database import get_expired_unlocks, delete_pending_unlock
    from bot.services import storage

    try:
        expired = await get_expired_unlocks()
        for record in expired:
            uid, path = record["user_id"], record["file_id"]
            try:
                await storage.delete_clean_photo(path)
            except Exception:
                logger.warning("Could not delete storage file user=%s path=%s", uid, path)
            await delete_pending_unlock(uid)
        if expired:
            logger.info("Cleaned up %d expired pending unlocks", len(expired))
    except Exception:
        logger.exception("Error during expired unlocks cleanup")


async def _cleanup_loop() -> None:
    while True:
        await asyncio.sleep(3600)
        await _cleanup_expired_unlocks()


async def _paywall_reminder_loop(bot: Bot) -> None:
    """Sends a single reminder to users who saw the paywall >24h ago and haven't paid."""
    from bot.database import get_pending_paywall_reminders, mark_paywall_reminder_sent
    from bot.keyboards.builders import paywall_reminder_kb

    while True:
        await asyncio.sleep(3600)
        try:
            user_ids = await get_pending_paywall_reminders()
            for uid in user_ids:
                if uid in ADMIN_IDS:
                    continue
                try:
                    await bot.send_message(
                        uid,
                        "Привет! Ты смотрел(а) наши тарифы, но так и не пополнил(а) баланс.\n\n"
                        "Возвращайся — мы ждем!",
                        reply_markup=paywall_reminder_kb(),
                    )
                    await mark_paywall_reminder_sent(uid)
                except Exception:
                    logger.debug("Could not send reminder to user %s (likely blocked bot)", uid)
                await asyncio.sleep(0.05)
        except Exception:
            logger.exception("Paywall reminder loop error")
