#!./python
from src.config import setup_logging, LOGGING_LEVEL, APP_PORT, PROFILE

if __name__ == "__main__":
    import uvicorn
    setup_logging(LOGGING_LEVEL)
    uvicorn.run("src.civitaikido:app", host="127.0.0.1", port=APP_PORT, reload=False)
