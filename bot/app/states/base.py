"""Common FSM states (placeholder for future flows)."""

from aiogram.fsm.state import State, StatesGroup


class BaseStates(StatesGroup):
    """Base state group for shared flows."""

    idle = State()
