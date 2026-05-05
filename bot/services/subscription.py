"""Check Telegram channel subscription status."""
import asyncio
import logging
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from bot.config import CHANNEL_ID

logger = logging.getLogger(__name__)


async def is_bot_admin(bot: Bot) -> bool:
    try:
        admins = await bot.get_chat_administrators(CHANNEL_ID)
        bot_id = (await bot.get_me()).id
        return any(admin.user.id == bot_id for admin in admins)
    except Exception as e:
        logger.error(f"Failed to check bot admin status: {e}")
        return False


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    for attempt in range(3):
        try:
            member = await bot.get_chat_member(CHANNEL_ID, user_id)
            logger.info(f"User {user_id} subscription status: {member.status}")
            return member.status not in ("left", "kicked")
        except TelegramBadRequest as e:
            logger.warning(f"Failed to check subscription for user {user_id}: {e}")
            return False
        except Exception as e:
            logger.warning(f"Network error checking subscription for user {user_id} (attempt {attempt + 1}): {e}")
            if attempt < 2:
                await asyncio.sleep(2)
    logger.error(f"All retries failed checking subscription for user {user_id}")
    return False
