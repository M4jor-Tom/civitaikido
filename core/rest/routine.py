from fastapi import APIRouter, Depends, Form, File, UploadFile

from core.constant import main
from core.provider import get_routine_executor
from core.service import RoutineExecutor

routine_router = APIRouter()

@routine_router.post("/inject_generate_extract", tags=[main])
async def inject_generate_extract(
        session_url: str = Form(...),
        file: UploadFile = File(...),
        inject_seed: bool = False,
        close_browser_when_finished: bool = True,
        routine_executor: RoutineExecutor = Depends(get_routine_executor)
    ):
    await routine_executor.execute_routine(session_url, file, inject_seed, close_browser_when_finished)
