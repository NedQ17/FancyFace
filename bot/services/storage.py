"""Supabase Storage helpers for temporary clean photo storage."""
import logging

import httpx

from bot.config import SUPABASE_URL, SUPABASE_SERVICE_KEY

logger = logging.getLogger(__name__)

BUCKET = "pending-unlocks"
_BASE = f"{SUPABASE_URL}/storage/v1/object"
_HEADERS = {
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "apikey": SUPABASE_SERVICE_KEY,
}


async def upload_clean_photo(user_id: int, image_bytes: bytes) -> str:
    path = f"{user_id}.jpg"
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(
            f"{_BASE}/{BUCKET}/{path}",
            content=image_bytes,
            headers={**_HEADERS, "Content-Type": "image/jpeg", "x-upsert": "true"},
        )
        r.raise_for_status()
    return path


async def download_clean_photo(path: str) -> bytes:
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(f"{_BASE}/{BUCKET}/{path}", headers=_HEADERS)
        r.raise_for_status()
        return r.content


async def delete_clean_photo(path: str) -> None:
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.request(
            "DELETE",
            f"{SUPABASE_URL}/storage/v1/object/{BUCKET}",
            json={"prefixes": [path]},
            headers={**_HEADERS, "Content-Type": "application/json"},
        )
        r.raise_for_status()
