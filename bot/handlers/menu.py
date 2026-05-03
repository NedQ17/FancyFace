from aiogram import Router, F
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


@router.callback_query(F.data == "menu:back")
async def menu_back(callback: CallbackQuery, state: FSMContext) -> None:
    await show_main_menu(callback, state)
