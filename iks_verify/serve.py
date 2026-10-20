import uvicorn

from iks_verify.runtime import configure_event_loop

if __name__ == "__main__":
    configure_event_loop()
    uvicorn.run("iks_verify.api.main:app", host="127.0.0.1", port=8000, reload=False)
