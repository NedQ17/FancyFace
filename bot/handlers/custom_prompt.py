import io
import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from bot import database as db
from bot.keyboards.builders import (
    custom_mode_kb, custom_gender_kb, custom_category_kb, custom_framing_kb,
    custom_render_kb, custom_mood_kb, custom_clothing_kb, custom_clothing_type_kb,
    custom_background_kb, custom_lighting_kb, custom_details_kb, custom_restrictions_kb,
    custom_era_kb, custom_review_kb, after_custom_kb, paywall_kb, credits_empty_kb, cancel_kb,
    DETAILS_OPTIONS, RESTRICTIONS_OPTIONS,
)
from bot.services.generation import generate_portrait, upload_photo, download_image, GenerationError
from bot.states.flows import CustomFlow

router = Router()
logger = logging.getLogger(__name__)

TOTAL_STEPS = 11

PHOTO_TIPS = (
    "Почти готово! Осталось прислать своё фото.\n\n"
    "Для точной передачи черт лица используй чёткое портретное фото при хорошем освещении. "
    "Анфас или лёгкий поворот — лучший вариант.\n\n"
    "<b>Без очков, без фильтров, без группового фото.</b>"
)

# ─── Mappings ─────────────────────────────────────────────────────────────────

GENDER_MAP = {
    "female": ("Женщина", "woman"),
    "male":   ("Мужчина", "man"),
    "skip":   ("—", ""),
}
CATEGORY_MAP = {
    "business":     ("Деловой",          "professional corporate business portrait"),
    "portrait":     ("Портрет",          "artistic fine art portrait photography"),
    "photorealism": ("Фотореализм",      "hyperrealistic documentary photograph"),
    "lifestyle":    ("Лайфстайл",        "candid lifestyle photography"),
    "cinematic":    ("Кинематографичный","cinematic film still portrait"),
    "art":          ("Арт стиль",        "expressive fine art stylized portrait"),
}
FRAMING_MAP = {
    "bust":  ("Бюст",          "tight bust shot, head and shoulders framing"),
    "waist": ("По пояс",       "half body shot, waist-up framing"),
    "full":  ("В полный рост", "full body shot, entire figure visible, feet on solid ground"),
}
RENDER_MAP = {
    "realism":  ("Реализм",          "photorealistic true-to-life rendering, no stylization"),
    "stylized": ("Лёгкая стилизация","lightly stylized with painterly artistic touches"),
    "art":      ("Арт стиль",        "strong artistic stylization, expressive fine art rendering"),
}
MOOD_MAP = {
    "calm":     ("Спокойное",   "calm serene peaceful expression and atmosphere"),
    "pleased":  ("Довольное",   "warm gentle pleasant smile, approachable friendly mood"),
    "serious":  ("Серьёзное",   "serious composed strong gaze, confident powerful demeanor"),
    "romantic": ("Романтичное", "soft romantic dreamy atmosphere, gentle intimate mood"),
    "business": ("Деловое",     "professional authoritative confident business demeanor"),
}
CLOTHING_MAP = {
    "keep":       ("Оригинальная", "wearing original clothing unchanged"),
    "casual":     ("Кэжуал",      "wearing casual relaxed everyday clothing"),
    "classic":    ("Классическая","wearing classic elegant timeless clothing"),
    "business":   ("Бизнес",      "wearing formal business attire, tailored suit or blazer"),
    "festival":   ("Фестиваль",   "wearing vibrant expressive festival outfit"),
    "historical": ("Историческая","wearing authentic historical period costume"),
    "minimal":    ("Минимализм",  "wearing minimalist clean simple understated clothing"),
}
BACKGROUND_MAP = {
    "studio":   ("Студия",      "clean professional studio seamless backdrop"),
    "city":     ("Город",       "dynamic urban cityscape environment"),
    "nature":   ("Природа",     "natural outdoor organic lush environment"),
    "interior": ("Интерьер",    "elegant architectural interior setting"),
    "blurred":  ("Размытый фон","soft bokeh blurred background, subject in sharp focus"),
}
LIGHTING_MAP = {
    "natural":   ("Естественный свет","soft natural daylight, window light"),
    "soft":      ("Мягкий свет",      "soft diffused even studio illumination"),
    "backlit":   ("Контровой свет",   "dramatic backlight rim lighting, contre-jour"),
    "cinematic": ("Кинематографичный","cinematic moody directional lighting, dramatic shadows"),
}
ERA_MAP = {
    "50s":  ("Пятидесятые", "1950s mid-century vintage era aesthetic"),
    "70s":  ("Семидесятые", "1970s retro groovy era aesthetic"),
    "90s":  ("Девяностые",  "1990s nostalgia era aesthetic"),
    "00s":  ("Нулевые",     "early 2000s Y2K millennium era aesthetic"),
    "skip": ("—",           ""),
}
DETAILS_LABEL_MAP = {o[0]: o[1] for o in DETAILS_OPTIONS}
DETAILS_PROMPT_MAP = {
    "candles": "warm flickering candle glow in surroundings",
    "flowers": "fresh flowers as decorative accent",
    "plants":  "lush green plants in the environment",
    "fabrics": "flowing fabrics and draped textiles",
    "minimal": "minimalist clean geometric decorative elements",
}
RESTRICTIONS_LABEL_MAP = {o[0]: o[1] for o in RESTRICTIONS_OPTIONS}
RESTRICTIONS_PROMPT_MAP = {
    "no_pose":       "preserve the original body pose exactly",
    "no_expression": "preserve the exact facial expression unchanged",
    "no_hair":       "preserve the original hairstyle unchanged",
    "no_objects":    "do not add any objects to the hands",
}


# ─── Prompt assembly ──────────────────────────────────────────────────────────

def _assemble_prompt(data: dict) -> str:
    parts = []

    gender_prompt = GENDER_MAP.get(data.get("gender", "skip"), ("", ""))[1]
    category_prompt = CATEGORY_MAP.get(data.get("category", "photorealism"), ("", ""))[1]
    if gender_prompt:
        parts.append(f"{gender_prompt}, {category_prompt}")
    else:
        parts.append(category_prompt)

    parts.append(FRAMING_MAP.get(data.get("framing", "bust"), ("", ""))[1])
    parts.append(RENDER_MAP.get(data.get("render", "realism"), ("", ""))[1])
    parts.append(MOOD_MAP.get(data.get("mood", "calm"), ("", ""))[1])

    clothing_key = data.get("clothing", "keep")
    if clothing_key == "keep":
        parts.append(CLOTHING_MAP["keep"][1])
    elif clothing_key == "replace":
        ctype = data.get("clothing_type", "")
        if ctype == "custom":
            parts.append(f"wearing: {data.get('clothing_custom', '')}")
        elif ctype in CLOTHING_MAP:
            parts.append(CLOTHING_MAP[ctype][1])
    else:
        parts.append(CLOTHING_MAP.get(clothing_key, CLOTHING_MAP["keep"])[1])

    bg_key = data.get("background", "")
    if bg_key == "custom":
        parts.append(f"background: {data.get('background_custom', '')}")
    elif bg_key in BACKGROUND_MAP:
        parts.append(BACKGROUND_MAP[bg_key][1])

    parts.append(LIGHTING_MAP.get(data.get("lighting", "natural"), ("", ""))[1])

    details = data.get("details", set())
    detail_prompts = [DETAILS_PROMPT_MAP[d] for d in details if d in DETAILS_PROMPT_MAP]
    if data.get("details_custom"):
        detail_prompts.append(data["details_custom"])
    if detail_prompts:
        parts.append(", ".join(detail_prompts))

    restrictions = data.get("restrictions", set())
    restriction_prompts = [RESTRICTIONS_PROMPT_MAP[r] for r in restrictions if r in RESTRICTIONS_PROMPT_MAP]
    if restriction_prompts:
        parts.append(", ".join(restriction_prompts))

    era_prompt = ERA_MAP.get(data.get("era", "skip"), ("", ""))[1]
    if era_prompt:
        parts.append(era_prompt)

    parts.append("photorealistic, high quality, detailed")
    return ", ".join(p for p in parts if p)


def _describe_settings(data: dict) -> str:
    lines = ["<b>Твои настройки:</b>\n"]

    gender_label = GENDER_MAP.get(data.get("gender", "skip"), ("—",))[0]
    lines.append(f"Пол: {gender_label}")
    lines.append(f"Категория: {CATEGORY_MAP.get(data.get('category',''), ('—',))[0]}")
    lines.append(f"Кадрирование: {FRAMING_MAP.get(data.get('framing',''), ('—',))[0]}")
    lines.append(f"Рендер: {RENDER_MAP.get(data.get('render',''), ('—',))[0]}")
    lines.append(f"Настроение: {MOOD_MAP.get(data.get('mood',''), ('—',))[0]}")

    clothing_key = data.get("clothing", "keep")
    if clothing_key == "keep":
        lines.append("Одежда: оригинальная")
    elif clothing_key == "replace":
        ctype = data.get("clothing_type", "")
        if ctype == "custom":
            lines.append(f"Одежда: {data.get('clothing_custom', '—')}")
        else:
            lines.append(f"Одежда: {CLOTHING_MAP.get(ctype, ('—',))[0]}")

    bg_key = data.get("background", "")
    if bg_key == "custom":
        lines.append(f"Фон: {data.get('background_custom', '—')}")
    else:
        lines.append(f"Фон: {BACKGROUND_MAP.get(bg_key, ('—',))[0]}")

    lines.append(f"Освещение: {LIGHTING_MAP.get(data.get('lighting',''), ('—',))[0]}")

    details = data.get("details", set())
    if details:
        detail_labels = [DETAILS_LABEL_MAP.get(d, d) for d in details if d != "custom"]
        if data.get("details_custom"):
            detail_labels.append(data["details_custom"])
        lines.append(f"Детали: {', '.join(detail_labels)}")

    restrictions = data.get("restrictions", set())
    if restrictions:
        r_labels = [RESTRICTIONS_LABEL_MAP.get(r, r) for r in restrictions]
        lines.append(f"Ограничения: {', '.join(r_labels)}")

    era_label = ERA_MAP.get(data.get("era", "skip"), ("—",))[0]
    if era_label != "—":
        lines.append(f"Эпоха: {era_label}")

    return "\n".join(lines)


def _step(n: int) -> str:
    return f"<b>Шаг {n} из {TOTAL_STEPS}</b>"


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


# ─── Builder: step 1 — Gender ─────────────────────────────────────────────────

@router.callback_query(F.data == "custom:builder")
@router.callback_query(F.data == "custom:restart")
async def custom_builder_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CustomFlow.step1_gender)
    await state.update_data({})
    await callback.message.edit_text(
        f"{_step(1)} — Пол:", parse_mode="HTML",
        reply_markup=custom_gender_kb(),
    )
    await callback.answer()


@router.callback_query(CustomFlow.step1_gender, F.data.startswith("custom:gender:"))
async def step1_gender(callback: CallbackQuery, state: FSMContext) -> None:
    gender = callback.data.split(":")[2]
    await state.update_data(gender=gender)
    await state.set_state(CustomFlow.step2_category)
    await callback.message.edit_text(
        f"{_step(2)} — Категория:", parse_mode="HTML",
        reply_markup=custom_category_kb(),
    )
    await callback.answer()


# ─── Step 2 — Category ───────────────────────────────────────────────────────

@router.callback_query(CustomFlow.step2_category, F.data.startswith("custom:category:"))
async def step2_category(callback: CallbackQuery, state: FSMContext) -> None:
    category = callback.data.split(":")[2]
    await state.update_data(category=category)
    await state.set_state(CustomFlow.step3_framing)
    await callback.message.edit_text(
        f"{_step(3)} — Кадрирование портрета:", parse_mode="HTML",
        reply_markup=custom_framing_kb(),
    )
    await callback.answer()


# ─── Step 3 — Framing ────────────────────────────────────────────────────────

@router.callback_query(CustomFlow.step3_framing, F.data.startswith("custom:framing:"))
async def step3_framing(callback: CallbackQuery, state: FSMContext) -> None:
    framing = callback.data.split(":")[2]
    await state.update_data(framing=framing)
    await state.set_state(CustomFlow.step4_render)
    await callback.message.edit_text(
        f"{_step(4)} — Стиль рендеринга:", parse_mode="HTML",
        reply_markup=custom_render_kb(),
    )
    await callback.answer()


# ─── Step 4 — Render style ───────────────────────────────────────────────────

@router.callback_query(CustomFlow.step4_render, F.data.startswith("custom:render:"))
async def step4_render(callback: CallbackQuery, state: FSMContext) -> None:
    render = callback.data.split(":")[2]
    await state.update_data(render=render)
    await state.set_state(CustomFlow.step5_mood)
    await callback.message.edit_text(
        f"{_step(5)} — Настроение:", parse_mode="HTML",
        reply_markup=custom_mood_kb(),
    )
    await callback.answer()


# ─── Step 5 — Mood ───────────────────────────────────────────────────────────

@router.callback_query(CustomFlow.step5_mood, F.data.startswith("custom:mood:"))
async def step5_mood(callback: CallbackQuery, state: FSMContext) -> None:
    mood = callback.data.split(":")[2]
    await state.update_data(mood=mood)
    await state.set_state(CustomFlow.step6_clothing)
    await callback.message.edit_text(
        f"{_step(6)} — Одежда:", parse_mode="HTML",
        reply_markup=custom_clothing_kb(),
    )
    await callback.answer()


# ─── Step 6 — Clothing ───────────────────────────────────────────────────────

@router.callback_query(CustomFlow.step6_clothing, F.data == "custom:clothing:keep")
async def step6_clothing_keep(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(clothing="keep")
    await _go_to_background(callback, state)


@router.callback_query(CustomFlow.step6_clothing, F.data == "custom:clothing:replace")
async def step6_clothing_replace(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(clothing="replace")
    await state.set_state(CustomFlow.step6b_clothing_type)
    await callback.message.edit_text(
        f"{_step(6)} — Выбери тип одежды:", parse_mode="HTML",
        reply_markup=custom_clothing_type_kb(),
    )
    await callback.answer()


@router.callback_query(CustomFlow.step6b_clothing_type, F.data.startswith("custom:ctype:"))
async def step6b_clothing_type(callback: CallbackQuery, state: FSMContext) -> None:
    ctype = callback.data.split(":")[2]
    if ctype == "custom":
        await state.set_state(CustomFlow.step6b_clothing_custom)
        await callback.message.edit_text(
            f"{_step(6)} — Опиши одежду своими словами:",
            parse_mode="HTML", reply_markup=cancel_kb(),
        )
    else:
        await state.update_data(clothing_type=ctype)
        await _go_to_background(callback, state)
    await callback.answer()


@router.message(CustomFlow.step6b_clothing_custom, F.text)
async def step6b_clothing_custom(message: Message, state: FSMContext) -> None:
    await state.update_data(clothing_type="custom", clothing_custom=message.text)
    await state.set_state(CustomFlow.step7_background)
    await message.answer(
        f"{_step(7)} — Фон:", parse_mode="HTML",
        reply_markup=custom_background_kb(),
    )


async def _go_to_background(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CustomFlow.step7_background)
    await callback.message.edit_text(
        f"{_step(7)} — Фон:", parse_mode="HTML",
        reply_markup=custom_background_kb(),
    )
    await callback.answer()


# ─── Step 7 — Background ─────────────────────────────────────────────────────

@router.callback_query(CustomFlow.step7_background, F.data.startswith("custom:bg:"))
async def step7_background(callback: CallbackQuery, state: FSMContext) -> None:
    bg = callback.data.split(":")[2]
    if bg == "custom":
        await state.set_state(CustomFlow.step7b_background_custom)
        await callback.message.edit_text(
            f"{_step(7)} — Опиши фон своими словами:",
            parse_mode="HTML", reply_markup=cancel_kb(),
        )
    else:
        await state.update_data(background=bg)
        await _go_to_lighting(callback, state)
    await callback.answer()


@router.message(CustomFlow.step7b_background_custom, F.text)
async def step7b_background_custom(message: Message, state: FSMContext) -> None:
    await state.update_data(background="custom", background_custom=message.text)
    await state.set_state(CustomFlow.step8_lighting)
    await message.answer(
        f"{_step(8)} — Освещение:", parse_mode="HTML",
        reply_markup=custom_lighting_kb(),
    )


async def _go_to_lighting(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CustomFlow.step8_lighting)
    await callback.message.edit_text(
        f"{_step(8)} — Освещение:", parse_mode="HTML",
        reply_markup=custom_lighting_kb(),
    )
    await callback.answer()


# ─── Step 8 — Lighting ───────────────────────────────────────────────────────

@router.callback_query(CustomFlow.step8_lighting, F.data.startswith("custom:light:"))
async def step8_lighting(callback: CallbackQuery, state: FSMContext) -> None:
    light = callback.data.split(":")[2]
    await state.update_data(lighting=light)
    await state.set_state(CustomFlow.step9_details)
    data = await state.get_data()
    await callback.message.edit_text(
        f"{_step(9)} — Детали и декор:\n<i>Можно выбрать несколько</i>",
        parse_mode="HTML",
        reply_markup=custom_details_kb(data.get("details", set())),
    )
    await callback.answer()


# ─── Step 9 — Details (multi-select) ─────────────────────────────────────────

@router.callback_query(CustomFlow.step9_details, F.data.startswith("custom:detail:"))
async def step9_detail_toggle(callback: CallbackQuery, state: FSMContext) -> None:
    key = callback.data.split(":")[2]
    if key == "done":
        await _go_to_restrictions(callback, state)
        return
    if key == "custom":
        await state.set_state(CustomFlow.step9_details_custom)
        await callback.message.answer(
            "Опиши детали своими словами:", reply_markup=cancel_kb()
        )
        await callback.answer()
        return

    data = await state.get_data()
    selected: set = data.get("details", set())
    if key in selected:
        selected.discard(key)
    else:
        selected.add(key)
    await state.update_data(details=selected)
    await callback.message.edit_reply_markup(
        reply_markup=custom_details_kb(selected)
    )
    await callback.answer()


@router.message(CustomFlow.step9_details_custom, F.text)
async def step9_details_custom(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    selected: set = data.get("details", set())
    selected.add("custom")
    await state.update_data(details=selected, details_custom=message.text)
    await state.set_state(CustomFlow.step9_details)
    await message.answer(
        f"{_step(9)} — Детали и декор:\n<i>Можно выбрать несколько</i>",
        parse_mode="HTML",
        reply_markup=custom_details_kb(selected),
    )


async def _go_to_restrictions(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await state.set_state(CustomFlow.step10_restrictions)
    await callback.message.edit_text(
        f"{_step(10)} — Ограничения:\n<i>Можно выбрать несколько или пропустить</i>",
        parse_mode="HTML",
        reply_markup=custom_restrictions_kb(data.get("restrictions", set())),
    )
    await callback.answer()


# ─── Step 10 — Restrictions (multi-select) ───────────────────────────────────

@router.callback_query(CustomFlow.step10_restrictions, F.data.startswith("custom:restrict:"))
async def step10_restriction_toggle(callback: CallbackQuery, state: FSMContext) -> None:
    key = callback.data.split(":")[2]
    if key == "done":
        await _go_to_era(callback, state)
        return

    data = await state.get_data()
    selected: set = data.get("restrictions", set())
    if key in selected:
        selected.discard(key)
    else:
        selected.add(key)
    await state.update_data(restrictions=selected)
    await callback.message.edit_reply_markup(
        reply_markup=custom_restrictions_kb(selected)
    )
    await callback.answer()


# ─── Step 11 — Era ───────────────────────────────────────────────────────────

async def _go_to_era(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CustomFlow.step11_era)
    await callback.message.edit_text(
        f"{_step(11)} — Стиль эпохи:", parse_mode="HTML",
        reply_markup=custom_era_kb(),
    )
    await callback.answer()


@router.callback_query(CustomFlow.step11_era, F.data.startswith("custom:era:"))
async def step11_era(callback: CallbackQuery, state: FSMContext) -> None:
    era = callback.data.split(":")[2]
    await state.update_data(era=era)
    await _show_review(callback, state)


# ─── Review ───────────────────────────────────────────────────────────────────

async def _show_review(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    desc = _describe_settings(data)
    await state.set_state(CustomFlow.step_review)
    await callback.message.edit_text(
        desc, parse_mode="HTML", reply_markup=custom_review_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "custom:generate")
async def custom_generate(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    if "prompt" not in data:
        await state.update_data(prompt=_assemble_prompt(data))
    await state.set_state(CustomFlow.waiting_photo)
    await callback.message.answer(PHOTO_TIPS, parse_mode="HTML", reply_markup=cancel_kb())
    await callback.answer()


# ─── Back navigation ─────────────────────────────────────────────────────────

@router.callback_query(F.data == "custom:back")
async def custom_back(callback: CallbackQuery, state: FSMContext) -> None:
    current = await state.get_state()
    data = await state.get_data()

    if current == CustomFlow.step1_gender:
        await state.clear()
        await callback.message.edit_text(
            "Как хочешь создать образ?", reply_markup=custom_mode_kb()
        )
    elif current == CustomFlow.step2_category:
        await state.set_state(CustomFlow.step1_gender)
        await callback.message.edit_text(
            f"{_step(1)} — Пол:", parse_mode="HTML",
            reply_markup=custom_gender_kb(),
        )
    elif current == CustomFlow.step3_framing:
        await state.set_state(CustomFlow.step2_category)
        await callback.message.edit_text(
            f"{_step(2)} — Категория:", parse_mode="HTML",
            reply_markup=custom_category_kb(),
        )
    elif current == CustomFlow.step4_render:
        await state.set_state(CustomFlow.step3_framing)
        await callback.message.edit_text(
            f"{_step(3)} — Кадрирование портрета:", parse_mode="HTML",
            reply_markup=custom_framing_kb(),
        )
    elif current == CustomFlow.step5_mood:
        await state.set_state(CustomFlow.step4_render)
        await callback.message.edit_text(
            f"{_step(4)} — Стиль рендеринга:", parse_mode="HTML",
            reply_markup=custom_render_kb(),
        )
    elif current == CustomFlow.step6_clothing:
        await state.set_state(CustomFlow.step5_mood)
        await callback.message.edit_text(
            f"{_step(5)} — Настроение:", parse_mode="HTML",
            reply_markup=custom_mood_kb(),
        )
    elif current == CustomFlow.step6b_clothing_type:
        await state.set_state(CustomFlow.step6_clothing)
        await callback.message.edit_text(
            f"{_step(6)} — Одежда:", parse_mode="HTML",
            reply_markup=custom_clothing_kb(),
        )
    elif current == CustomFlow.step7_background:
        if data.get("clothing") == "replace":
            await state.set_state(CustomFlow.step6b_clothing_type)
            await callback.message.edit_text(
                f"{_step(6)} — Выбери тип одежды:", parse_mode="HTML",
                reply_markup=custom_clothing_type_kb(),
            )
        else:
            await state.set_state(CustomFlow.step6_clothing)
            await callback.message.edit_text(
                f"{_step(6)} — Одежда:", parse_mode="HTML",
                reply_markup=custom_clothing_kb(),
            )
    elif current == CustomFlow.step8_lighting:
        await state.set_state(CustomFlow.step7_background)
        await callback.message.edit_text(
            f"{_step(7)} — Фон:", parse_mode="HTML",
            reply_markup=custom_background_kb(),
        )
    elif current == CustomFlow.step9_details:
        await state.set_state(CustomFlow.step8_lighting)
        await callback.message.edit_text(
            f"{_step(8)} — Освещение:", parse_mode="HTML",
            reply_markup=custom_lighting_kb(),
        )
    elif current == CustomFlow.step10_restrictions:
        await state.set_state(CustomFlow.step9_details)
        await callback.message.edit_text(
            f"{_step(9)} — Детали и декор:\n<i>Можно выбрать несколько</i>",
            parse_mode="HTML",
            reply_markup=custom_details_kb(data.get("details", set())),
        )
    elif current == CustomFlow.step11_era:
        await state.set_state(CustomFlow.step10_restrictions)
        await callback.message.edit_text(
            f"{_step(10)} — Ограничения:\n<i>Можно выбрать несколько или пропустить</i>",
            parse_mode="HTML",
            reply_markup=custom_restrictions_kb(data.get("restrictions", set())),
        )
    elif current == CustomFlow.step_review:
        await state.set_state(CustomFlow.step11_era)
        await callback.message.edit_text(
            f"{_step(11)} — Стиль эпохи:", parse_mode="HTML",
            reply_markup=custom_era_kb(),
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
    total = (user["paid_credits"] or 0) + (user["bonus_credits"] or 0) + (user["free_credits"] or 0)
    if total < 1:
        await state.clear()
        await message.answer(
            "У тебя закончились кредиты. Пополни баланс, чтобы продолжить.",
            reply_markup=credits_empty_kb(),
        )
        await db.mark_paywall_shown(message.from_user.id)
        return

    status_msg = await message.answer("Генерирую твой образ, скоро будет готово... ⏳")
    await state.clear()

    photo_bytes = await _get_photo_bytes(message, bot)
    if not photo_bytes:
        await status_msg.edit_text("Не удалось прочитать фото. Попробуй ещё раз.")
        return

    uid = message.from_user.id
    credit_type = await db.consume_credit(uid)
    gen_id = await db.create_generation(
        user_id=uid,
        gen_type="custom",
        prompt=prompt,
    )

    logger.info("User %s custom generation started", uid)
    try:
        face_url = await upload_photo(photo_bytes)
        logger.info("User %s photo uploaded", uid)
        result_url = await generate_portrait(face_url, prompt)
        logger.info("User %s generation done, downloading result", uid)
        result_bytes = await download_image(result_url)
        logger.info("User %s result downloaded (%d bytes)", uid, len(result_bytes))
    except GenerationError:
        await db.fail_generation(gen_id)
        await db.refund_credit(uid, credit_type)
        await status_msg.edit_text(
            "Что-то пошло не так при генерации. Кредит не списан — попробуй ещё раз.",
            reply_markup=after_custom_kb(),
        )
        return

    was_free = credit_type == "free"

    try:
        result_msg = await message.answer_photo(
            BufferedInputFile(result_bytes, filename="result.jpg"),
            reply_markup=after_custom_kb(),
        )
        logger.info("User %s result sent successfully", uid)
    except Exception:
        logger.exception("User %s failed to send result photo", uid)
        await db.fail_generation(gen_id)
        await db.refund_credit(uid, credit_type)
        await status_msg.edit_text(
            "Не удалось отправить изображение. Кредит не списан — попробуй ещё раз.",
            reply_markup=after_custom_kb(),
        )
        return

    await status_msg.delete()
    file_id = result_msg.photo[-1].file_id
    await db.complete_generation(gen_id, [file_id], was_free)
    await state.update_data(prompt=prompt)


# ─── Helpers ──────────────────────────────────────────────────────────────────

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
