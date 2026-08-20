from datetime import UTC, datetime
from typing import Annotated

import psycopg
from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import PlainTextResponse

from main import env

router = APIRouter(tags=["whatsapp"])


@router.get("/webhook/whatsapp")
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


@router.post("/webhook/whatsapp")
async def recieve_response(request: Request):
    payload = await request.json()

    value = payload["entry"][0]["changes"][0]["value"]
    messages = value.get("messages")

    if not messages:
        return

    message = messages[0]

    whatsapp_message_id = message["id"]
    sender = message["from"]
    message_type = message["type"]
    content = message.get("text", {}).get("body")
    sent_at = datetime.fromtimestamp(int(message["timestamp"]), tz=UTC)

    async with await psycopg.AsyncConnection.connect(
        dbname=env.postgres_db,
        user=env.postgres_user,
        password=env.postgres_password,
        host=env.postgres_host,
        port=env.postgres_port,
    ) as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO messages (
                    whatsapp_message_id,
                    sender,
                    message_type,
                    content,
                    sent_at
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (whatsapp_message_id) DO NOTHING
                """,
                (
                    whatsapp_message_id,
                    sender,
                    message_type,
                    content,
                    sent_at,
                ),
            )

    print(payload, flush=True)
    return
