"""Check Telegram channel subscription status."""
import logging
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from bot.config import CHANNEL_ID

logger = logging.getLogger(__name__)


async def is_bot_admin(bot: Bot) -> bool:
    """Check if bot is admin in the channel."""
    try:
        admins = await bot.get_chat_administrators(CHANNEL_ID)
        bot_id = (await bot.get_me()).id
        return any(admin.user.id == bot_id for admin in admins)
    except Exception as e:
        logger.error(f"Failed to check bot admin status: {e}")
        return False


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        logger.info(f"User {user_id} subscription status: {member.status}")
        return member.status not in ("left", "kicked")
    except TelegramBadRequest as e:
        logger.warning(f"Failed to check subscription for user {user_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking subscription for user {user_id}: {e}")
        return False
