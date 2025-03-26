#!./python

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.civitaikido:app", host="127.0.0.1", port=8000, reload=True)
