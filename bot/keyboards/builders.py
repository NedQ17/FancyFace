from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import CHANNEL_URL, PACKAGES
from bot.data.styles import FIRST_PAGE_COUNT


def main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🎨 Выбрать стиль",  callback_data="menu:styles")
    builder.button(text="✏️ Свой промпт",    callback_data="menu:custom")
    builder.button(text="💰 Мой баланс",     callback_data="menu:profile")
    builder.button(text="💳 Пополнить",      callback_data="menu:topup")
    builder.button(text="📢 Канал с идеями", url=CHANNEL_URL)
    builder.adjust(1, 1, 2, 1)
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
    builder.button(text="🔧 Конструктор по шагам",   callback_data="custom:builder")
    builder.button(text="✍️ Вставить готовый промпт", callback_data="custom:direct")
    builder.button(text="← Меню",                    callback_data="menu:back")
    builder.adjust(1)
    return builder.as_markup()


def custom_gender_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Женщина",    callback_data="custom:gender:female")
    builder.button(text="Мужчина",    callback_data="custom:gender:male")
    builder.button(text="Пропустить", callback_data="custom:gender:skip")
    builder.button(text="В меню",     callback_data="menu:back")
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def custom_category_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Деловой",          callback_data="custom:category:business")
    builder.button(text="Портрет",          callback_data="custom:category:portrait")
    builder.button(text="Фотореализм",      callback_data="custom:category:photorealism")
    builder.button(text="Лайфстайл",        callback_data="custom:category:lifestyle")
    builder.button(text="Кинематографичный", callback_data="custom:category:cinematic")
    builder.button(text="Арт стиль",        callback_data="custom:category:art")
    builder.button(text="В меню",           callback_data="menu:back")
    builder.adjust(2, 2, 2, 1)
    return builder.as_markup()


def custom_framing_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Бюст (голова-плечи)", callback_data="custom:framing:bust")
    builder.button(text="По пояс",             callback_data="custom:framing:waist")
    builder.button(text="В полный рост",       callback_data="custom:framing:full")
    builder.button(text="В меню",              callback_data="menu:back")
    builder.adjust(1)
    return builder.as_markup()


def custom_render_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Реализм",           callback_data="custom:render:realism")
    builder.button(text="Лёгкая стилизация", callback_data="custom:render:stylized")
    builder.button(text="Арт стиль",         callback_data="custom:render:art")
    builder.button(text="В меню",            callback_data="menu:back")
    builder.adjust(1)
    return builder.as_markup()


def custom_mood_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Спокойное",   callback_data="custom:mood:calm")
    builder.button(text="Довольное",   callback_data="custom:mood:pleased")
    builder.button(text="Серьёзное",   callback_data="custom:mood:serious")
    builder.button(text="Романтичное", callback_data="custom:mood:romantic")
    builder.button(text="Деловое",     callback_data="custom:mood:business")
    builder.button(text="В меню",      callback_data="menu:back")
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup()


def custom_clothing_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Оставить оригинальную одежду", callback_data="custom:clothing:keep")
    builder.button(text="Заменить одежду",              callback_data="custom:clothing:replace")
    builder.button(text="В меню",                       callback_data="menu:back")
    builder.adjust(1)
    return builder.as_markup()


def custom_clothing_type_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Кэжуал",          callback_data="custom:ctype:casual")
    builder.button(text="Классическая",    callback_data="custom:ctype:classic")
    builder.button(text="Бизнес",          callback_data="custom:ctype:business")
    builder.button(text="Фестиваль",       callback_data="custom:ctype:festival")
    builder.button(text="Историческая",    callback_data="custom:ctype:historical")
    builder.button(text="Минимализм",      callback_data="custom:ctype:minimal")
    builder.button(text="Описать самому",  callback_data="custom:ctype:custom")
    builder.button(text="В меню",          callback_data="menu:back")
    builder.adjust(2, 2, 2, 1, 1)
    return builder.as_markup()


def custom_background_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Студия",          callback_data="custom:bg:studio")
    builder.button(text="Город",           callback_data="custom:bg:city")
    builder.button(text="Природа",         callback_data="custom:bg:nature")
    builder.button(text="Улица",           callback_data="custom:bg:street")
    builder.button(text="Интерьер",        callback_data="custom:bg:interior")
    builder.button(text="Размытый фон",    callback_data="custom:bg:blurred")
    builder.button(text="Описать самому",  callback_data="custom:bg:custom")
    builder.button(text="В меню",          callback_data="menu:back")
    builder.adjust(2, 2, 2, 1, 1)
    return builder.as_markup()


def custom_lighting_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Естественный свет", callback_data="custom:light:natural")
    builder.button(text="Мягкий свет",       callback_data="custom:light:soft")
    builder.button(text="Контровой свет",    callback_data="custom:light:backlit")
    builder.button(text="Кинематографичный", callback_data="custom:light:cinematic")
    builder.button(text="В меню",            callback_data="menu:back")
    builder.adjust(2, 2, 1)
    return builder.as_markup()


DETAILS_OPTIONS = [
    ("candles", "Свечи"),
    ("flowers", "Цветы"),
    ("plants",  "Растения"),
    ("fabrics", "Ткани/драпировки"),
    ("minimal", "Минималистичный декор"),
    ("custom",  "Описать самому"),
]

RESTRICTIONS_OPTIONS = [
    ("no_pose",       "Не менять позу"),
    ("no_expression", "Не менять выражение лица"),
    ("no_hair",       "Не менять причёску"),
    ("no_objects",    "Не добавлять объекты в руки"),
]


def custom_details_kb(selected: set[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, label in DETAILS_OPTIONS:
        prefix = "✅ " if key in selected else ""
        builder.button(text=f"{prefix}{label}", callback_data=f"custom:detail:{key}")
    next_label = "→ Далее" if selected - {"custom"} else "Пропустить"
    builder.button(text=next_label, callback_data="custom:detail:done")
    builder.button(text="В меню", callback_data="menu:back")
    builder.adjust(2, 2, 1, 1, 1)
    return builder.as_markup()


def custom_era_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Пятидесятые", callback_data="custom:era:50s")
    builder.button(text="Семидесятые", callback_data="custom:era:70s")
    builder.button(text="Девяностые",  callback_data="custom:era:90s")
    builder.button(text="Нулевые",     callback_data="custom:era:00s")
    builder.button(text="Пропустить",  callback_data="custom:era:skip")
    builder.button(text="В меню",      callback_data="menu:back")
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup()


def custom_restrictions_kb(selected: set[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, label in RESTRICTIONS_OPTIONS:
        prefix = "✅ " if key in selected else ""
        builder.button(text=f"{prefix}{label}", callback_data=f"custom:restrict:{key}")
    next_label = "→ Далее" if selected else "Пропустить"
    builder.button(text=next_label, callback_data="custom:restrict:done")
    builder.button(text="В меню", callback_data="menu:back")
    builder.adjust(1)
    return builder.as_markup()


def custom_review_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Сгенерировать", callback_data="custom:generate")
    builder.button(text="Начать заново", callback_data="custom:restart")
    builder.button(text="В меню",        callback_data="menu:back")
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
