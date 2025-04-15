import logging
from core.constant.logging_strips import DONE_PREFIX, WAIT_PREFIX, SKIP_PREFIX

logger = logging.getLogger(__name__)

async def try_action(action_name: str, callback):
    try:
        logger.debug(WAIT_PREFIX + action_name)
        await callback()
        logger.debug(DONE_PREFIX + action_name)
    except Exception as e:
        logger.warning(SKIP_PREFIX + action_name + ": " + str(e))

async def click_if_visible(action_name: str, locator):
    logger.debug(WAIT_PREFIX + "Locator for " + action_name)
    if await locator.is_visible():
        await locator.click()
        logger.debug(DONE_PREFIX + "Clicked locator for " + action_name)
    else:
        logger.warning(SKIP_PREFIX + "Locator for " + action_name + " not visible")
