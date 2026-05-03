from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot import database as db
from bot.config import BOT_USERNAME, REFERRAL_CREDITS
from bot.keyboards.builders import profile_kb, back_to_menu_kb

router = Router()


async def _build_profile_text(user_id: int) -> str:
    user = await db.get_user(user_id)
    if not user:
        return "Профиль не найден."
    paid = user.get("paid_credits") or 0
    free = user.get("free_credits") or 0
    total_credits = paid + free
    total_gen = user.get("total_generated") or 0
    created = user["created_at"].strftime("%d.%m.%Y") if user.get("created_at") else "—"
    ref_count = await db.get_referral_count(user_id)
    credit_detail = f" (из них {free} бесплатных)" if free > 0 else ""
    return (
        f"👤 <b>Мой профиль</b>\n\n"
        f"💳 Кредитов: <b>{total_credits}</b>{credit_detail}\n"
        f"📸 Сгенерировано фото: <b>{total_gen}</b>\n"
        f"👥 Приглашено друзей: <b>{ref_count}</b>\n"
        f"📅 В боте с: {created}"
    )


@router.message(Command("profile"))
async def cmd_profile(message: Message) -> None:
    text = await _build_profile_text(message.from_user.id)
    await message.answer(text, parse_mode="HTML", reply_markup=profile_kb())


@router.callback_query(F.data == "menu:profile")
async def show_profile(callback: CallbackQuery) -> None:
    text = await _build_profile_text(callback.from_user.id)
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=profile_kb())
    await callback.answer()


@router.callback_query(F.data == "profile:referral")
async def show_referral(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    ref_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"
    ref_count = await db.get_referral_count(user_id)

    share_text = (
        f"Попробуй этот бот — делает крутые AI-фото по твоему селфи. "
        f"Вот ссылка, по ней тебе сразу дадут {REFERRAL_CREDITS} бесплатные генерации: "
        f"{ref_link}"
    )

    text = (
        f"👥 <b>Реферальная программа</b>\n\n"
        f"Приглашай друзей — оба получаете по <b>{REFERRAL_CREDITS} кредита</b>.\n\n"
        f"Твоих рефералов: <b>{ref_count}</b>\n\n"
        f"Твоя ссылка:\n<code>{ref_link}</code>\n\n"
        f"Готовый текст для пересылки:\n<i>{share_text}</i>"
    )
    await callback.message.edit_text(
        text, parse_mode="HTML", reply_markup=back_to_menu_kb()
    )
    await callback.answer()
