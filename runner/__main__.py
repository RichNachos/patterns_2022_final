import uvicorn

from runner.setup import setup

if __name__ == "__main__":
    uvicorn.run(setup(), host="0.0.0.0", port=8000)
