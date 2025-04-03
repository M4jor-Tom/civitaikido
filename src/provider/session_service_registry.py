from src.model.injection_extraction_state import InjectionExtractionState
from src.provider import SessionServiceContainer
import logging

logger = logging.getLogger(__name__)

def build_session(session_id: str) -> SessionServiceContainer:
    container = SessionServiceContainer(session_id)
    logger.info(f"Built container for session_id: {session_id}")
    container.init()
    return container

class SessionServiceRegistry:
    def __init__(self):
        self.sessions: dict[str, SessionServiceContainer] = {}

    def get_or_create(self, session_id: str) -> SessionServiceContainer:
        if session_id not in self.sessions:
            self.sessions[session_id] = build_session(session_id)
        elif self.sessions[session_id].state_manager.injection_extraction_state == InjectionExtractionState.IMAGES_EXTRACTED:
            self.sessions[session_id].shutdown()
            self.sessions[session_id] = build_session(session_id)
        else:
            logger.info(f"Found container for session_id: {session_id}")
        return self.sessions[session_id]

    async def shutdown_all(self):
        for session in self.sessions.values():
            await session.shutdown()
