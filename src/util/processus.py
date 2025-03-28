from src.util import *

async def try_action(action_name: str, callback):
    try:
        log_wait(action_name)
        await callback()
        log_done(action_name)
    except Exception as e:
        log_skip(action_name + ": " + str(e))

async def click_if_visible(action_name: str, locator):
    if await locator.is_visible():
        await locator.click()
        log_done("Clicked locator for " + action_name)
    else:
        log_skip("Locator for " + action_name + " not visible")