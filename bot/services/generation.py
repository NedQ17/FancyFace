"""AI image generation via fal.ai FLUX Kontext Pro."""
from __future__ import annotations

import asyncio
import os
import fal_client
import httpx

from bot.config import FAL_KEY

os.environ["FAL_KEY"] = FAL_KEY

FAL_MODEL = "fal-ai/flux-pro/kontext"


class GenerationError(Exception):
    pass


def _upload_sync(data: bytes, content_type: str = "image/jpeg") -> str:
    return fal_client.upload(data, content_type)


def _run_sync(prompt: str, face_url: str) -> dict:
    return fal_client.run(
        FAL_MODEL,
        arguments={
            "image_url": face_url,
            "prompt": f"{prompt}, high quality, photorealistic, detailed",
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
            "image_size": "portrait_4_3",
        },
    )


async def upload_photo(photo_bytes: bytes) -> str:
    loop = asyncio.get_event_loop()
    try:
        return await loop.run_in_executor(None, lambda: _upload_sync(photo_bytes))
    except Exception as e:
        raise GenerationError(f"Ошибка загрузки фото: {e}") from e


async def generate_portrait(face_url: str, prompt: str) -> bytes:
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(None, lambda: _run_sync(prompt, face_url))
    except Exception as e:
        raise GenerationError(f"Ошибка генерации: {e}") from e

    try:
        image_url: str = result["images"][0]["url"]
    except (KeyError, IndexError, TypeError) as e:
        raise GenerationError(f"Неожиданный ответ от сервиса генерации: {result}") from e

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(image_url)
            response.raise_for_status()
            return response.content
    except httpx.HTTPError as e:
        raise GenerationError(f"Ошибка загрузки результата: {e}") from e
