import asyncio

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot import database as db
from bot.config import ADMIN_IDS
from bot.keyboards.builders import (
    admin_menu_kb, admin_confirm_broadcast_kb, admin_cancel_kb, back_to_menu_kb,
)
from bot.states.flows import AdminFlow

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ─── Entry ────────────────────────────────────────────────────────────────────

@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer("👑 <b>Панель администратора</b>", parse_mode="HTML",
                         reply_markup=admin_menu_kb())


@router.callback_query(F.data == "admin:cancel")
async def admin_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "👑 <b>Панель администратора</b>", parse_mode="HTML",
        reply_markup=admin_menu_kb()
    )
    await callback.answer()


# ─── Statistics ───────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery) -> None:
    if not is_admin(callback.from_user.id):
        return
    stats = await db.get_admin_stats()
    text = (
        "📊 <b>Статистика</b>\n\n"
        f"👥 Всего пользователей: <b>{stats['total_users']}</b>\n"
        f"  • За сегодня: <b>{stats['new_today']}</b>\n"
        f"  • За неделю: <b>{stats['new_week']}</b>\n"
        f"  • За месяц: <b>{stats['new_month']}</b>\n\n"
        f"📸 Генераций завершено:\n"
        f"  • За сегодня: <b>{stats['gen_today']}</b>\n"
        f"  • За неделю: <b>{stats['gen_week']}</b>\n"
        f"  • За месяц: <b>{stats['gen_month']}</b>\n\n"
        f"💰 Выручка (₽):\n"
        f"  • За сегодня: <b>{stats['rev_today']}</b>\n"
        f"  • За неделю: <b>{stats['rev_week']}</b>\n"
        f"  • За месяц: <b>{stats['rev_month']}</b>"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=admin_menu_kb())
    await callback.answer()


# ─── Broadcast ────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminFlow.waiting_broadcast)
    await callback.message.edit_text(
        "Отправь сообщение для рассылки (текст, фото или фото с подписью).",
        reply_markup=admin_cancel_kb(),
    )
    await callback.answer()


@router.message(AdminFlow.waiting_broadcast, F.text | F.photo)
async def admin_broadcast_preview(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return
    if message.photo:
        await state.update_data(
            broadcast_type="photo",
            photo_id=message.photo[-1].file_id,
            caption=message.caption or "",
        )
    else:
        await state.update_data(broadcast_type="text", text=message.text)

    await state.set_state(AdminFlow.broadcast_confirm)
    await message.answer(
        "Вот так будет выглядеть сообщение. Отправить всем пользователям?",
        reply_markup=admin_confirm_broadcast_kb(),
    )


@router.callback_query(F.data == "admin:broadcast_confirm", AdminFlow.broadcast_confirm)
async def admin_broadcast_send(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    if not is_admin(callback.from_user.id):
        return
    data = await state.get_data()
    await state.clear()

    user_ids = await db.get_all_active_user_ids()
    await callback.message.edit_text(f"Рассылка запущена... ({len(user_ids)} пользователей)")
    await callback.answer()

    sent, failed = await _broadcast(bot, user_ids, data)
    await callback.message.answer(
        f"✅ Рассылка завершена.\nОтправлено: {sent}\nОшибок: {failed}",
        reply_markup=admin_menu_kb(),
    )


async def _broadcast(bot: Bot, user_ids: list[int], data: dict) -> tuple[int, int]:
    sent = failed = 0
    for i, uid in enumerate(user_ids):
        try:
            if data.get("broadcast_type") == "photo":
                await bot.send_photo(uid, data["photo_id"], caption=data.get("caption"))
            else:
                await bot.send_message(uid, data["text"])
            sent += 1
        except Exception:
            failed += 1
        if i % 25 == 24:
            await asyncio.sleep(1)
    return sent, failed


# ─── Add credits ──────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:add_credits")
async def admin_credits_start(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminFlow.waiting_user_id_credits)
    await callback.message.edit_text(
        "Введи user_id пользователя:", reply_markup=admin_cancel_kb()
    )
    await callback.answer()


@router.message(AdminFlow.waiting_user_id_credits, F.text)
async def admin_credits_user(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return
    if not message.text.strip().isdigit():
        await message.answer("Введи числовой user_id.")
        return
    await state.update_data(target_user_id=int(message.text.strip()))
    await state.set_state(AdminFlow.waiting_credits_amount)
    await message.answer("Сколько кредитов начислить?", reply_markup=admin_cancel_kb())


@router.message(AdminFlow.waiting_credits_amount, F.text)
async def admin_credits_amount(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return
    if not message.text.strip().isdigit():
        await message.answer("Введи число.")
        return
    data = await state.get_data()
    amount = int(message.text.strip())
    uid = data["target_user_id"]
    user = await db.get_user(uid)
    if not user:
        await message.answer("Пользователь не найден.", reply_markup=admin_menu_kb())
    else:
        await db.add_credits(uid, paid=amount)
        await message.answer(
            f"✅ Начислено {amount} кредитов пользователю {uid}.",
            reply_markup=admin_menu_kb(),
        )
    await state.clear()


# ─── Block user ───────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:block")
async def admin_block_start(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminFlow.waiting_user_id_block)
    await callback.message.edit_text(
        "Введи user_id для блокировки (или разблокировки):",
        reply_markup=admin_cancel_kb(),
    )
    await callback.answer()


@router.message(AdminFlow.waiting_user_id_block, F.text)
async def admin_block_user(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return
    if not message.text.strip().isdigit():
        await message.answer("Введи числовой user_id.")
        return
    uid = int(message.text.strip())
    user = await db.get_user(uid)
    if not user:
        await message.answer("Пользователь не найден.", reply_markup=admin_menu_kb())
    else:
        if user.get("is_blocked"):
            await db.unblock_user(uid)
            await message.answer(f"✅ Пользователь {uid} разблокирован.", reply_markup=admin_menu_kb())
        else:
            await db.block_user(uid)
            await message.answer(f"🚫 Пользователь {uid} заблокирован.", reply_markup=admin_menu_kb())
    await state.clear()


# ─── Add style ────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:add_style")
async def admin_add_style_start(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminFlow.adding_style_name)
    await callback.message.edit_text(
        "Введи название нового стиля:", reply_markup=admin_cancel_kb()
    )
    await callback.answer()


@router.message(AdminFlow.adding_style_name, F.text)
async def admin_style_name(message: Message, state: FSMContext) -> None:
    await state.update_data(style_name=message.text.strip())
    await state.set_state(AdminFlow.adding_style_emoji)
    await message.answer("Введи эмодзи для стиля (или отправь «-» без эмодзи):")


@router.message(AdminFlow.adding_style_emoji, F.text)
async def admin_style_emoji(message: Message, state: FSMContext) -> None:
    emoji = message.text.strip()
    if emoji == "-":
        emoji = ""
    await state.update_data(style_emoji=emoji)
    await state.set_state(AdminFlow.adding_style_prompt)
    await message.answer(
        "Введи промпт для этого стиля (на английском, для InstantID):"
    )


@router.message(AdminFlow.adding_style_prompt, F.text)
async def admin_style_prompt(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    style_id = await db.add_style(
        name=data["style_name"],
        emoji=data["style_emoji"],
        prompt=message.text.strip(),
    )
    await state.clear()
    await message.answer(
        f"✅ Стиль «{data['style_name']}» добавлен (id={style_id}).",
        reply_markup=admin_menu_kb(),
    )


# ─── Add session ──────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:add_session")
async def admin_add_session_start(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminFlow.adding_session_name)
    await callback.message.edit_text(
        "Введи название фотосессии:", reply_markup=admin_cancel_kb()
    )
    await callback.answer()


@router.message(AdminFlow.adding_session_name, F.text)
async def admin_session_name(message: Message, state: FSMContext) -> None:
    await state.update_data(session_name=message.text.strip())
    await state.set_state(AdminFlow.adding_session_description)
    await message.answer("Введи описание фотосессии (2–3 предложения):")


@router.message(AdminFlow.adding_session_description, F.text)
async def admin_session_desc(message: Message, state: FSMContext) -> None:
    await state.update_data(session_desc=message.text.strip())
    await state.set_state(AdminFlow.adding_session_count)
    await message.answer("Сколько фото в серии?")


@router.message(AdminFlow.adding_session_count, F.text)
async def admin_session_count(message: Message, state: FSMContext) -> None:
    if not message.text.strip().isdigit():
        await message.answer("Введи число.")
        return
    await state.update_data(session_count=int(message.text.strip()))
    await state.set_state(AdminFlow.adding_session_prompts)
    await message.answer(
        "Введи промпты через точку с запятой (;), по одному на каждое фото:\n\n"
        "Пример:\n<i>business portrait, office background; standing pose, city view</i>",
        parse_mode="HTML",
    )


@router.message(AdminFlow.adding_session_prompts, F.text)
async def admin_session_prompts(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    prompts = [p.strip() for p in message.text.split(";") if p.strip()]
    count = data["session_count"]
    if len(prompts) != count:
        await message.answer(
            f"Ожидается {count} промптов, получено {len(prompts)}. Попробуй ещё раз."
        )
        return
    session_id = await db.add_session(
        name=data["session_name"],
        description=data["session_desc"],
        photo_count=count,
        prompts=prompts,
    )
    await state.clear()
    await message.answer(
        f"✅ Фотосессия «{data['session_name']}» добавлена (id={session_id}).",
        reply_markup=admin_menu_kb(),
    )
