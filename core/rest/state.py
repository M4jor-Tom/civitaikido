from fastapi import APIRouter, Depends

from core.constant import main
from core.model import State
from core.provider import get_state_manager
from core.service import StateManager

state_router = APIRouter()

@state_router.get("/get_state", tags=[main])
async def get_state(state_manager: StateManager = Depends(get_state_manager)) -> State | None:
    return state_manager.state
