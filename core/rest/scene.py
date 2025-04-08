from fastapi import APIRouter, Depends

from core.constant import main
from core.model import Scene
from core.provider import get_scene_manager
from core.service import SceneManager

scene_router = APIRouter()

@scene_router.get("/get_scene", tags=[main])
async def get_scene(scene_manager: SceneManager = Depends(get_scene_manager)) -> Scene:
    return await scene_manager.build_scene()
