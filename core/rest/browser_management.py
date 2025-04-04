import asyncio

from fastapi import APIRouter, Depends
from core.service import BrowserManager, CivitaiPagePreparator, PopupRemover
from core.provider import get_browser_manager, get_civitai_page_preparator, get_popup_remover
from core.constant import low_layer

browser_management_router = APIRouter()

@browser_management_router.post("/open_browser", tags=[low_layer])
async def open_browser(civitai_connection_url: str, ask_first_session_preparation: bool,
                       browser_manager: BrowserManager = Depends(get_browser_manager),
                       civitai_page_preparator: CivitaiPagePreparator = Depends(get_civitai_page_preparator),
                       popup_remover: PopupRemover = Depends(get_popup_remover)):
    await browser_manager.open_browser(civitai_connection_url)
    await asyncio.gather(
        popup_remover.remove_popups(ask_first_session_preparation),
        civitai_page_preparator.prepare_civitai_page(ask_first_session_preparation)
    )
    return {"message": "Browser prepared", "url": civitai_connection_url}
