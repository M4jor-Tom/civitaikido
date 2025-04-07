from fastapi import APIRouter, Depends, Form, File, UploadFile

from core.constant import main
from core.provider import get_routine_executor, get_state_manager
from core.service import RoutineExecutor, StateManager

routine_router = APIRouter()

@routine_router.post("/inject_generate_extract", tags=[main])
async def inject_generate_extract(
        session_url: str = Form(...),
        file: UploadFile = File(...),
        inject_seed: bool = False,
        close_browser_when_finished: bool = True,
        routine_executor: RoutineExecutor = Depends(get_routine_executor),
        state_manager: StateManager = Depends(get_state_manager)
    ):
    try:
        await routine_executor.execute_routine(session_url, file, inject_seed, close_browser_when_finished)
    except TimeoutError as e:
        return f"Failed on state {state_manager.injection_extraction_state.value} with exception: {e}"
