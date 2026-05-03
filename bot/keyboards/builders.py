from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import CHANNEL_URL, PACKAGES
from bot.data.styles import FIRST_PAGE_COUNT


def main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🎨 Выбрать стиль",  callback_data="menu:styles")
    builder.button(text="📸 Фотосессия",     callback_data="menu:sessions")
    builder.button(text="✏️ Свой промпт",    callback_data="menu:custom")
    builder.button(text="💰 Мой баланс",     callback_data="menu:profile")
    builder.button(text="💳 Пополнить",      callback_data="menu:topup")
    builder.button(text="📢 Канал с идеями", url=CHANNEL_URL)
    builder.adjust(1, 2, 2, 1)
    return builder.as_markup()


def styles_kb(styles: list[dict], show_all: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    visible = styles if show_all else styles[:FIRST_PAGE_COUNT]
    for s in visible:
        label = f"{s['emoji']} {s['name']}" if s.get("emoji") else s["name"]
        builder.button(text=label, callback_data=f"style:select:{s['id']}")
    builder.adjust(2)
    if not show_all and len(styles) > FIRST_PAGE_COUNT:
        builder.row(
            InlineKeyboardButton(text="Ещё стили...", callback_data="style:more")
        )
    builder.row(
        InlineKeyboardButton(text="← Меню", callback_data="menu:back")
    )
    return builder.as_markup()


def after_style_kb(style_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Ещё в этом стиле", callback_data=f"style:retry:{style_id}")
    builder.button(text="🎨 Другой стиль",      callback_data="menu:styles")
    builder.button(text="🏠 Главное меню",      callback_data="menu:back")
    builder.adjust(1)
    return builder.as_markup()


def sessions_kb(sessions: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for s in sessions:
        builder.button(
            text=f"{s['name']} ({s['photo_count']} фото)",
            callback_data=f"session:select:{s['id']}",
        )
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="← Меню", callback_data="menu:back"))
    return builder.as_markup()


def session_detail_kb(session_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="▶️ Начать",  callback_data=f"session:start:{session_id}")
    builder.button(text="← Назад",   callback_data="menu:sessions")
    builder.adjust(2)
    return builder.as_markup()


def after_session_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📸 Другая фотосессия", callback_data="menu:sessions")
    builder.button(text="🏠 Главное меню",       callback_data="menu:back")
    builder.adjust(1)
    return builder.as_markup()


def custom_mode_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔧 Конструктор по шагам", callback_data="custom:builder")
    builder.button(text="✍️ Вставить готовый промпт", callback_data="custom:direct")
    builder.button(text="← Меню", callback_data="menu:back")
    builder.adjust(1)
    return builder.as_markup()


def custom_who_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Один человек",         callback_data="custom:who:one")
    builder.button(text="👥 Несколько взрослых",   callback_data="custom:who:group")
    builder.button(text="👨‍👩‍👧 Взрослые и дети",    callback_data="custom:who:family")
    builder.button(text="👶 Только дети",          callback_data="custom:who:kids")
    builder.button(text="🏠 В меню",               callback_data="menu:back")
    builder.adjust(2, 1)
    return builder.as_markup()


def custom_gender_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👩 Женщина",   callback_data="custom:gender:female")
    builder.button(text="👨 Мужчина",   callback_data="custom:gender:male")
    builder.button(text="⏭ Пропустить", callback_data="custom:gender:skip")
    builder.button(text="🏠 В меню",    callback_data="menu:back")
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def custom_style_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💼 Деловой",  callback_data="custom:style:business")
    builder.button(text="👗 Модный",   callback_data="custom:style:fashion")
    builder.button(text="🎨 Арт",      callback_data="custom:style:art")
    builder.button(text="📷 Реализм",  callback_data="custom:style:realism")
    builder.button(text="🧙 Фэнтези",  callback_data="custom:style:fantasy")
    builder.button(text="🏠 В меню",   callback_data="menu:back")
    builder.adjust(2, 1)
    return builder.as_markup()


def custom_location_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🏢 Офис",         callback_data="custom:loc:office")
    builder.button(text="🌿 Природа",      callback_data="custom:loc:nature")
    builder.button(text="🏙 Город",        callback_data="custom:loc:city")
    builder.button(text="🎭 Студия",       callback_data="custom:loc:studio")
    builder.button(text="✍️ Написать свой", callback_data="custom:loc:custom")
    builder.button(text="🏠 В меню",       callback_data="menu:back")
    builder.adjust(2, 1)
    return builder.as_markup()


def custom_details_skip_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⏭ Пропустить", callback_data="custom:details:skip")
    builder.button(text="🏠 В меню",    callback_data="menu:back")
    builder.adjust(1)
    return builder.as_markup()


def custom_review_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 Генерировать",      callback_data="custom:generate")
    builder.button(text="🔄 Изменить с шага 1", callback_data="custom:restart")
    builder.button(text="🏠 В меню",            callback_data="menu:back")
    builder.adjust(1)
    return builder.as_markup()


def after_custom_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Сгенерировать снова", callback_data="custom:regenerate")
    builder.button(text="🏠 Главное меню",         callback_data="menu:back")
    builder.adjust(1)
    return builder.as_markup()


def paywall_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for pkg in PACKAGES:
        builder.button(text=pkg["label"], callback_data=f"pay:pkg:{pkg['id']}")
    builder.row(InlineKeyboardButton(text="← Назад", callback_data="menu:back"))
    builder.adjust(1)
    return builder.as_markup()


def payment_link_kb(url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Оплатить", url=url)
    builder.button(text="← Назад к пакетам", callback_data="pay:back")
    builder.adjust(1)
    return builder.as_markup()


def after_payment_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="▶️ Продолжить", callback_data="menu:styles")
    builder.button(text="🏠 В меню", callback_data="menu:back")
    builder.adjust(1)
    return builder.as_markup()


def subscribe_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📢 Подписаться на канал", url=CHANNEL_URL)
    builder.button(text="✅ Я подписался",          callback_data="subscribe:check")
    builder.button(text="🏠 В меню",               callback_data="menu:back")
    builder.adjust(1)
    return builder.as_markup()


def profile_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Пополнить баланс", callback_data="menu:topup")
    builder.button(text="👥 Пригласить друга", callback_data="profile:referral")
    builder.button(text="🏠 Главное меню",     callback_data="menu:back")
    builder.adjust(2, 1)
    return builder.as_markup()


def cancel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✖️ Отмена", callback_data="menu:back")
    return builder.as_markup()


def back_to_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 Главное меню", callback_data="menu:back")
    return builder.as_markup()


def paywall_reminder_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Пополнить баланс", callback_data="menu:topup")
    builder.button(text="🏠 В меню",           callback_data="menu:back")
    builder.adjust(1)
    return builder.as_markup()


# ─── Admin ────────────────────────────────────────────────────────────────────

def admin_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Статистика",        callback_data="admin:stats")
    builder.button(text="📣 Рассылка",          callback_data="admin:broadcast")
    builder.button(text="💰 Начислить кредиты", callback_data="admin:add_credits")
    builder.button(text="🚫 Заблокировать",     callback_data="admin:block")
    builder.button(text="🎨 Добавить стиль",    callback_data="admin:add_style")
    builder.button(text="📸 Добавить сессию",   callback_data="admin:add_session")
    builder.adjust(2)
    return builder.as_markup()


def admin_confirm_broadcast_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Отправить всем", callback_data="admin:broadcast_confirm")
    builder.button(text="✖️ Отмена",         callback_data="admin:cancel")
    builder.adjust(2)
    return builder.as_markup()


def admin_cancel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✖️ Отмена", callback_data="admin:cancel")
    return builder.as_markup()
