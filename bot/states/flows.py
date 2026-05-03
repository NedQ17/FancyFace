from aiogram.fsm.state import State, StatesGroup


class StyleFlow(StatesGroup):
    waiting_photo = State()


class SessionFlow(StatesGroup):
    waiting_photo = State()


class CustomFlow(StatesGroup):
    step1_who = State()
    step2_gender = State()
    step3_style = State()
    step4_location = State()
    step4_custom_location = State()
    step5_details = State()
    waiting_direct_prompt = State()
    waiting_photo = State()


class AdminFlow(StatesGroup):
    waiting_broadcast = State()
    broadcast_confirm = State()
    waiting_user_id_credits = State()
    waiting_credits_amount = State()
    waiting_user_id_block = State()
    adding_style_name = State()
    adding_style_emoji = State()
    adding_style_prompt = State()
    adding_session_name = State()
    adding_session_description = State()
    adding_session_count = State()
    adding_session_prompts = State()
