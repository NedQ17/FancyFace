import asyncio
import io
import logging
from collections import defaultdict

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from bot import database as db
from bot.keyboards.builders import styles_kb, after_style_kb, after_merge_kb, paywall_kb, credits_empty_kb, cancel_kb, style_addition_kb, photo_request_kb
from bot.services.generation import generate_portrait, generate_merge_portrait, upload_photo, download_image, apply_watermark, GenerationError
from bot.services import storage
from bot.states.flows import StyleFlow
from bot.utils import pending_paywall

logger = logging.getLogger(__name__)

# Per-user lock so concurrent media-group photos are processed serially
_media_group_locks: defaultdict[int, asyncio.Lock] = defaultdict(asyncio.Lock)

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


async def launch_style_for_message(message: Message, state: FSMContext, style_id: int) -> None:
    style = await db.get_style(style_id)
    if not style:
        from bot.keyboards.builders import main_menu_kb
        await message.answer("Стиль не найден.", reply_markup=main_menu_kb())
        return
    await state.set_state(StyleFlow.waiting_custom_addition)
    await state.update_data(style_id=style_id, custom_addition=None)
    label = f"{style['emoji']} {style['name']}" if style.get("emoji") else style["name"]
    await message.answer(
        f"Стиль: <b>{label}</b>\n\n{ADDITION_QUESTION}",
        parse_mode="HTML",
        reply_markup=style_addition_kb(),
    )


@router.callback_query(F.data == "menu:styles")
async def show_styles(callback: CallbackQuery, state: FSMContext) -> None:
    if await pending_paywall(callback):
        return
    await state.clear()
    styles = await db.get_styles()
    text = (
        "Выбери стиль для своего образа:\n\n"
        "<i>💡 Для парного фото — выбери стиль и отправь сразу два фото.</i>"
    )
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=styles_kb(styles, page=0))
    except Exception:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=styles_kb(styles, page=0))
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


ADDITION_QUESTION = (
    "Хочешь добавить что-то конкретное к образу?\n\n"
    "Например: <i>красное платье</i>, <i>букет цветов в руках</i>, <i>чёрные очки</i>\n\n"
    "Или отправь <b>фото фона</b> — место или сцену, куда хочешь попасть.\n\n"
    "Напиши, отправь фото, или нажми «Пропустить»."
)


@router.callback_query(F.data.startswith("style:select:"))
async def style_selected(callback: CallbackQuery, state: FSMContext) -> None:
    style_id = int(callback.data.split(":")[2])
    style = await db.get_style(style_id)
    if not style:
        await callback.answer("Стиль не найден.", show_alert=True)
        return

    await state.set_state(StyleFlow.waiting_custom_addition)
    await state.update_data(style_id=style_id)

    await callback.message.edit_text(ADDITION_QUESTION, parse_mode="HTML", reply_markup=style_addition_kb())
    await callback.answer()


@router.callback_query(F.data == "style:skip_addition")
async def skip_addition(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(custom_addition=None)
    await state.set_state(StyleFlow.waiting_photo)
    data = await state.get_data()
    await callback.message.edit_text(
        PHOTO_TIPS, parse_mode="HTML", reply_markup=photo_request_kb(data["style_id"])
    )
    await callback.answer()


@router.message(StyleFlow.waiting_custom_addition, F.text)
async def receive_addition(message: Message, state: FSMContext) -> None:
    await state.update_data(custom_addition=message.text.strip())
    await state.set_state(StyleFlow.waiting_photo)
    data = await state.get_data()
    await message.answer(PHOTO_TIPS, parse_mode="HTML", reply_markup=photo_request_kb(data["style_id"]))


@router.message(StyleFlow.waiting_custom_addition, F.photo | F.document)
async def receive_addition_bg_photo(message: Message, state: FSMContext, bot: Bot) -> None:
    photo_bytes = await _get_photo_bytes(message, bot)
    if not photo_bytes:
        await message.answer("Не удалось прочитать фото. Попробуй ещё раз.")
        return
    status_msg = await message.answer("Загружаю фото фона... ⏳")
    try:
        bg_url = await upload_photo(photo_bytes)
    except GenerationError as exc:
        await status_msg.edit_text(f"Ошибка загрузки: {exc}. Попробуй ещё раз.")
        return
    await status_msg.delete()
    await state.update_data(bg_url=bg_url)
    await state.set_state(StyleFlow.waiting_photo)
    data = await state.get_data()
    await message.answer(
        "Фото фона принято! Теперь отправь своё фото.",
        reply_markup=photo_request_kb(data["style_id"]),
    )


@router.callback_query(F.data.startswith("style:retry:"))
async def style_retry(callback: CallbackQuery, state: FSMContext) -> None:
    style_id = int(callback.data.split(":")[2])
    await state.set_state(StyleFlow.waiting_custom_addition)
    await state.update_data(style_id=style_id, custom_addition=None)
    await callback.message.answer(ADDITION_QUESTION, parse_mode="HTML", reply_markup=style_addition_kb())
    await callback.answer()


@router.message(StyleFlow.waiting_photo, F.photo | F.document)
async def style_photo_received(message: Message, state: FSMContext, bot: Bot) -> None:
    if message.media_group_id:
        async with _media_group_locks[message.from_user.id]:
            await _handle_media_group_photo(message, state, bot)
        return

    data = await state.get_data()
    style_id: int = data["style_id"]
    custom_addition: str | None = data.get("custom_addition")

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

    status_msg = await message.answer("Генерирую твой образ, скоро будет готово... ⏳")
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
    )

    prompt = style["prompt"]
    if custom_addition:
        prompt = f"{prompt}. Additional user request: {custom_addition}."

    uid = message.from_user.id
    bg_url = data.get("bg_url")
    logger.info("User %s generation started style_id=%s", uid, style_id)
    try:
        face_url = await upload_photo(photo_bytes)
        logger.info("User %s photo uploaded", uid)
        result_url = await generate_portrait(face_url, prompt, style.get("scenes") or [], bg_url=bg_url)
        logger.info("User %s generation done, downloading result", uid)
        result_bytes = await download_image(result_url)
        logger.info("User %s result downloaded (%d bytes)", uid, len(result_bytes))
    except GenerationError as exc:
        logger.error("User %s generation failed style_id=%s: %s", uid, style_id, exc)
        await db.fail_generation(gen_id)
        await db.refund_credit(message.from_user.id, credit_type)
        await status_msg.edit_text(
            "Что-то пошло не так при генерации. Кредит не списан — попробуй ещё раз или выбери другой стиль.",
            reply_markup=after_style_kb(style_id),
        )
        return

    was_free = (credit_type == "free")

    if was_free:
        watermarked_bytes = apply_watermark(result_bytes)
        result_msg = await message.answer_photo(
            BufferedInputFile(watermarked_bytes, filename="result.jpg"),
        )
        await status_msg.delete()
        logger.info("User %s watermarked result sent style_id=%s", uid, style_id)

        try:
            storage_path = await storage.upload_clean_photo(uid, result_bytes)
            await db.save_pending_unlock(uid, storage_path)
            await message.answer(
                "Нравится образ? ✨\n\n"
                "Это пробная версия с водяным знаком.\n"
                "Купи любой пакет — и получишь это фото <b>без водяного знака</b> автоматически.\n\n"
                "<i>Фото хранится 24 часа.</i>",
                parse_mode="HTML",
                reply_markup=paywall_kb(),
            )
            logger.info("User %s clean photo uploaded to storage style_id=%s", uid, style_id)
        except Exception:
            logger.exception("User %s storage upload failed — sending clean image instead", uid)
            await message.answer_photo(
                BufferedInputFile(result_bytes, filename="result.jpg"),
                caption="Готово! (не удалось сохранить для разблокировки — отправляем сразу)",
                reply_markup=after_style_kb(style_id),
            )
    else:
        result_msg = await message.answer_photo(
            BufferedInputFile(result_bytes, filename="result.jpg"),
            reply_markup=after_style_kb(style_id),
        )
        await status_msg.delete()
        logger.info("User %s result sent successfully style_id=%s", uid, style_id)

    file_id = result_msg.photo[-1].file_id
    await db.complete_generation(gen_id, [file_id], was_free)


async def _handle_media_group_photo(message: Message, state: FSMContext, bot: Bot) -> None:
    """Called under per-user lock — processes first or second photo of a 2-photo album."""
    data = await state.get_data()
    style_id: int | None = data.get("style_id")
    if not style_id:
        return  # State was cleared by a concurrent handler

    face_url1: str | None = data.get("face_url1")
    uid = message.from_user.id

    if face_url1 and data.get("merge_group_id") == message.media_group_id:
        # ── Second photo: generate merge ──────────────────────────────────────
        await state.clear()
        custom_addition: str | None = data.get("custom_addition")

        user = await db.get_user(uid)
        if not user:
            return
        total = (user["paid_credits"] or 0) + (user["bonus_credits"] or 0) + (user["free_credits"] or 0)
        if total < 1:
            await message.answer(
                "У тебя закончились кредиты. Пополни баланс, чтобы продолжить.",
                reply_markup=credits_empty_kb(),
            )
            await db.mark_paywall_shown(uid)
            return

        style = await db.get_style(style_id)
        if not style:
            return

        photo_bytes = await _get_photo_bytes(message, bot)
        if not photo_bytes:
            await message.answer("Не удалось прочитать второе фото. Попробуй ещё раз.", reply_markup=cancel_kb())
            return

        status_msg = await message.answer("Генерирую совместное фото, это займёт немного времени... ⏳")

        try:
            face_url2 = await upload_photo(photo_bytes)
        except GenerationError as exc:
            await status_msg.edit_text(f"Ошибка загрузки фото: {exc}. Попробуй ещё раз.")
            return

        prompt = style["prompt"]
        if custom_addition:
            prompt = f"{prompt}. Additional user request: {custom_addition}."

        credit_type = await db.consume_credit(uid)
        gen_id = await db.create_generation(user_id=uid, gen_type="merge", prompt=style["prompt"], style_id=style_id)

        bg_url = data.get("bg_url")
        try:
            result_url = await generate_merge_portrait(face_url1, face_url2, prompt, bg_url=bg_url)
            result_bytes = await download_image(result_url)
            logger.info("User %s merge done style_id=%s", uid, style_id)
        except GenerationError as exc:
            logger.error("User %s merge failed: %s", uid, exc)
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
            result_msg = await message.answer_photo(BufferedInputFile(watermarked_bytes, filename="merge.jpg"))
            await status_msg.delete()
            try:
                storage_path = await storage.upload_clean_photo(uid, result_bytes)
                await db.save_pending_unlock(uid, storage_path)
                await message.answer(
                    "Нравится образ? ✨\n\nЭто пробная версия с водяным знаком.\n"
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

        await db.complete_generation(gen_id, [result_msg.photo[-1].file_id], was_free)
        return

    # ── First photo: upload and wait for second ───────────────────────────────
    user = await db.get_user(uid)
    if not user:
        return
    total = (user["paid_credits"] or 0) + (user["bonus_credits"] or 0) + (user["free_credits"] or 0)
    if total < 1:
        await state.clear()
        await message.answer(
            "У тебя закончились кредиты. Пополни баланс, чтобы продолжить.",
            reply_markup=credits_empty_kb(),
        )
        await db.mark_paywall_shown(uid)
        return

    photo_bytes = await _get_photo_bytes(message, bot)
    if not photo_bytes:
        return
    try:
        face_url1 = await upload_photo(photo_bytes)
    except GenerationError as exc:
        await message.answer(f"Ошибка загрузки первого фото: {exc}. Попробуй ещё раз.", reply_markup=cancel_kb())
        return
    await state.update_data(face_url1=face_url1, merge_group_id=message.media_group_id)


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
