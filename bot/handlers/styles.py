import io
import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, URLInputFile

from bot import database as db
from bot.keyboards.builders import styles_kb, after_style_kb, paywall_kb, credits_empty_kb, cancel_kb
from bot.services.generation import generate_portrait, upload_photo, GenerationError

logger = logging.getLogger(__name__)
from bot.states.flows import StyleFlow

router = Router()

PHOTO_TIPS = (
    "Отлично! Теперь отправь своё фото.\n\n"
    "<b>Советы для лучшего результата:</b>\n"
    "• Лицо должно быть чётким и хорошо освещённым\n"
    "• Смотри в камеру или чуть в сторону\n"
    "• Избегай солнечных очков и масок\n"
    "• Подойдёт обычное селфи или портретное фото\n\n"
    "Чем качественнее исходник — тем лучше результат."
)


@router.callback_query(F.data == "menu:styles")
async def show_styles(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    styles = await db.get_styles()
    try:
        await callback.message.edit_text(
            "Выбери стиль для своего образа:",
            reply_markup=styles_kb(styles, page=0),
        )
    except Exception:
        await callback.message.answer(
            "Выбери стиль для своего образа:",
            reply_markup=styles_kb(styles, page=0),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("style:page:"))
async def styles_page(callback: CallbackQuery) -> None:
    page = int(callback.data.split(":")[2])
    styles = await db.get_styles()
    await callback.message.edit_reply_markup(reply_markup=styles_kb(styles, page=page))
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(F.data.startswith("style:select:"))
async def style_selected(callback: CallbackQuery, state: FSMContext) -> None:
    style_id = int(callback.data.split(":")[2])
    style = await db.get_style(style_id)
    if not style:
        await callback.answer("Стиль не найден.", show_alert=True)
        return

    await state.set_state(StyleFlow.waiting_photo)
    await state.update_data(style_id=style_id)

    await callback.message.edit_text(PHOTO_TIPS, parse_mode="HTML", reply_markup=cancel_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("style:retry:"))
async def style_retry(callback: CallbackQuery, state: FSMContext) -> None:
    style_id = int(callback.data.split(":")[2])
    await state.set_state(StyleFlow.waiting_photo)
    await state.update_data(style_id=style_id)
    await callback.message.answer(PHOTO_TIPS, parse_mode="HTML", reply_markup=cancel_kb())
    await callback.answer()


@router.message(StyleFlow.waiting_photo, F.photo | F.document)
async def style_photo_received(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    style_id: int = data["style_id"]

    user = await db.get_user(message.from_user.id)
    if not user:
        return

    total = (user["paid_credits"] or 0) + (user["free_credits"] or 0)
    if total < 1:
        await state.clear()
        await message.answer(
            "У тебя закончились кредиты. Пополни баланс, чтобы продолжить.",
            reply_markup=credits_empty_kb(),
        )
        await db.mark_paywall_shown(message.from_user.id)
        return

    style = await db.get_style(style_id)
    if not style:
        await state.clear()
        return

    status_msg = await message.answer("Генерирую твой образ, подожди 20–30 секунд... ⏳")
    await state.clear()

    photo_bytes = await _get_photo_bytes(message, bot)
    if not photo_bytes:
        await status_msg.edit_text("Не удалось прочитать фото. Попробуй ещё раз.")
        return

    credit_type = await db.consume_credit(message.from_user.id)
    gen_id = await db.create_generation(
        user_id=message.from_user.id,
        gen_type="style",
        prompt=style["prompt"],
        style_id=style_id,
        source_file_id=_get_file_id(message),
    )

    try:
        face_url = await upload_photo(photo_bytes)
        result_url = await generate_portrait(face_url, style["prompt"], style.get("scenes") or [])
    except GenerationError as exc:
        logger.error("Generation failed for user %s, style %s: %s", message.from_user.id, style_id, exc)
        await db.fail_generation(gen_id)
        await db.refund_credit(message.from_user.id, credit_type)
        await status_msg.edit_text(
            "Что-то пошло не так при генерации. Кредит не списан — попробуй ещё раз или выбери другой стиль.",
            reply_markup=after_style_kb(style_id),
        )
        return

    was_free = credit_type == "free"
    result_msg = await message.answer_photo(
        URLInputFile(result_url, filename="result.jpg"),
        reply_markup=after_style_kb(style_id),
    )
    await status_msg.delete()

    file_id = result_msg.photo[-1].file_id
    await db.complete_generation(gen_id, [file_id], was_free)


async def _get_photo_bytes(message: Message, bot: Bot) -> bytes | None:
    try:
        if message.photo:
            file = await bot.get_file(message.photo[-1].file_id)
        elif message.document and (message.document.mime_type or "").startswith("image/"):
            file = await bot.get_file(message.document.file_id)
        else:
            return None
        buf = io.BytesIO()
        await bot.download_file(file.file_path, destination=buf)
        return buf.getvalue()
    except Exception:
        return None


def _get_file_id(message: Message) -> str | None:
    if message.photo:
        return message.photo[-1].file_id
    if message.document:
        return message.document.file_id
    return None
