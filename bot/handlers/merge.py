import io
import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from bot import database as db
from bot.keyboards.builders import (
    merge_styles_kb, after_merge_kb, paywall_kb, credits_empty_kb, cancel_kb,
)
from bot.services.generation import (
    generate_merge_portrait, upload_photo, download_image, apply_watermark, GenerationError,
)
from bot.services import storage
from bot.states.flows import MergeFlow

logger = logging.getLogger(__name__)

router = Router()

_PHOTO1_TIPS = (
    "Отправь фото <b>первого человека</b>.\n\n"
    "• Лицо должно быть чётким и хорошо освещённым\n"
    "• Смотри прямо в камеру\n"
    "• Без очков и масок"
)

_PHOTO2_TIPS = (
    "Отлично! Теперь отправь фото <b>второго человека</b>.\n\n"
    "• Те же требования: чёткое лицо, без очков\n"
    "• Чем лучше фото — тем точнее результат"
)


@router.callback_query(F.data.startswith("style:pair:"))
async def style_start_pair(callback: CallbackQuery, state: FSMContext) -> None:
    style_id = int(callback.data.split(":")[2])
    style = await db.get_style(style_id)
    if not style:
        await callback.answer("Стиль не найден.", show_alert=True)
        return
    await state.set_state(MergeFlow.waiting_photo1)
    await state.update_data(style_id=style_id)
    label = f"{style['emoji']} {style['name']}" if style.get("emoji") else style["name"]
    await callback.message.edit_text(
        f"Стиль: <b>{label}</b>\n\n{_PHOTO1_TIPS}",
        parse_mode="HTML",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:merge")
async def start_merge(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    styles = await db.get_styles()
    try:
        await callback.message.edit_text(
            "Выбери стиль для совместного фото:",
            reply_markup=merge_styles_kb(styles, page=0),
        )
    except Exception:
        await callback.message.answer(
            "Выбери стиль для совместного фото:",
            reply_markup=merge_styles_kb(styles, page=0),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("merge:page:"))
async def merge_styles_page(callback: CallbackQuery) -> None:
    page = int(callback.data.split(":")[2])
    styles = await db.get_styles()
    await callback.message.edit_reply_markup(reply_markup=merge_styles_kb(styles, page=page))
    await callback.answer()


@router.callback_query(F.data.startswith("merge:style:"))
async def merge_style_selected(callback: CallbackQuery, state: FSMContext) -> None:
    style_id = int(callback.data.split(":")[2])
    style = await db.get_style(style_id)
    if not style:
        await callback.answer("Стиль не найден.", show_alert=True)
        return
    await state.set_state(MergeFlow.waiting_photo1)
    await state.update_data(style_id=style_id)
    label = f"{style['emoji']} {style['name']}" if style.get("emoji") else style["name"]
    await callback.message.edit_text(
        f"Стиль: <b>{label}</b>\n\n{_PHOTO1_TIPS}",
        parse_mode="HTML",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("merge:retry:"))
async def merge_retry(callback: CallbackQuery, state: FSMContext) -> None:
    style_id = int(callback.data.split(":")[2])
    style = await db.get_style(style_id)
    if not style:
        await callback.answer("Стиль не найден.", show_alert=True)
        return
    await state.set_state(MergeFlow.waiting_photo1)
    await state.update_data(style_id=style_id)
    await callback.message.answer(
        _PHOTO1_TIPS,
        parse_mode="HTML",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(MergeFlow.waiting_photo1, F.photo | F.document)
async def merge_photo1_received(message: Message, state: FSMContext, bot: Bot) -> None:
    user = await db.get_user(message.from_user.id)
    if not user:
        return
    total = (user["paid_credits"] or 0) + (user["bonus_credits"] or 0) + (user["free_credits"] or 0)
    if total < 1:
        await state.clear()
        await message.answer(
            "У тебя закончились кредиты. Пополни баланс, чтобы продолжить.",
            reply_markup=credits_empty_kb(),
        )
        await db.mark_paywall_shown(message.from_user.id)
        return

    photo_bytes = await _get_photo_bytes(message, bot)
    if not photo_bytes:
        await message.answer("Не удалось прочитать фото. Попробуй ещё раз.", reply_markup=cancel_kb())
        return

    status_msg = await message.answer("Загружаю первое фото... ⏳")
    try:
        face_url1 = await upload_photo(photo_bytes)
    except GenerationError as exc:
        await status_msg.edit_text(f"Ошибка загрузки фото: {exc}. Попробуй ещё раз.")
        return

    await status_msg.delete()
    await state.update_data(face_url1=face_url1)
    await state.set_state(MergeFlow.waiting_photo2)
    await message.answer(_PHOTO2_TIPS, parse_mode="HTML", reply_markup=cancel_kb())


@router.message(MergeFlow.waiting_photo2, F.photo | F.document)
async def merge_photo2_received(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    await state.clear()  # Clear immediately so extra photos from album don't re-enter
    style_id: int | None = data.get("style_id")
    face_url1: str | None = data.get("face_url1")
    if not style_id or not face_url1:
        return

    user = await db.get_user(message.from_user.id)
    if not user:
        return
    total = (user["paid_credits"] or 0) + (user["bonus_credits"] or 0) + (user["free_credits"] or 0)
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

    photo_bytes = await _get_photo_bytes(message, bot)
    if not photo_bytes:
        await message.answer("Не удалось прочитать фото. Попробуй ещё раз.", reply_markup=cancel_kb())
        return

    status_msg = await message.answer("Генерирую совместное фото, это займёт немного времени... ⏳")
    uid = message.from_user.id
    try:
        face_url2 = await upload_photo(photo_bytes)
        logger.info("User %s merge: both photos uploaded", uid)
    except GenerationError as exc:
        await status_msg.edit_text(f"Ошибка загрузки фото: {exc}. Попробуй ещё раз.")
        return

    credit_type = await db.consume_credit(uid)
    gen_id = await db.create_generation(
        user_id=uid,
        gen_type="merge",
        prompt=style["prompt"],
        style_id=style_id,
    )

    try:
        result_url = await generate_merge_portrait(face_url1, face_url2, style["prompt"])
        logger.info("User %s merge generation done", uid)
        result_bytes = await download_image(result_url)
    except GenerationError as exc:
        logger.error("User %s merge generation failed: %s", uid, exc)
        await db.fail_generation(gen_id)
        await db.refund_credit(uid, credit_type)
        await status_msg.edit_text(
            "Что-то пошло не так при генерации. Кредит не списан — попробуй ещё раз.",
            reply_markup=after_merge_kb(style_id),
        )
        return

    was_free = (credit_type == "free")

    if was_free:
        watermarked_bytes = apply_watermark(result_bytes)
        result_msg = await message.answer_photo(
            BufferedInputFile(watermarked_bytes, filename="merge.jpg"),
        )
        await status_msg.delete()
        try:
            storage_path = await storage.upload_clean_photo(uid, result_bytes)
            await db.save_pending_unlock(uid, storage_path)
            await message.answer(
                "Нравится образ? ✨\n\n"
                "Это пробная версия с водяным знаком.\n"
                "Купи любой пакет — и получишь фото <b>без водяного знака</b> автоматически.\n\n"
                "<i>Фото хранится 24 часа.</i>",
                parse_mode="HTML",
                reply_markup=paywall_kb(),
            )
        except Exception:
            logger.exception("User %s merge storage upload failed", uid)
            await message.answer_photo(
                BufferedInputFile(result_bytes, filename="merge.jpg"),
                caption="Готово!",
                reply_markup=after_merge_kb(style_id),
            )
    else:
        result_msg = await message.answer_photo(
            BufferedInputFile(result_bytes, filename="merge.jpg"),
            reply_markup=after_merge_kb(style_id),
        )
        await status_msg.delete()
        logger.info("User %s merge result sent style_id=%s", uid, style_id)

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
