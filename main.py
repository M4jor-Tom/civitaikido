#!./python
from core.config import setup_logging, LOGGING_LEVEL, APP_PORT

if __name__ == "__main__":
    import uvicorn
    setup_logging(LOGGING_LEVEL)
    uvicorn.run("core.civitaikido:app", host="127.0.0.1", port=APP_PORT, reload=False)
