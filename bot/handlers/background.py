import asyncio
import io
import logging
from collections import defaultdict

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from bot import database as db
from bot.keyboards.builders import after_bg_kb, paywall_kb, credits_empty_kb, cancel_kb, bg_skip_prompt_kb
from bot.utils import pending_paywall
from bot.services.generation import (
    generate_portrait, generate_merge_portrait, upload_photo, download_image,
    apply_watermark, GenerationError,
)
from bot.services import storage
from bot.states.flows import BackgroundFlow

logger = logging.getLogger(__name__)
router = Router()

_media_group_locks: defaultdict[int, asyncio.Lock] = defaultdict(asyncio.Lock)

_BASE_PROMPT = (
    "candid photo shot on iPhone, person naturally placed in the scene, "
    "sharp background, no bokeh, no depth of field, no background blur, "
    "everything in focus, natural colors, casual snapshot, no studio lighting, no AI look"
)

_PORTRAIT_TIPS = (
    "Теперь отправь своё фото.\n\n"
    "• Лицо должно быть чётким и хорошо освещённым\n"
    "• Смотри в камеру или чуть в сторону\n"
    "• Без очков и масок\n\n"
    "<i>💡 Для парного фото — отправь два фото сразу.</i>"
)


@router.callback_query(F.data == "menu:background")
async def start_background(callback: CallbackQuery, state: FSMContext) -> None:
    if await pending_paywall(callback):
        return
    await state.clear()
    await state.set_state(BackgroundFlow.waiting_bg_photo)
    try:
        await callback.message.edit_text(
            "Отправь фото фона — место или сцену, куда хочешь попасть.",
            reply_markup=cancel_kb(),
        )
    except Exception:
        await callback.message.answer(
            "Отправь фото фона — место или сцену, куда хочешь попасть.",
            reply_markup=cancel_kb(),
        )
    await callback.answer()


@router.message(BackgroundFlow.waiting_bg_photo, F.photo | F.document)
async def bg_photo_received(message: Message, state: FSMContext, bot: Bot) -> None:
    photo_bytes = await _get_photo_bytes(message, bot)
    if not photo_bytes:
        await message.answer("Не удалось прочитать фото. Попробуй ещё раз.", reply_markup=cancel_kb())
        return

    status_msg = await message.answer("Загружаю фото фона... ⏳")
    try:
        bg_url = await upload_photo(photo_bytes)
    except GenerationError as exc:
        await status_msg.edit_text(f"Ошибка загрузки: {exc}. Попробуй ещё раз.")
        return

    await status_msg.delete()
    await state.update_data(bg_url=bg_url)
    await state.set_state(BackgroundFlow.waiting_custom_prompt)
    await message.answer(
        "Фото фона принято! ✅\n\n"
        "Хочешь добавить пожелания к образу?\n\n"
        "Например: <i>красное платье</i>, <i>улыбка</i>, <i>деловой стиль</i>\n\n"
        "Напиши или нажми «Пропустить».",
        parse_mode="HTML",
        reply_markup=bg_skip_prompt_kb(),
    )


@router.message(BackgroundFlow.waiting_custom_prompt, F.text)
async def bg_custom_prompt_received(message: Message, state: FSMContext) -> None:
    await state.update_data(custom_prompt=message.text.strip())
    await state.set_state(BackgroundFlow.waiting_photo)
    await message.answer(_PORTRAIT_TIPS, parse_mode="HTML", reply_markup=cancel_kb())


@router.callback_query(BackgroundFlow.waiting_custom_prompt, F.data == "bg:skip_prompt")
async def bg_skip_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(custom_prompt=None)
    await state.set_state(BackgroundFlow.waiting_photo)
    await callback.message.edit_text(_PORTRAIT_TIPS, parse_mode="HTML", reply_markup=cancel_kb())
    await callback.answer()


@router.message(BackgroundFlow.waiting_photo, F.photo | F.document)
async def bg_portrait_received(message: Message, state: FSMContext, bot: Bot) -> None:
    if message.media_group_id:
        async with _media_group_locks[message.from_user.id]:
            await _handle_media_group(message, state, bot)
        return

    data = await state.get_data()
    await state.clear()
    bg_url = data.get("bg_url")
    if not bg_url:
        return

    uid = message.from_user.id
    user = await db.get_user(uid)
    if not user:
        return
    total = (user["paid_credits"] or 0) + (user["bonus_credits"] or 0) + (user["free_credits"] or 0)
    if total < 1:
        await message.answer("У тебя закончились кредиты. Пополни баланс.", reply_markup=credits_empty_kb())
        await db.mark_paywall_shown(uid)
        return

    photo_bytes = await _get_photo_bytes(message, bot)
    if not photo_bytes:
        await message.answer("Не удалось прочитать фото. Попробуй ещё раз.", reply_markup=cancel_kb())
        return

    custom_prompt = data.get("custom_prompt")
    prompt = _BASE_PROMPT
    if custom_prompt:
        prompt = f"{prompt}. Additional user request: {custom_prompt}."

    status_msg = await message.answer("Генерирую твой образ, скоро будет готово... ⏳")
    credit_type = await db.consume_credit(uid)
    gen_id = await db.create_generation(user_id=uid, gen_type="background", prompt=bg_url)

    try:
        portrait_url = await upload_photo(photo_bytes)
        result_url = await generate_portrait(portrait_url, prompt, bg_url=bg_url)
        result_bytes = await download_image(result_url)
        logger.info("User %s bg done", uid)
    except GenerationError as exc:
        logger.error("User %s bg failed: %s", uid, exc)
        await db.fail_generation(gen_id)
        await db.refund_credit(uid, credit_type)
        await status_msg.edit_text(
            "Что-то пошло не так. Кредит не списан — попробуй ещё раз.",
            reply_markup=after_bg_kb(),
        )
        return

    await _send_result(message, status_msg, result_bytes, uid, gen_id, credit_type)


async def _handle_media_group(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    bg_url = data.get("bg_url")
    if not bg_url:
        return

    uid = message.from_user.id
    face_url1: str | None = data.get("face_url1")

    if face_url1 and data.get("merge_group_id") == message.media_group_id:
        # Second photo → generate pair on custom background
        await state.clear()

        user = await db.get_user(uid)
        if not user:
            return
        total = (user["paid_credits"] or 0) + (user["bonus_credits"] or 0) + (user["free_credits"] or 0)
        if total < 1:
            await message.answer("У тебя закончились кредиты.", reply_markup=credits_empty_kb())
            await db.mark_paywall_shown(uid)
            return

        photo_bytes = await _get_photo_bytes(message, bot)
        if not photo_bytes:
            await message.answer("Не удалось прочитать второе фото. Попробуй ещё раз.", reply_markup=cancel_kb())
            return

        status_msg = await message.answer("Генерирую совместное фото... ⏳")
        try:
            face_url2 = await upload_photo(photo_bytes)
        except GenerationError as exc:
            await status_msg.edit_text(f"Ошибка загрузки: {exc}. Попробуй ещё раз.")
            return

        custom_prompt = data.get("custom_prompt")
        prompt = _BASE_PROMPT
        if custom_prompt:
            prompt = f"{prompt}. Additional user request: {custom_prompt}."

        credit_type = await db.consume_credit(uid)
        gen_id = await db.create_generation(user_id=uid, gen_type="background_merge", prompt=bg_url)

        try:
            result_url = await generate_merge_portrait(
                face_url1, face_url2,
                prompt,
                bg_url=bg_url,
            )
            result_bytes = await download_image(result_url)
            logger.info("User %s bg merge done", uid)
        except GenerationError as exc:
            logger.error("User %s bg merge failed: %s", uid, exc)
            await db.fail_generation(gen_id)
            await db.refund_credit(uid, credit_type)
            await status_msg.edit_text(
                "Что-то пошло не так. Кредит не списан — попробуй ещё раз.",
                reply_markup=after_bg_kb(),
            )
            return

        await _send_result(message, status_msg, result_bytes, uid, gen_id, credit_type)
        return

    # First photo → upload and wait for second
    user = await db.get_user(uid)
    if not user:
        return
    total = (user["paid_credits"] or 0) + (user["bonus_credits"] or 0) + (user["free_credits"] or 0)
    if total < 1:
        await state.clear()
        await message.answer("У тебя закончились кредиты.", reply_markup=credits_empty_kb())
        await db.mark_paywall_shown(uid)
        return

    photo_bytes = await _get_photo_bytes(message, bot)
    if not photo_bytes:
        return
    try:
        face_url1 = await upload_photo(photo_bytes)
    except GenerationError as exc:
        await message.answer(f"Ошибка загрузки: {exc}. Попробуй ещё раз.", reply_markup=cancel_kb())
        return
    await state.update_data(face_url1=face_url1, merge_group_id=message.media_group_id)


async def _send_result(
    message: Message,
    status_msg: Message,
    result_bytes: bytes,
    uid: int,
    gen_id: int,
    credit_type: str,
) -> None:
    was_free = (credit_type == "free")
    if was_free:
        watermarked = apply_watermark(result_bytes)
        result_msg = await message.answer_photo(BufferedInputFile(watermarked, filename="result.jpg"))
        await status_msg.delete()
        try:
            path = await storage.upload_clean_photo(uid, result_bytes)
            await db.save_pending_unlock(uid, path)
            await message.answer(
                "Нравится образ? ✨\n\nЭто пробная версия с водяным знаком.\n"
                "Купи любой пакет — и получишь фото <b>без водяного знака</b> автоматически.\n\n"
                "<i>Фото хранится 24 часа.</i>",
                parse_mode="HTML",
                reply_markup=paywall_kb(),
            )
        except Exception:
            logger.exception("User %s bg storage upload failed", uid)
            await message.answer_photo(
                BufferedInputFile(result_bytes, filename="result.jpg"),
                reply_markup=after_bg_kb(),
            )
    else:
        result_msg = await message.answer_photo(
            BufferedInputFile(result_bytes, filename="result.jpg"),
            reply_markup=after_bg_kb(),
        )
        await status_msg.delete()

    await db.complete_generation(gen_id, [result_msg.photo[-1].file_id], was_free)


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
