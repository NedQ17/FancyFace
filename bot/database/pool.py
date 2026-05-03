import asyncpg
from urllib.parse import urlparse

from bot.config import SUPABASE_DB_URL

_pool: asyncpg.Pool | None = None


async def init_pool() -> None:
    global _pool
    try:
        _pool = await asyncpg.create_pool(
            SUPABASE_DB_URL,
            min_size=1,
            max_size=5,
            ssl="require",
            statement_cache_size=0,  # required for Supabase Transaction pooler
        )
    except Exception as exc:
        parsed_url = urlparse(SUPABASE_DB_URL)
        host = parsed_url.hostname or SUPABASE_DB_URL
        raise RuntimeError(
            f"Failed to connect to database host {host!r}. "
            "Verify SUPABASE_DB_URL and network/DNS access."
        ) from exc


async def close_pool() -> None:
    if _pool:
        await _pool.close()


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Database pool is not initialized")
    return _pool
