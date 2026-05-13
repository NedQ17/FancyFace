from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import database as db
from bot.keyboards.builders import main_menu_kb

router = Router()


async def show_main_menu(target: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    text = "Главное меню — выбери, что хочешь сделать:"
    kb = main_menu_kb()
    if isinstance(target, CallbackQuery):
        try:
            await target.message.edit_text(text, reply_markup=kb)
        except Exception:
            await target.message.answer(text, reply_markup=kb)
        await target.answer()
    else:
        await target.answer(text, reply_markup=kb)


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext) -> None:
    await show_main_menu(message, state)


@router.callback_query(F.data == "menu:back")
async def menu_back(callback: CallbackQuery, state: FSMContext) -> None:
    await show_main_menu(callback, state)


@router.callback_query(F.data == "menu:info")
async def menu_info(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(
        'Контакты, оферта, политика обработки персональных данных сервиса:\n'
        '<a href="https://avocadophotobot.github.io/legal/">avocadophotobot.github.io/legal</a>',
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@router.message(StateFilter(None), F.photo | F.document)
async def fallback_photo(message: Message) -> None:
    await message.answer(
        "Чтобы создать фото, сначала выбери стиль или запусти конструктор.",
        reply_markup=main_menu_kb(),
    )


@router.message(StateFilter(None), F.text & ~F.text.startswith("/"))
async def fallback_text(message: Message) -> None:
    await message.answer(
        "Не понимаю эту команду. Используй меню ниже.",
        reply_markup=main_menu_kb(),
    )
