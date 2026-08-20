from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentVariables(BaseSettings):
    meta_verify_token: str
    meta_app_secret: str
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


env = EnvironmentVariables()

app = FastAPI()


@app.get("/status")
def get_status():
    return {"status": "ok"}
