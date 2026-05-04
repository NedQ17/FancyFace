"""AI image generation via fal.ai FLUX Kontext Pro."""
from __future__ import annotations

import asyncio
import os
import random
import fal_client
import httpx

from bot.config import FAL_KEY

os.environ["FAL_KEY"] = FAL_KEY

FAL_MODEL = "fal-ai/nano-banana-2/edit"


class GenerationError(Exception):
    pass


def _upload_sync(data: bytes, content_type: str = "image/jpeg") -> str:
    return fal_client.upload(data, content_type)


def _build_prompt(prompt: str, scenes: list[str]) -> str:
    scene = random.choice(scenes)
    return (
        f"Generate a photorealistic portrait photo of the person from the reference image. "
        f"{scene}. {prompt}. Preserve the person's exact facial features, face shape, and identity."
    )


def _run_sync(prompt: str, face_url: str, scenes: list[str]) -> dict:
    return fal_client.run(
        FAL_MODEL,
        arguments={
            "image_urls": [face_url],
            "prompt": _build_prompt(prompt, scenes),
            "num_images": 1,
            "aspect_ratio": "3:4",
            "resolution": "1K",
            "output_format": "jpeg",
            "safety_tolerance": 5,
        },
    )


async def upload_photo(photo_bytes: bytes) -> str:
    loop = asyncio.get_running_loop()
    try:
        return await asyncio.wait_for(
            loop.run_in_executor(None, lambda: _upload_sync(photo_bytes)),
            timeout=60.0,
        )
    except asyncio.TimeoutError:
        raise GenerationError("Превышено время загрузки фото")
    except Exception as e:
        raise GenerationError(f"Ошибка загрузки фото: {e}") from e


async def generate_portrait(face_url: str, prompt: str, scenes: list[str] | None = None) -> str:
    """Returns the image URL on the fal.ai CDN."""
    if not scenes:
        scenes = ["standing confidently, looking at camera"]
    loop = asyncio.get_running_loop()
    try:
        result = await asyncio.wait_for(
            loop.run_in_executor(None, lambda: _run_sync(prompt, face_url, scenes)),
            timeout=120.0,
        )
    except asyncio.TimeoutError:
        raise GenerationError("Превышено время ожидания генерации")
    except Exception as e:
        raise GenerationError(f"Ошибка генерации: {e}") from e

    try:
        return result["images"][0]["url"]
    except (KeyError, IndexError, TypeError) as e:
        raise GenerationError(f"Неожиданный ответ от сервиса генерации: {result}") from e


async def download_image(image_url: str) -> bytes:
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(image_url)
            response.raise_for_status()
            return response.content
    except httpx.HTTPError as e:
        raise GenerationError(f"Ошибка загрузки результата: {e}") from e
