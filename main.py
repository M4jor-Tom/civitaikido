#!./python
from src.config import setup_logging

if __name__ == "__main__":
    import uvicorn
    setup_logging()
    uvicorn.run("src.civitaikido:app", host="127.0.0.1", port=8000, reload=False)
