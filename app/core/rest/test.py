from fastapi import APIRouter, Depends

from core.provider import get_browser_manager
from core.service import BrowserManager
from core.constant import dev

test_router = APIRouter()

@test_router.get("/test", tags=[dev])
async def test(
        url: str,
        browser_manager: BrowserManager = Depends(get_browser_manager)
    ):
    await browser_manager.open_browser(url)
