from fastapi import APIRouter, Depends, Form, File, UploadFile

from core.constant import main
from core.model import State, InjectionExtractionState
from core.provider import get_routine_executor, get_state_manager
from core.service import RoutineExecutor, StateManager

routine_router = APIRouter()

@routine_router.post("/inject_generate_extract", tags=[main])
async def inject_generate_extract(
        session_url: str = Form(...),
        file: UploadFile = File(...),
        inject_seed: bool = False,
        close_browser_when_finished: bool = True,
        prompt_hash_in_generation_dir: bool = False,
        routine_executor: RoutineExecutor = Depends(get_routine_executor),
        state_manager: StateManager = Depends(get_state_manager),
        start_state: InjectionExtractionState = InjectionExtractionState.INIT
    ):
    try:
        output_state: State = await routine_executor.execute_routine(
            session_url=session_url,
            file=file,
            inject_seed=inject_seed,
            close_browser_when_finished=close_browser_when_finished,
            prompt_hash_in_generation_dir=prompt_hash_in_generation_dir,
            start_state=start_state)
        return f"Exited on state {output_state}"
    except Exception as e:
        return f"Failed on state {state_manager.state} with exception: {e}"
