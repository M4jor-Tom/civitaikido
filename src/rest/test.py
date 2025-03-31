from fastapi import APIRouter, Depends, Form

from src.provider import get_browser_manager
from src.service import BrowserManager
from src.constant import dev

test_router = APIRouter()

@test_router.get("/test", tags=[dev])
async def test(
        url: str = Form(...),
        browser_manager: BrowserManager = Depends(get_browser_manager)
    ):
    await browser_manager.open_browser(url)
