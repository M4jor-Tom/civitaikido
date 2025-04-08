from fastapi import APIRouter, Depends, Form, File, UploadFile
from playwright.async_api import TimeoutError

from core.constant import main
from core.model.injection_extraction_state import InjectionExtractionState
from core.provider import get_routine_executor, get_scene_manager
from core.service import RoutineExecutor, SceneManager

routine_router = APIRouter()

@routine_router.post("/inject_generate_extract", tags=[main])
async def inject_generate_extract(
        session_url: str = Form(...),
        file: UploadFile = File(...),
        inject_seed: bool = False,
        close_browser_when_finished: bool = True,
        routine_executor: RoutineExecutor = Depends(get_routine_executor),
        scene_manager: SceneManager = Depends(get_scene_manager),
        overridden_state: InjectionExtractionState | None = None,
        open_new_browser: bool = True
    ):
    try:
        await routine_executor.execute_routine(
            session_url=session_url,
            file=file,
            inject_seed=inject_seed,
            open_new_browser=open_new_browser,
            close_browser_when_finished=close_browser_when_finished,
            overridden_state=overridden_state)
        return await scene_manager.build_scene()
    except TimeoutError as e:
        return f"Failed on scene {await scene_manager.build_scene()} with exception: {e}"
