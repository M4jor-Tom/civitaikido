import logging

from core.config import session_id_var


class SessionIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.session_id = session_id_var.get()
        return True
