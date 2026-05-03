import io

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, BufferedInputFile

from bot import database as db
from bot.keyboards.builders import (
    custom_mode_kb, custom_who_kb, custom_gender_kb, custom_style_kb,
    custom_location_kb, custom_details_skip_kb, custom_review_kb,
    after_custom_kb, paywall_kb, cancel_kb,
)
from bot.services.generation import generate_portrait, upload_photo, GenerationError
from bot.services.watermark import add_watermark
from bot.states.flows import CustomFlow

router = Router()

PHOTO_TIPS = (
    "Почти готово! Осталось прислать своё фото.\n\n"
    "Для точной передачи черт лица используй чёткое портретное фото при хорошем освещении. "
    "Анфас или лёгкий поворот — лучший вариант.\n\n"
    "<b>Без очков, без фильтров, без группового фото.</b>"
)

WHO_MAP = {
    "one": "один человек",
    "group": "несколько взрослых",
    "family": "взрослые и дети",
    "kids": "дети",
}
GENDER_MAP = {
    "female": "женщина",
    "male": "мужчина",
    "skip": "",
}
STYLE_MAP = {
    "business": "professional business style",
    "fashion": "high fashion editorial style",
    "art": "fine art artistic style",
    "realism": "photorealistic documentary style",
    "fantasy": "epic fantasy style",
}
LOCATION_MAP = {
    "office": "modern office background",
    "nature": "natural outdoor nature background",
    "city": "urban city street background",
    "studio": "professional studio background",
}


def _assemble_prompt(data: dict) -> str:
    parts = []
    gender = GENDER_MAP.get(data.get("gender", ""), "")
    if gender:
        parts.append(gender)
    style = STYLE_MAP.get(data.get("style", "realism"), "photorealistic")
    parts.append(f"{style} portrait")
    loc = data.get("location") or LOCATION_MAP.get(data.get("loc_key", ""), "")
    if loc:
        parts.append(loc)
    details = data.get("details", "")
    if details:
        parts.append(details)
    parts.append("photorealistic, high quality")
    return ", ".join(parts)


def _describe_prompt(data: dict) -> str:
    lines = []
    who = WHO_MAP.get(data.get("who", "one"), "один человек")
    gender = GENDER_MAP.get(data.get("gender", "skip"), "")
    style_key = data.get("style", "realism")
    style_names = {
        "business": "Деловой", "fashion": "Модный",
        "art": "Арт", "realism": "Реализм", "fantasy": "Фэнтези",
    }
    loc_names = {
        "office": "Офис", "nature": "Природа",
        "city": "Город", "studio": "Студия",
    }
    loc = data.get("location") or loc_names.get(data.get("loc_key", ""), "")
    details = data.get("details", "")

    lines.append(f"👤 Кто: {who}")
    if gender:
        lines.append(f"⚤ Пол: {gender}")
    lines.append(f"🎨 Стиль: {style_names.get(style_key, style_key)}")
    if loc:
        lines.append(f"📍 Локация: {loc}")
    if details:
        lines.append(f"✏️ Детали: {details}")
    return "\n".join(lines)


# ─── Entry ────────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "menu:custom")
async def custom_entry(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "Как хочешь создать образ?", reply_markup=custom_mode_kb()
    )
    await callback.answer()


# ─── Direct prompt ────────────────────────────────────────────────────────────

@router.callback_query(F.data == "custom:direct")
async def custom_direct(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CustomFlow.waiting_direct_prompt)
    await callback.message.edit_text(
        "Опиши желаемый образ текстом. Например:\n"
        "<i>«деловой портрет в сером костюме на фоне офиса»</i>\n\n"
        "Чем подробнее — тем лучше результат.",
        parse_mode="HTML",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(CustomFlow.waiting_direct_prompt, F.text)
async def custom_direct_prompt_received(message: Message, state: FSMContext) -> None:
    await state.update_data(prompt=message.text)
    await state.set_state(CustomFlow.waiting_photo)
    await message.answer(PHOTO_TIPS, parse_mode="HTML", reply_markup=cancel_kb())


# ─── Builder ──────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "custom:builder")
@router.callback_query(F.data == "custom:restart")
async def custom_builder_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CustomFlow.step1_who)
    await state.update_data({})
    await callback.message.edit_text(
        "<b>Шаг 1 из 5</b> — Кто на фото?", parse_mode="HTML",
        reply_markup=custom_who_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("custom:who:"))
async def custom_step1(callback: CallbackQuery, state: FSMContext) -> None:
    who = callback.data.split(":")[2]
    await state.update_data(who=who)
    await state.set_state(CustomFlow.step2_gender)
    await callback.message.edit_text(
        "<b>Шаг 2 из 5</b> — Пол:", parse_mode="HTML",
        reply_markup=custom_gender_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("custom:gender:"))
async def custom_step2(callback: CallbackQuery, state: FSMContext) -> None:
    gender = callback.data.split(":")[2]
    await state.update_data(gender=gender)
    await state.set_state(CustomFlow.step3_style)
    await callback.message.edit_text(
        "<b>Шаг 3 из 5</b> — Стиль:", parse_mode="HTML",
        reply_markup=custom_style_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("custom:style:"))
async def custom_step3(callback: CallbackQuery, state: FSMContext) -> None:
    style = callback.data.split(":")[2]
    await state.update_data(style=style)
    await state.set_state(CustomFlow.step4_location)
    await callback.message.edit_text(
        "<b>Шаг 4 из 5</b> — Фон и локация:", parse_mode="HTML",
        reply_markup=custom_location_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("custom:loc:"))
async def custom_step4(callback: CallbackQuery, state: FSMContext) -> None:
    loc_key = callback.data.split(":")[2]
    if loc_key == "custom":
        await state.set_state(CustomFlow.step4_custom_location)
        await callback.message.edit_text(
            "<b>Шаг 4 из 5</b> — Опиши локацию текстом:",
            parse_mode="HTML",
            reply_markup=cancel_kb(),
        )
    else:
        await state.update_data(loc_key=loc_key)
        await state.set_state(CustomFlow.step5_details)
        await callback.message.edit_text(
            "<b>Шаг 5 из 5</b> — Добавь детали (опционально):\n\n"
            "Цвет одежды, настроение, эпоха — что угодно.",
            parse_mode="HTML",
            reply_markup=custom_details_skip_kb(),
        )
    await callback.answer()


@router.message(CustomFlow.step4_custom_location, F.text)
async def custom_step4_text(message: Message, state: FSMContext) -> None:
    await state.update_data(location=message.text)
    await state.set_state(CustomFlow.step5_details)
    await message.answer(
        "<b>Шаг 5 из 5</b> — Добавь детали (опционально):\n\n"
        "Цвет одежды, настроение, эпоха — что угодно.",
        parse_mode="HTML",
        reply_markup=custom_details_skip_kb(),
    )


@router.callback_query(F.data == "custom:details:skip")
async def custom_step5_skip(callback: CallbackQuery, state: FSMContext) -> None:
    await _show_review(callback, state)
    await callback.answer()


@router.message(CustomFlow.step5_details, F.text)
async def custom_step5_text(message: Message, state: FSMContext) -> None:
    await state.update_data(details=message.text)
    await _show_review_msg(message, state)


async def _show_review(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    desc = _describe_prompt(data)
    await callback.message.edit_text(
        f"<b>Твой образ:</b>\n\n{desc}\n\nВсё верно?",
        parse_mode="HTML",
        reply_markup=custom_review_kb(),
    )


async def _show_review_msg(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    desc = _describe_prompt(data)
    await message.answer(
        f"<b>Твой образ:</b>\n\n{desc}\n\nВсё верно?",
        parse_mode="HTML",
        reply_markup=custom_review_kb(),
    )


@router.callback_query(F.data == "custom:generate")
async def custom_generate(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    if "prompt" not in data:
        prompt = _assemble_prompt(data)
        await state.update_data(prompt=prompt)
    await state.set_state(CustomFlow.waiting_photo)
    await callback.message.edit_text(
        PHOTO_TIPS, parse_mode="HTML", reply_markup=cancel_kb()
    )
    await callback.answer()


# ─── Photo received ───────────────────────────────────────────────────────────

@router.callback_query(F.data == "custom:regenerate")
async def custom_regenerate(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CustomFlow.waiting_photo)
    await callback.message.answer(PHOTO_TIPS, parse_mode="HTML", reply_markup=cancel_kb())
    await callback.answer()


@router.message(CustomFlow.waiting_photo, F.photo | F.document)
async def custom_photo_received(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    prompt: str = data.get("prompt", "photorealistic portrait, high quality")

    user = await db.get_user(message.from_user.id)
    total = (user["paid_credits"] or 0) + (user["free_credits"] or 0)
    if total < 1:
        await state.clear()
        await message.answer(
            "У тебя закончились кредиты. Пополни баланс, чтобы продолжить.",
            reply_markup=paywall_kb(),
        )
        await db.mark_paywall_shown(message.from_user.id)
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
        gen_type="custom",
        prompt=prompt,
        source_file_id=_get_file_id(message),
    )

    try:
        face_url = await upload_photo(photo_bytes)
        result_bytes = await generate_portrait(face_url, prompt)
    except GenerationError:
        await db.fail_generation(gen_id)
        await db.refund_credit(message.from_user.id, credit_type)
        await status_msg.edit_text(
            "Что-то пошло не так при генерации. Кредит не списан — попробуй ещё раз.",
            reply_markup=after_custom_kb(),
        )
        return

    was_free = credit_type == "free"
    if was_free:
        result_bytes = add_watermark(result_bytes)

    try:
        result_msg = await message.answer_photo(
            BufferedInputFile(result_bytes, filename="result.jpg"),
            reply_markup=after_custom_kb(),
        )
    except Exception:
        await db.fail_generation(gen_id)
        await db.refund_credit(message.from_user.id, credit_type)
        await status_msg.edit_text(
            "Не удалось отправить изображение. Кредит не списан — попробуй ещё раз.",
            reply_markup=after_custom_kb(),
        )
        return

    await status_msg.delete()

    file_id = result_msg.photo[-1].file_id
    await db.complete_generation(gen_id, [file_id], was_free)

    # Keep prompt in state for potential regeneration
    await state.update_data(prompt=prompt)


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
