from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import logging

from bot import database as db
from bot.config import BOT_USERNAME, FREE_CREDITS_FOR_SUBSCRIPTION, REFERRAL_CREDITS
from bot.keyboards.builders import main_menu_kb, subscribe_kb
from bot.services.subscription import is_subscribed

logger = logging.getLogger(__name__)

router = Router()

WELCOME_TEXT = (
    "Привет! Я <b>FancyFace</b> — бот, который делает профессиональные "
    "AI-фото с твоим лицом.\n\n"
    "Загрузи своё фото, выбери образ — и получи крутой результат за 20–30 секунд. "
    "Никакого фотографа, никакого фоторедактора.\n\n"
    "🎁 <b>Подпишись на наш канал с идеями и промптами</b> — "
    f"и получи <b>{FREE_CREDITS_FOR_SUBSCRIPTION} бесплатные генерации</b>!"
)

ALREADY_SUBSCRIBED_TEXT = (
    "Ты уже получил бесплатные генерации за подписку раньше.\n\n"
    "Ниже — главное меню."
)

SUBSCRIPTION_SUCCESS_TEXT = (
    "Отлично! Подписка подтверждена.\n"
    f"Тебе начислено <b>{FREE_CREDITS_FOR_SUBSCRIPTION} бесплатные генерации</b>.\n\n"
    "Можем начинать!"
)

NOT_SUBSCRIBED_TEXT = (
    "Кажется, ты ещё не подписался на канал.\n"
    "Подпишись и нажми «Я подписался» ещё раз."
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.clear()

    args = message.text.split(maxsplit=1)[1] if " " in message.text else ""
    referrer_id: int | None = None
    if args.startswith("ref_"):
        try:
            ref = int(args[4:])
            if ref != message.from_user.id:
                referrer_id = ref
        except ValueError:
            pass

    user = await db.get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name or "",
        referrer_id=referrer_id,
    )

    if user.get("is_blocked"):
        return

    # Process referral if this is a new user (created just now, has referrer)
    if referrer_id and not user.get("channel_subscribed"):
        # referrer_id presence means user was just created; give referral bonus
        try:
            created = await db.record_referral(referrer_id, message.from_user.id)
            if created:
                await db.add_credits(referrer_id, paid=REFERRAL_CREDITS)
                await db.add_credits(message.from_user.id, paid=REFERRAL_CREDITS)
                try:
                    await bot.send_message(
                        referrer_id,
                        f"🎉 По твоей ссылке зарегистрировался новый пользователь! "
                        f"Тебе начислено <b>{REFERRAL_CREDITS} кредита</b>.",
                        parse_mode="HTML",
                    )
                except Exception:
                    pass
        except Exception:
            pass

    # If already interacted before — show main menu right away
    if user.get("total_generated", 0) > 0 or user.get("paid_credits", 0) > 0 or user.get("free_credits", 0) > 0:
        await message.answer(
            "Добро пожаловать! Выбери, что хочешь сделать.",
            reply_markup=main_menu_kb(),
        )
        return

    # New user — show onboarding
    if user.get("channel_subscribed"):
        await message.answer(ALREADY_SUBSCRIBED_TEXT, reply_markup=main_menu_kb())
        return

    await message.answer(WELCOME_TEXT, parse_mode="HTML", reply_markup=subscribe_kb())


@router.callback_query(F.data == "subscribe:check")
async def check_subscription(callback: CallbackQuery, bot: Bot) -> None:
    user_id = callback.from_user.id
    logger.info(f"Checking subscription for user {user_id}")

    user = await db.get_user(user_id)
    if not user:
        await callback.answer("Что-то пошло не так. Нажми /start.", show_alert=True)
        return

    if user.get("channel_subscribed"):
        logger.info(f"User {user_id} already marked as subscribed in DB")
        await callback.message.edit_text(
            ALREADY_SUBSCRIBED_TEXT, reply_markup=main_menu_kb()
        )
        await callback.answer()
        return

    # Подождем немного, чтобы Telegram API обновил статус подписки
    import asyncio
    logger.info(f"Waiting 2 seconds before checking subscription for user {user_id}")
    await asyncio.sleep(2)

    subscribed = await is_subscribed(bot, user_id)
    if not subscribed:
        logger.warning(f"User {user_id} is not subscribed according to Telegram API")
        await callback.answer(NOT_SUBSCRIBED_TEXT, show_alert=True)
        return

    logger.info(f"User {user_id} successfully subscribed, updating DB")
    await db.set_channel_subscribed(user_id)
    await db.add_credits(user_id, free=FREE_CREDITS_FOR_SUBSCRIPTION)

    await callback.message.edit_text(
        SUBSCRIPTION_SUCCESS_TEXT, parse_mode="HTML", reply_markup=main_menu_kb()
    )
    await callback.answer()
