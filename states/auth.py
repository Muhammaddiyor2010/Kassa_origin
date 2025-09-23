from aiogram.fsm.state import State, StatesGroup

class TokenStates(StatesGroup):
    waiting_for_token = State()

class AdminTokenStates(StatesGroup):
    waiting_for_admin_token = State()

