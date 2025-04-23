import logging

class SafeFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        if not hasattr(record, 'session_id'):
            record.session_id = 'unknown'
        return super().format(record)
