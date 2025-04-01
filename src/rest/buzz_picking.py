from fastapi import APIRouter, Depends, Form, File, UploadFile

from src.constant import main
from src.provider import get_browser_manager, get_buzz_collector
from src.service import BrowserManager, BuzzCollector

buzz_picking_router = APIRouter()

@buzz_picking_router.post("/pick_all_buzz", tags=[main])
async def pick_all_buzz(
        session_urls: list[str] = Form(...),
        close_browser_when_finished: bool = True,
        browser_manager: BrowserManager = Depends(get_browser_manager),
        buzz_runner: BuzzCollector = Depends(get_buzz_collector)
    ):
    if len(session_urls) > 0:
        await browser_manager.open_browser(session_urls[0])
        await buzz_runner.collect_buzz_for_urls(session_urls)
        if close_browser_when_finished:
            await browser_manager.shutdown_if_possible()

@buzz_picking_router.post("/pick_all_buzz_from_file", tags=[main])
async def pick_all_buzz_from_file(
        session_urls_file: UploadFile = File(...),
        close_browser_when_finished: bool = True,
        browser_manager: BrowserManager = Depends(get_browser_manager),
        buzz_runner: BuzzCollector = Depends(get_buzz_collector)
    ):
    session_urls: list[str] = (await session_urls_file.read()).decode("utf-8").splitlines()
    session_urls.reverse()
    if len(session_urls) > 0:
        await browser_manager.open_browser(session_urls[0])
        await buzz_runner.collect_buzz_for_urls(session_urls)
        if close_browser_when_finished:
            await browser_manager.shutdown_if_possible()
