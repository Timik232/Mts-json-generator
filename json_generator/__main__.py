import uvicorn

if __name__ == "__main__":
    uvicorn.run("json_generator.server:app", host="0.0.0.0", port=8000)
