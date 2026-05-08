import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import database as db
from bot.config import PACKAGES
from bot.keyboards.builders import paywall_kb, back_to_menu_kb
from bot.services.robokassa import build_payment_url

logger = logging.getLogger(__name__)
router = Router()

PAYWALL_TEXT = (
    "✨ <b>Создавай AI-фото в любом образе — от моды до кино</b>\n\n"
    "Каждая генерация — одно готовое фото в выбранном стиле.\n"
    "Чем больше фото — тем выгоднее!\n\n"
    "📦 <b>Тарифы:</b>\n"
    "5 фото — 139 ₽ → попробуй и оцени\n"
    "🔥 10 фото — 199 ₽ → лучший старт\n"
    "50 фото — 499 ₽ → для экспериментов со стилями\n"
    "💎 100 фото — 899 ₽ → максимум свободы и творчества\n\n"
    "👇 Выбери тариф и начни прямо сейчас!"
)


def _pkg_by_id(pkg_id: str) -> dict | None:
    return next((p for p in PACKAGES if p["id"] == pkg_id), None)


@router.message(Command("pay"))
async def cmd_pay(message: Message) -> None:
    await message.answer(PAYWALL_TEXT, parse_mode="HTML", reply_markup=paywall_kb())


@router.callback_query(F.data == "menu:topup")
async def show_paywall(callback: CallbackQuery) -> None:
    await db.mark_paywall_shown(callback.from_user.id)
    try:
        await callback.message.edit_text(
            PAYWALL_TEXT, parse_mode="HTML", reply_markup=paywall_kb()
        )
    except Exception:
        await callback.message.answer(
            PAYWALL_TEXT, parse_mode="HTML", reply_markup=paywall_kb()
        )
    await callback.answer()


@router.callback_query(F.data == "pay:back")
async def paywall_back(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        PAYWALL_TEXT, parse_mode="HTML", reply_markup=paywall_kb()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pay:pkg:"))
async def package_selected(callback: CallbackQuery) -> None:
    uid = callback.from_user.id
    pkg_id = callback.data.split(":")[2]
    pkg = _pkg_by_id(pkg_id)
    if not pkg:
        logger.warning("User %s selected unknown package_id=%s", uid, pkg_id)
        await callback.answer("Пакет не найден.", show_alert=True)
        return

    payment_id = await db.create_payment(
        user_id=uid,
        package_id=pkg_id,
        credits=pkg["credits"],
        amount_kopecks=pkg["price_rub"] * 100,
    )
    logger.info(
        "User %s payment created payment_id=%s package=%s credits=%s amount=%s RUB",
        uid, payment_id, pkg_id, pkg["credits"], pkg["price_rub"],
    )

    url = build_payment_url(
        payment_id=payment_id,
        amount_rub=float(pkg["price_rub"]),
        description=f"FancyFaceBot: {pkg['credits']} генераций",
        user_id=uid,
    )

    kb = InlineKeyboardBuilder()
    kb.button(text=f"Оплатить {pkg['price_rub']} ₽", url=url)
    kb.button(text="← Назад к тарифам", callback_data="pay:back")
    kb.adjust(1)

    try:
        await callback.message.edit_text(
            f"Пакет: <b>{pkg['label']}</b>\n\nНажми кнопку — откроется страница оплаты.",
            parse_mode="HTML",
            reply_markup=kb.as_markup(),
        )
    except Exception:
        await callback.message.answer(
            f"Пакет: <b>{pkg['label']}</b>\n\nНажми кнопку — откроется страница оплаты.",
            parse_mode="HTML",
            reply_markup=kb.as_markup(),
        )
    await callback.answer()
