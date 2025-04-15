from core.config import setup_logging, LOGGING_LEVEL, APP_HOST, APP_PORT

if __name__ == "__main__":
    import uvicorn
    setup_logging(LOGGING_LEVEL)
    uvicorn.run("core.civitaikido:app", host=APP_HOST, port=APP_PORT, reload=False)
