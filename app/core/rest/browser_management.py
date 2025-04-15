from fastapi import APIRouter, Depends
from core.service import BrowserManager, ProfilePreparator
from core.provider import get_browser_manager, get_profile_preparator
from core.constant import low_layer

browser_management_router = APIRouter()

@browser_management_router.post("/open_browser", tags=[low_layer])
async def open_browser(civitai_connection_url: str,
                       browser_manager: BrowserManager = Depends(get_browser_manager),
                       profile_preparator: ProfilePreparator = Depends(get_profile_preparator)):
    await browser_manager.open_browser(civitai_connection_url)
    await profile_preparator.prepare_profile()
    return {"message": "Browser prepared", "url": civitai_connection_url}
