from fastapi import APIRouter, Depends
from src.service import BrowserManager, CivitaiPagePreparator
from src.provider import get_browser_manager, get_civitai_page_preparator

browser_management_router = APIRouter()

@browser_management_router.post("/open_browser")
async def open_browser(civitai_connection_url: str, ask_first_session_preparation: bool,
                       browser_manager: BrowserManager = Depends(get_browser_manager),
                       civitai_page_preparator: CivitaiPagePreparator = Depends(get_civitai_page_preparator)):
    await browser_manager.open_browser(civitai_connection_url)
    await civitai_page_preparator.prepare_civitai_page(ask_first_session_preparation)
    return {"message": "Browser prepared", "url": civitai_connection_url}
