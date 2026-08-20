from datetime import UTC, datetime
from typing import Annotated

import psycopg
from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import PlainTextResponse

from config import env

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
    contacts = value.get("contacts")

    if not messages:
        return

    message = messages[0]

    message_id = message["id"]
    contact_phone = message["from"]
    business_phone_number_id = value["metadata"]["phone_number_id"]
    contact_name = contacts[0].get("profile", {}).get("name") if contacts else None
    message_type = message["type"]
    content = message.get("text", {}).get("body")
    timestamp = datetime.fromtimestamp(int(message["timestamp"]), tz=UTC)

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
                    message_id,
                    contact_phone,
                    business_phone_number_id,
                    contact_name,
                    message_type,
                    content,
                    timestamp
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (message_id) DO NOTHING
                """,
                (
                    message_id,
                    contact_phone,
                    business_phone_number_id,
                    contact_name,
                    message_type,
                    content,
                    timestamp,
                ),
            )

    print(payload, flush=True)
    return
