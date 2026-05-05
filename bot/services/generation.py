"""AI image generation via fal.ai FLUX Kontext Pro."""
from __future__ import annotations

import asyncio
import concurrent.futures
import os
import random
import fal_client
import httpx

from bot.config import FAL_KEY

os.environ["FAL_KEY"] = FAL_KEY

_executor = concurrent.futures.ThreadPoolExecutor(max_workers=200)

FAL_MODEL = "fal-ai/nano-banana-2/edit"

NEGATIVE_PROMPT = (
    "cartoon, illustration, anime, cgi, 3d render, ai generated look, plastic skin, oversmoothed skin, "
    "beauty filter, deformed face, bad anatomy, extra fingers, missing fingers, bad hands, uncanny eyes, "
    "duplicated features, unrealistic symmetry, wax skin, blurry, distorted proportions, low detail, "
    "overprocessed, fake smile, unrealistic teeth, doll face"
)


class GenerationError(Exception):
    pass


def _upload_sync(data: bytes, content_type: str = "image/jpeg") -> str:
    return fal_client.upload(data, content_type)


def _build_prompt(prompt: str, scenes: list[str]) -> str:
    if scenes:
        scene = random.choice(scenes)
        return f"{prompt}. Scene: {scene}."
    return prompt


def _run_sync(prompt: str, face_url: str, scenes: list[str]) -> dict:
    return fal_client.run(
        FAL_MODEL,
        arguments={
            "image_urls": [face_url],
            "prompt": _build_prompt(prompt, scenes),
            "negative_prompt": NEGATIVE_PROMPT,
            "num_images": 1,
            "aspect_ratio": "3:4",
            "resolution": "1K",
            "output_format": "jpeg",
            "safety_tolerance": 5,
        },
    )


async def upload_photo(photo_bytes: bytes) -> str:
    loop = asyncio.get_running_loop()
    last_exc: Exception | None = None
    for attempt in range(3):
        if attempt > 0:
            await asyncio.sleep(2 ** attempt)
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(_executor, lambda: _upload_sync(photo_bytes)),
                timeout=60.0,
            )
        except asyncio.TimeoutError:
            raise GenerationError("Превышено время загрузки фото")
        except Exception as e:
            last_exc = e
    raise GenerationError(f"Ошибка загрузки фото: {last_exc}") from last_exc


async def generate_portrait(face_url: str, prompt: str, scenes: list[str] | None = None) -> str:
    """Returns the image URL on the fal.ai CDN."""
    if not scenes:
        scenes = ["standing confidently, looking at camera"]
    loop = asyncio.get_running_loop()
    try:
        result = await asyncio.wait_for(
            loop.run_in_executor(_executor, lambda: _run_sync(prompt, face_url, scenes)),
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
