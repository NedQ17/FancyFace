import asyncio
import io
import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from bot import database as db
from bot.keyboards.builders import (
    sessions_kb, session_detail_kb, after_session_kb, paywall_kb, credits_empty_kb, cancel_kb,
)
from bot.services.generation import generate_portrait, upload_photo, download_image, GenerationError
from bot.states.flows import SessionFlow

router = Router()
logger = logging.getLogger(__name__)

PHOTO_TIPS = (
    "Хорошо, начинаем фотосессию!\n\n"
    "Для лучшего результата отправь чёткое портретное фото. "
    "Лицо должно быть хорошо освещено и занимать большую часть кадра — "
    "это поможет правильно перенести твои черты в новый образ.\n\n"
    "<b>Избегай:</b> групповых фото, тёмных снимков, фото в профиль.\n\n"
    "Жду твоё фото!"
)


@router.callback_query(F.data == "menu:sessions")
async def show_sessions(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    sessions = await db.get_sessions()
    await callback.message.edit_text(
        "Выбери фотосессию:",
        reply_markup=sessions_kb(sessions),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("session:select:"))
async def session_selected(callback: CallbackQuery) -> None:
    session_id = int(callback.data.split(":")[2])
    session = await db.get_session(session_id)
    if not session:
        await callback.answer("Сессия не найдена.", show_alert=True)
        return

    text = (
        f"<b>{session['name']}</b>\n\n"
        f"{session['description']}\n\n"
        f"📸 Количество фото: <b>{session['photo_count']}</b>\n"
        f"💳 Спишется кредитов: <b>{session['photo_count']}</b>"
    )
    await callback.message.edit_text(
        text, parse_mode="HTML", reply_markup=session_detail_kb(session_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("session:start:"))
async def session_start(callback: CallbackQuery, state: FSMContext) -> None:
    session_id = int(callback.data.split(":")[2])
    session = await db.get_session(session_id)
    if not session:
        await callback.answer("Сессия не найдена.", show_alert=True)
        return

    user = await db.get_user(callback.from_user.id)
    total = (user["paid_credits"] or 0) + (user["free_credits"] or 0)
    needed = session["photo_count"]

    if total < needed:
        await callback.message.edit_text(
            f"Для этой фотосессии нужно <b>{needed} кредита</b>, "
            f"а у тебя <b>{total}</b>.\n\nПополни баланс, чтобы продолжить.",
            parse_mode="HTML",
            reply_markup=credits_empty_kb(),
        )
        await db.mark_paywall_shown(callback.from_user.id)
        await callback.answer()
        return

    await state.set_state(SessionFlow.waiting_photo)
    await state.update_data(session_id=session_id)

    await callback.message.edit_text(
        PHOTO_TIPS, parse_mode="HTML", reply_markup=cancel_kb()
    )
    await callback.answer()


@router.message(SessionFlow.waiting_photo, F.photo | F.document)
async def session_photo_received(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    session_id: int = data["session_id"]

    session = await db.get_session(session_id)
    if not session:
        await state.clear()
        return

    user = await db.get_user(message.from_user.id)
    needed = session["photo_count"]
    total = (user["paid_credits"] or 0) + (user["free_credits"] or 0)

    if total < needed:
        await state.clear()
        await message.answer(
            f"Недостаточно кредитов для фотосессии ({needed} нужно, {total} есть).",
            reply_markup=credits_empty_kb(),
        )
        await db.mark_paywall_shown(message.from_user.id)
        return

    await state.clear()

    status_msg = await message.answer(
        "Создаю твою фотосессию... Это займёт немного больше времени — "
        "генерирую несколько фото. Первое уже скоро! ⏳"
    )

    photo_bytes = await _get_photo_bytes(message, bot)
    if not photo_bytes:
        await status_msg.edit_text("Не удалось прочитать фото. Попробуй ещё раз.")
        return

    uid = message.from_user.id
    face_url = None
    try:
        logger.info("User %s uploading photo for session_id=%s", uid, session_id)
        face_url = await upload_photo(photo_bytes)
        logger.info("User %s photo uploaded", uid)
    except GenerationError:
        await status_msg.edit_text(
            "Не удалось загрузить фото. Попробуй ещё раз.",
            reply_markup=cancel_kb(),
        )
        return

    prompts: list[str] = session["prompts"]
    gen_id = await db.create_generation(
        user_id=uid,
        gen_type="session",
        prompt=session["name"],
        session_id=session_id,
    )

    result_file_ids: list[str] = []
    used_free = False

    for i, prompt in enumerate(prompts, 1):
        credit_type = await db.consume_credit(uid)
        if credit_type == "free":
            used_free = True
        try:
            logger.info("User %s generating photo %s/%s session_id=%s", uid, i, len(prompts), session_id)
            result_url = await generate_portrait(face_url, prompt)
            logger.info("User %s photo %s/%s done, downloading", uid, i, len(prompts))
        except GenerationError:
            await db.refund_credit(uid, credit_type)
            await message.answer(f"Фото {i}/{len(prompts)} не удалось сгенерировать. Пропускаем.")
            continue

        try:
            result_bytes = await download_image(result_url)
            result_msg = await message.answer_photo(
                BufferedInputFile(result_bytes, filename=f"photo_{i}.jpg")
            )
            logger.info("User %s photo %s/%s sent", uid, i, len(prompts))
        except Exception:
            logger.exception("User %s failed to send photo %s/%s", uid, i, len(prompts))
            await db.refund_credit(uid, credit_type)
            continue

        result_file_ids.append(result_msg.photo[-1].file_id)

        if i < len(prompts):
            await asyncio.sleep(0.5)

    await db.complete_generation(gen_id, result_file_ids, was_free=used_free)

    if result_file_ids:
        await message.answer(
            "Фотосессия готова! Сохраняй понравившиеся. 🎉",
            reply_markup=after_session_kb(),
        )
    else:
        await message.answer(
            "К сожалению, не удалось сгенерировать ни одного фото. Кредиты не списаны.",
            reply_markup=after_session_kb(),
        )

    try:
        await status_msg.delete()
    except Exception:
        pass


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
        logger.exception("Failed to download photo from user %s", message.from_user.id)
        return None


def _get_file_id(message: Message) -> str | None:
    if message.photo:
        return message.photo[-1].file_id
    if message.document:
        return message.document.file_id
    return None
