from fastapi import FastAPI, Query, HTTPException, status
from fastapi.responses import PlainTextResponse
from typing import Annotated
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentVariables(BaseSettings):
    meta_verify_token: str
    meta_app_secret: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


env = EnvironmentVariables()

app = FastAPI()


@app.get("/status")
def get_status():
    return {"status": "ok"}


@app.get("/webhook/whatsapp")
def verify_whatsapp_webhook(
    mode: Annotated[str, Query(alias="hub.mode")],
    verify_token: Annotated[str, Query(alias="hub.verify_token")],
    challenge: Annotated[str, Query(alias="hub.challenge")],
):
    if verify_token == env.meta_verify_token and mode == "subscribe":
        return PlainTextResponse(status_code=200, content=challenge)
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Verification failed"
    )
