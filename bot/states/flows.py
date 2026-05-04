from aiogram.fsm.state import State, StatesGroup


class StyleFlow(StatesGroup):
    waiting_photo = State()


class SessionFlow(StatesGroup):
    waiting_photo = State()


class CustomFlow(StatesGroup):
    step1_gender = State()
    step2_category = State()
    step3_framing = State()
    step4_render = State()
    step5_mood = State()
    step6_clothing = State()
    step6b_clothing_type = State()
    step6b_clothing_custom = State()
    step7_background = State()
    step7b_background_custom = State()
    step8_lighting = State()
    step9_details = State()
    step9_details_custom = State()
    step10_restrictions = State()
    step11_era = State()
    step_review = State()
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
