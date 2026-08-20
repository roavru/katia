from fastapi import FastAPI

from whatsapp import router as whatsapp_router

app = FastAPI()
app.include_router(whatsapp_router)


@app.get("/status")
def get_status():
    return {"status": "ok"}
