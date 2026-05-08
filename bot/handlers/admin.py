import asyncio
import io
import re
from datetime import datetime, timedelta, timezone

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message, CallbackQuery

from bot import database as db
from bot.config import ADMIN_IDS, BOT_USERNAME, PACKAGES
from bot.keyboards.builders import (
    admin_menu_kb, admin_confirm_broadcast_kb, admin_cancel_kb,
    admin_sales_period_kb, admin_sales_back_kb,
    admin_styles_menu_kb, admin_styles_kb, admin_style_edit_kb, admin_style_delete_confirm_kb,
)
from bot.services.generation import generate_portrait, upload_photo, download_image, GenerationError
from bot.states.flows import AdminFlow

router = Router()

# Защита на уровне роутера — ни один хендлер не достижим для не-администраторов
router.message.filter(F.from_user.id.in_(set(ADMIN_IDS)))
router.callback_query.filter(F.from_user.id.in_(set(ADMIN_IDS)))

_PACKAGE_LABELS: dict[str, str] = {pkg["id"]: pkg["label"] for pkg in PACKAGES}


# ─── Entry ────────────────────────────────────────────────────────────────────

@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "👑 <b>Панель администратора</b>",
        parse_mode="HTML",
        reply_markup=admin_menu_kb(),
    )


@router.callback_query(F.data == "admin:cancel")
async def admin_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    try:
        await callback.message.edit_text(
            "👑 <b>Панель администратора</b>",
            parse_mode="HTML",
            reply_markup=admin_menu_kb(),
        )
    except Exception:
        await callback.message.delete()
        await callback.message.answer(
            "👑 <b>Панель администратора</b>",
            parse_mode="HTML",
            reply_markup=admin_menu_kb(),
        )
    await callback.answer()


# ─── Statistics ───────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery) -> None:
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


# ─── Sales ────────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:sales")
async def admin_sales_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "💰 <b>Продажи</b>\n\nВыбери период:",
        parse_mode="HTML",
        reply_markup=admin_sales_period_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.in_({"admin:sales:today", "admin:sales:week", "admin:sales:month"}))
async def admin_sales_preset(callback: CallbackQuery) -> None:
    now = datetime.now(tz=timezone.utc)
    if callback.data == "admin:sales:today":
        from_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
        label = "сегодня"
    elif callback.data == "admin:sales:week":
        from_dt = (now - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        label = "последние 7 дней"
    else:
        from_dt = (now - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
        label = "последние 30 дней"

    stats = await db.get_sales_stats(from_dt, now)
    await callback.message.edit_text(
        _format_sales(stats, label),
        parse_mode="HTML",
        reply_markup=admin_sales_back_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:sales:custom")
async def admin_sales_custom_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminFlow.waiting_sales_date_range)
    await callback.message.edit_text(
        "Введи диапазон дат в формате:\n"
        "<code>ДД.ММ.ГГГГ-ДД.ММ.ГГГГ</code>\n\n"
        "Пример: <code>01.04.2025-30.04.2025</code>",
        parse_mode="HTML",
        reply_markup=admin_cancel_kb(),
    )
    await callback.answer()


@router.message(AdminFlow.waiting_sales_date_range, F.text)
async def admin_sales_custom_range(message: Message, state: FSMContext) -> None:
    text = message.text.strip().replace(" ", "")
    match = re.fullmatch(r"(\d{2}\.\d{2}\.\d{4})-(\d{2}\.\d{2}\.\d{4})", text)
    if not match:
        await message.answer(
            "Неверный формат. Попробуй ещё раз:\n"
            "<code>ДД.ММ.ГГГГ-ДД.ММ.ГГГГ</code>",
            parse_mode="HTML",
        )
        return

    try:
        from_dt = datetime.strptime(match.group(1), "%d.%m.%Y").replace(tzinfo=timezone.utc)
        to_dt = datetime.strptime(match.group(2), "%d.%m.%Y").replace(
            hour=23, minute=59, second=59, tzinfo=timezone.utc
        )
    except ValueError:
        await message.answer("Неверная дата. Проверь числа и попробуй ещё раз.")
        return

    if from_dt > to_dt:
        await message.answer("Начало диапазона не может быть позже конца.")
        return

    await state.clear()
    stats = await db.get_sales_stats(from_dt, to_dt)
    label = f"{match.group(1)} — {match.group(2)}"
    await message.answer(
        _format_sales(stats, label),
        parse_mode="HTML",
        reply_markup=admin_sales_back_kb(),
    )


def _format_sales(stats: dict, period_label: str) -> str:
    total_count = stats["total_count"]
    total_rub = stats["total_rub"]
    breakdown = stats["breakdown"]

    lines = [f"💰 <b>Продажи — {period_label}</b>\n"]

    if total_count == 0:
        lines.append("Покупок не было.")
        return "\n".join(lines)

    lines.append(f"📦 Покупок: <b>{total_count}</b>")
    lines.append(f"💵 Выручка: <b>{total_rub:,} ₽</b>\n".replace(",", " "))
    lines.append("По пакетам:")

    for row in breakdown:
        pkg_id = row["package_id"]
        label = _PACKAGE_LABELS.get(pkg_id, pkg_id)
        count = row["count"]
        rub = row["total_rub"]
        lines.append(f"  • {label} — {count} шт → <b>{rub:,} ₽</b>".replace(",", " "))

    return "\n".join(lines)


# ─── Broadcast ────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminFlow.waiting_broadcast)
    await callback.message.edit_text(
        "Отправь сообщение для рассылки (текст, фото или фото с подписью).",
        reply_markup=admin_cancel_kb(),
    )
    await callback.answer()


@router.message(AdminFlow.waiting_broadcast, F.text | F.photo)
async def admin_broadcast_preview(message: Message, state: FSMContext) -> None:
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
    await state.set_state(AdminFlow.waiting_user_id_credits)
    await callback.message.edit_text(
        "Введи user_id пользователя:", reply_markup=admin_cancel_kb()
    )
    await callback.answer()


@router.message(AdminFlow.waiting_user_id_credits, F.text)
async def admin_credits_user(message: Message, state: FSMContext) -> None:
    if not message.text.strip().isdigit():
        await message.answer("Введи числовой user_id.")
        return
    await state.update_data(target_user_id=int(message.text.strip()))
    await state.set_state(AdminFlow.waiting_credits_amount)
    await message.answer("Сколько кредитов начислить?", reply_markup=admin_cancel_kb())


@router.message(AdminFlow.waiting_credits_amount, F.text)
async def admin_credits_amount(message: Message, state: FSMContext) -> None:
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
    await state.set_state(AdminFlow.waiting_user_id_block)
    await callback.message.edit_text(
        "Введи user_id для блокировки (или разблокировки):",
        reply_markup=admin_cancel_kb(),
    )
    await callback.answer()


@router.message(AdminFlow.waiting_user_id_block, F.text)
async def admin_block_user(message: Message, state: FSMContext) -> None:
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


# ─── Styles editor ────────────────────────────────────────────────────────────

async def _show_styles_submenu(target, state: FSMContext) -> None:
    await state.clear()
    text = "🎨 <b>Стили</b>\n\nВыбери раздел:"
    kb = admin_styles_menu_kb()
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        await target.answer()
    else:
        await target.answer(text, parse_mode="HTML", reply_markup=kb)


@router.callback_query(F.data == "admin:styles")
async def admin_styles(callback: CallbackQuery, state: FSMContext) -> None:
    await _show_styles_submenu(callback, state)


@router.callback_query(F.data == "admin:styles:bot")
async def admin_styles_bot(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    styles = await db.get_styles(active_only=False, listed_only=True)
    await callback.message.edit_text(
        "🎨 <b>Стили бота</b>\n\nВыбери стиль для изменения:",
        parse_mode="HTML",
        reply_markup=admin_styles_kb(styles, page=0, section="bot"),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:styles:channel")
async def admin_styles_channel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    all_styles = await db.get_styles(active_only=False, listed_only=False, newest_first=True)
    styles = [s for s in all_styles if not s.get("show_in_list", True)]
    await callback.message.edit_text(
        "📢 <b>Стили для канала</b>\n\nВыбери стиль для изменения:",
        parse_mode="HTML",
        reply_markup=admin_styles_kb(styles, page=0, section="channel"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:styles:bot:page:"))
async def admin_styles_bot_page(callback: CallbackQuery, state: FSMContext) -> None:
    page = int(callback.data.split(":")[4])
    await state.clear()
    styles = await db.get_styles(active_only=False, listed_only=True)
    await callback.message.edit_reply_markup(reply_markup=admin_styles_kb(styles, page=page, section="bot"))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:styles:channel:page:"))
async def admin_styles_channel_page(callback: CallbackQuery, state: FSMContext) -> None:
    page = int(callback.data.split(":")[4])
    await state.clear()
    all_styles = await db.get_styles(active_only=False, listed_only=False, newest_first=True)
    styles = [s for s in all_styles if not s.get("show_in_list", True)]
    await callback.message.edit_reply_markup(reply_markup=admin_styles_kb(styles, page=page, section="channel"))
    await callback.answer()


# ─── Style: view & edit menu ──────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:style:edit:"))
async def admin_style_edit_menu(callback: CallbackQuery) -> None:
    style_id = int(callback.data.split(":")[3])
    style = await db.get_style(style_id)
    if not style:
        await callback.answer("Стиль не найден.", show_alert=True)
        return
    prompt_preview = (style["prompt"] or "")[:80]
    if len(style["prompt"] or "") > 80:
        prompt_preview += "…"
    text = (
        f"✏️ <b>{style['name']}</b>\n\n"
        f"<i>Промпт:</i> {prompt_preview}"
    )
    await callback.message.edit_text(
        text, parse_mode="HTML", reply_markup=admin_style_edit_kb(style)
    )
    await callback.answer()


# ─── Style: edit name ─────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:style:name:"))
async def admin_style_name_start(callback: CallbackQuery, state: FSMContext) -> None:
    style_id = int(callback.data.split(":")[3])
    style = await db.get_style(style_id)
    if not style:
        await callback.answer("Стиль не найден.", show_alert=True)
        return
    await state.set_state(AdminFlow.editing_style_name)
    await state.update_data(editing_style_id=style_id)
    await callback.message.edit_text(
        f"Текущее название: <b>{style['name']}</b>\n\nВведи новое название:",
        parse_mode="HTML",
        reply_markup=admin_cancel_kb(),
    )
    await callback.answer()


@router.message(AdminFlow.editing_style_name, F.text)
async def admin_style_name_save(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    style_id = data["editing_style_id"]
    new_name = message.text.strip()
    await db.update_style_name(style_id, new_name)
    await state.clear()
    style = await db.get_style(style_id)
    await message.answer(
        f"✅ Название обновлено: <b>{new_name}</b>",
        parse_mode="HTML",
        reply_markup=admin_style_edit_kb(style),
    )


# ─── Style: edit emoji ────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:style:emoji:"))
async def admin_style_emoji_start(callback: CallbackQuery, state: FSMContext) -> None:
    style_id = int(callback.data.split(":")[3])
    style = await db.get_style(style_id)
    if not style:
        await callback.answer("Стиль не найден.", show_alert=True)
        return
    current = style.get("emoji") or "—"
    await state.set_state(AdminFlow.editing_style_emoji)
    await state.update_data(editing_style_id=style_id)
    await callback.message.edit_text(
        f"Текущий эмодзи: <b>{current}</b>\n\n"
        "Отправь новый эмодзи или «-» чтобы убрать:",
        parse_mode="HTML",
        reply_markup=admin_cancel_kb(),
    )
    await callback.answer()


@router.message(AdminFlow.editing_style_emoji, F.text)
async def admin_style_emoji_save(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    style_id = data["editing_style_id"]
    new_emoji = "" if message.text.strip() == "-" else message.text.strip()
    await db.update_style_emoji(style_id, new_emoji)
    await state.clear()
    style = await db.get_style(style_id)
    display = new_emoji or "—"
    await message.answer(
        f"✅ Эмодзи обновлён: <b>{display}</b>",
        parse_mode="HTML",
        reply_markup=admin_style_edit_kb(style),
    )


# ─── Style: edit prompt ───────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:style:prompt:"))
async def admin_style_prompt_start(callback: CallbackQuery, state: FSMContext) -> None:
    style_id = int(callback.data.split(":")[3])
    style = await db.get_style(style_id)
    if not style:
        await callback.answer("Стиль не найден.", show_alert=True)
        return
    await state.set_state(AdminFlow.editing_style_prompt)
    await state.update_data(editing_style_id=style_id)
    current_prompt = style.get("prompt") or "(пусто)"
    await callback.message.edit_text(
        f"<b>Текущий промпт:</b>\n\n<i>{current_prompt}</i>\n\n"
        "Введи новый промпт (на английском):",
        parse_mode="HTML",
        reply_markup=admin_cancel_kb(),
    )
    await callback.answer()


@router.message(AdminFlow.editing_style_prompt, F.text)
async def admin_style_prompt_save(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    style_id = data["editing_style_id"]
    new_prompt = message.text.strip()
    await db.update_style_prompt(style_id, new_prompt)
    await state.clear()
    style = await db.get_style(style_id)
    await message.answer(
        "✅ Промпт сохранён.",
        reply_markup=admin_style_edit_kb(style),
    )


# ─── Style: delete ───────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:style:delete:"))
async def admin_style_delete(callback: CallbackQuery) -> None:
    parts = callback.data.split(":")
    # distinguish "admin:style:delete:{id}" from "admin:style:delete:confirm:{id}"
    if parts[4] == "confirm":
        style_id = int(parts[5])
        style = await db.get_style(style_id)
        name = style["name"] if style else f"id={style_id}"
        await db.delete_style(style_id)
        await callback.message.edit_text(
            f"🗑 Стиль «{name}» удалён.\n\n"
            "🎨 <b>Стили</b>\n\nВыбери раздел:",
            parse_mode="HTML",
            reply_markup=admin_styles_menu_kb(),
        )
    else:
        style_id = int(parts[3])
        style = await db.get_style(style_id)
        if not style:
            await callback.answer("Стиль не найден.", show_alert=True)
            return
        await callback.message.edit_text(
            f"Удалить стиль <b>«{style['name']}»</b>?\n\nЭто действие необратимо.",
            parse_mode="HTML",
            reply_markup=admin_style_delete_confirm_kb(style_id),
        )
    await callback.answer()


# ─── Style: toggle visibility ────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:style:visibility:"))
async def admin_style_toggle_visibility(callback: CallbackQuery) -> None:
    style_id = int(callback.data.split(":")[3])
    style = await db.get_style(style_id)
    if not style:
        await callback.answer("Стиль не найден.", show_alert=True)
        return
    new_visibility = not style.get("show_in_list", True)
    await db.update_style_visibility(style_id, new_visibility)
    style = await db.get_style(style_id)
    status = "виден в списке" if new_visibility else "скрыт из списка"
    await callback.answer(f"Стиль теперь {status}.", show_alert=False)
    prompt_preview = (style["prompt"] or "")[:80]
    if len(style["prompt"] or "") > 80:
        prompt_preview += "…"
    text = (
        f"✏️ <b>{style['name']}</b>\n\n"
        f"<i>Промпт:</i> {prompt_preview}"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=admin_style_edit_kb(style))


# ─── Style: deep link ────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:style:link:"))
async def admin_style_show_link(callback: CallbackQuery) -> None:
    style_id = int(callback.data.split(":")[3])
    style = await db.get_style(style_id)
    if not style:
        await callback.answer("Стиль не найден.", show_alert=True)
        return
    link = f"https://t.me/{BOT_USERNAME}?start=style_{style_id}"
    await callback.answer()
    await callback.message.answer(
        f"🔗 Ссылка для стиля <b>{style['name']}</b>:\n\n"
        f"<code>{link}</code>\n\n"
        "Скопируй и вставь в пост канала.",
        parse_mode="HTML",
    )


# ─── Style: add new ───────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:style:add")
async def admin_add_style_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminFlow.adding_style_name)
    await callback.message.edit_text(
        "Введи название нового стиля:", reply_markup=admin_cancel_kb()
    )
    await callback.answer()


@router.message(AdminFlow.adding_style_name, F.text)
async def admin_style_new_name(message: Message, state: FSMContext) -> None:
    await state.update_data(style_name=message.text.strip())
    await state.set_state(AdminFlow.adding_style_emoji)
    await message.answer("Введи эмодзи для стиля (или «-» без эмодзи):")


@router.message(AdminFlow.adding_style_emoji, F.text)
async def admin_style_new_emoji(message: Message, state: FSMContext) -> None:
    emoji = message.text.strip()
    if emoji == "-":
        emoji = ""
    await state.update_data(style_emoji=emoji)
    await state.set_state(AdminFlow.adding_style_prompt)
    await message.answer("Введи промпт для этого стиля (на английском):")


@router.message(AdminFlow.adding_style_prompt, F.text)
async def admin_style_new_prompt(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    style_id = await db.add_style(
        name=data["style_name"],
        emoji=data["style_emoji"],
        prompt=message.text.strip(),
    )
    await state.clear()
    await message.answer(f"✅ Стиль «{data['style_name']}» добавлен (id={style_id}).")
    await _show_styles_submenu(message, state)


# ─── Playground ───────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:playground")
async def admin_playground_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminFlow.playground_prompt)
    await callback.message.edit_text(
        "🧪 <b>Playground</b>\n\n"
        "Введи промпт на английском.\n"
        "Можно вставить готовый или написать с нуля.",
        parse_mode="HTML",
        reply_markup=admin_cancel_kb(),
    )
    await callback.answer()


@router.message(AdminFlow.playground_prompt, F.text)
async def admin_playground_prompt(message: Message, state: FSMContext) -> None:
    await state.update_data(playground_prompt=message.text.strip())
    await state.set_state(AdminFlow.playground_photo)
    await message.answer(
        "Теперь отправь фото (selfie или портрет).",
        reply_markup=admin_cancel_kb(),
    )


@router.message(AdminFlow.playground_photo, F.photo | F.document)
async def admin_playground_photo(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    prompt = data["playground_prompt"]
    await state.clear()

    status_msg = await message.answer("Генерирую... ⏳")

    try:
        if message.photo:
            file = await bot.get_file(message.photo[-1].file_id)
        elif message.document and (message.document.mime_type or "").startswith("image/"):
            file = await bot.get_file(message.document.file_id)
        else:
            await status_msg.edit_text("Нужно фото или изображение.")
            return
        buf = io.BytesIO()
        await bot.download_file(file.file_path, destination=buf)
        photo_bytes = buf.getvalue()
    except Exception:
        await status_msg.edit_text("Не удалось прочитать фото.")
        return

    try:
        face_url = await upload_photo(photo_bytes)
        result_url = await generate_portrait(face_url, prompt)
        result_bytes = await download_image(result_url)
    except GenerationError as exc:
        await status_msg.edit_text(f"Ошибка генерации: {exc}")
        return

    await status_msg.delete()
    await message.answer_photo(
        BufferedInputFile(result_bytes, filename="result.jpg"),
    )
