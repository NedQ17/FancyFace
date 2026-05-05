from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery, Message, LabeledPrice, PreCheckoutQuery,
)

from bot import database as db
from bot.config import PACKAGES, PAYMENT_PROVIDER_TOKEN
from bot.keyboards.builders import paywall_kb, after_payment_kb, back_to_menu_kb

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

NO_PROVIDER_TEXT = (
    "Оплата временно недоступна. Обратитесь к администратору."
)


def _pkg_by_id(pkg_id: str) -> dict | None:
    return next((p for p in PACKAGES if p["id"] == pkg_id), None)


@router.message(Command("pay"))
async def cmd_pay(message: Message) -> None:
    if not PAYMENT_PROVIDER_TOKEN:
        await message.answer(NO_PROVIDER_TEXT)
        return
    await message.answer(PAYWALL_TEXT, parse_mode="HTML", reply_markup=paywall_kb())


@router.callback_query(F.data == "menu:topup")
async def show_paywall(callback: CallbackQuery) -> None:
    await db.mark_paywall_shown(callback.from_user.id)

    if not PAYMENT_PROVIDER_TOKEN:
        text = (
            PAYWALL_TEXT +
            "\n\nОплата временно недоступна — платежный провайдер не настроен. "
            "Обратись к администратору или попробуй позже."
        )
        try:
            await callback.message.edit_text(
                text, parse_mode="HTML", reply_markup=back_to_menu_kb()
            )
        except Exception:
            await callback.message.answer(
                text, parse_mode="HTML", reply_markup=back_to_menu_kb()
            )
        await callback.answer()
        return

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
async def package_selected(callback: CallbackQuery, bot: Bot) -> None:
    pkg_id = callback.data.split(":")[2]
    pkg = _pkg_by_id(pkg_id)
    if not pkg:
        await callback.answer("Пакет не найден.", show_alert=True)
        return

    if not PAYMENT_PROVIDER_TOKEN:
        await callback.answer(NO_PROVIDER_TEXT, show_alert=True)
        return

    payment_id = await db.create_payment(
        user_id=callback.from_user.id,
        package_id=pkg_id,
        credits=pkg["credits"],
        amount_kopecks=pkg["price_rub"] * 100,
    )

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=pkg["label"],
        description=f"Пополнение баланса FancyFaceBot: {pkg['credits']} генераций",
        payload=str(payment_id),
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency="RUB",
        prices=[LabeledPrice(label=pkg["label"], amount=pkg["price_rub"] * 100)],
        start_parameter=f"buy_{pkg_id}",
    )
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery) -> None:
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message) -> None:
    payload = message.successful_payment.invoice_payload
    telegram_payment_id = message.successful_payment.telegram_payment_charge_id

    try:
        payment_id = int(payload)
        credits = await db.complete_payment(payment_id, telegram_payment_id)
    except Exception:
        await message.answer(
            "Оплата получена, но при начислении кредитов возникла ошибка. "
            "Напиши нам — разберёмся!",
            reply_markup=back_to_menu_kb(),
        )
        return

    await message.answer(
        f"✅ Оплата прошла! Начислено <b>{credits} генераций</b>.\n\n"
        "Можешь продолжать.",
        parse_mode="HTML",
        reply_markup=after_payment_kb(),
    )
