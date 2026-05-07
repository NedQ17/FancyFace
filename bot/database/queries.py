from __future__ import annotations

import asyncpg
from datetime import datetime
from bot.database.pool import get_pool


# ─── Users ────────────────────────────────────────────────────────────────────

async def get_or_create_user(
    user_id: int,
    username: str | None,
    first_name: str,
    referrer_id: int | None = None,
) -> dict:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
        if row:
            await conn.execute(
                "UPDATE users SET username=$2, first_name=$3 WHERE user_id=$1",
                user_id, username, first_name or "",
            )
            return dict(row)
        row = await conn.fetchrow(
            """
            INSERT INTO users (user_id, username, first_name, referrer_id)
            VALUES ($1, $2, $3, $4)
            RETURNING *
            """,
            user_id, username, first_name or "", referrer_id,
        )
        return dict(row)


async def get_user(user_id: int) -> dict | None:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
        return dict(row) if row else None


async def get_total_credits(user: dict) -> int:
    return (user.get("paid_credits") or 0) + (user.get("free_credits") or 0)


async def consume_credit(user_id: int) -> str:
    """Deducts one credit. Returns 'paid' or 'free'. Raises ValueError if none."""
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                "SELECT paid_credits, free_credits FROM users WHERE user_id=$1 FOR UPDATE",
                user_id,
            )
            if row["paid_credits"] >= 1:
                await conn.execute(
                    "UPDATE users SET paid_credits = paid_credits - 1 WHERE user_id=$1",
                    user_id,
                )
                return "paid"
            if row["free_credits"] >= 1:
                await conn.execute(
                    "UPDATE users SET free_credits = free_credits - 1 WHERE user_id=$1",
                    user_id,
                )
                return "free"
            raise ValueError("insufficient_credits")


async def refund_credit(user_id: int, credit_type: str) -> None:
    pool = get_pool()
    async with pool.acquire() as conn:
        if credit_type == "paid":
            await conn.execute(
                "UPDATE users SET paid_credits = paid_credits + 1 WHERE user_id=$1", user_id
            )
        else:
            await conn.execute(
                "UPDATE users SET free_credits = free_credits + 1 WHERE user_id=$1", user_id
            )


async def add_credits(user_id: int, paid: int = 0, free: int = 0) -> None:
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """UPDATE users
               SET paid_credits = paid_credits + $2,
                   free_credits = free_credits + $3
               WHERE user_id=$1""",
            user_id, paid, free,
        )


async def set_channel_subscribed(user_id: int) -> None:
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET channel_subscribed=TRUE WHERE user_id=$1", user_id
        )


async def claim_subscription_bonus(user_id: int) -> bool:
    """Atomically marks bonus as claimed. Returns True if this was the first claim."""
    pool = get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            """UPDATE users SET subscription_bonus_claimed=TRUE
               WHERE user_id=$1 AND subscription_bonus_claimed=FALSE""",
            user_id,
        )
        return result == "UPDATE 1"


async def set_channel_unsubscribed(user_id: int) -> None:
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET channel_subscribed=FALSE WHERE user_id=$1", user_id
        )


async def mark_paywall_shown(user_id: int) -> None:
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """UPDATE users SET paywall_shown_at=NOW(), paywall_reminder_sent=FALSE
               WHERE user_id=$1 AND paywall_shown_at IS NULL""",
            user_id,
        )


async def mark_paywall_reminder_sent(user_id: int) -> None:
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET paywall_reminder_sent=TRUE WHERE user_id=$1", user_id
        )


async def get_pending_paywall_reminders() -> list[int]:
    """Users shown paywall >24h ago, not paid, reminder not yet sent."""
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT user_id FROM users
               WHERE paywall_shown_at IS NOT NULL
                 AND paywall_shown_at < NOW() - INTERVAL '24 hours'
                 AND paywall_reminder_sent = FALSE
                 AND paid_credits = 0
                 AND is_blocked = FALSE"""
        )
        return [r["user_id"] for r in rows]


async def block_user(user_id: int) -> None:
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET is_blocked=TRUE WHERE user_id=$1", user_id)


async def unblock_user(user_id: int) -> None:
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET is_blocked=FALSE WHERE user_id=$1", user_id)


async def get_all_active_user_ids() -> list[int]:
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT user_id FROM users WHERE is_blocked=FALSE"
        )
        return [r["user_id"] for r in rows]


async def get_sales_stats(from_dt: datetime, to_dt: datetime) -> dict:
    pool = get_pool()
    async with pool.acquire() as conn:
        summary = await conn.fetchrow(
            """SELECT
                COUNT(*) AS total_count,
                COALESCE(SUM(amount_kopecks) / 100, 0) AS total_rub
               FROM payments
               WHERE status = 'completed'
                 AND created_at >= $1
                 AND created_at < $2""",
            from_dt, to_dt,
        )
        breakdown = await conn.fetch(
            """SELECT
                package_id,
                COUNT(*) AS count,
                COALESCE(SUM(amount_kopecks) / 100, 0) AS total_rub
               FROM payments
               WHERE status = 'completed'
                 AND created_at >= $1
                 AND created_at < $2
               GROUP BY package_id
               ORDER BY total_rub DESC""",
            from_dt, to_dt,
        )
    return {
        "total_count": summary["total_count"],
        "total_rub":   summary["total_rub"],
        "breakdown":   [dict(r) for r in breakdown],
    }


async def get_admin_stats() -> dict:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """SELECT
                (SELECT COUNT(*) FROM users) AS total_users,
                (SELECT COUNT(*) FROM users WHERE created_at >= NOW() - INTERVAL '1 day') AS new_today,
                (SELECT COUNT(*) FROM users WHERE created_at >= NOW() - INTERVAL '7 days') AS new_week,
                (SELECT COUNT(*) FROM users WHERE created_at >= NOW() - INTERVAL '30 days') AS new_month,
                (SELECT COUNT(*) FROM generations WHERE status='completed' AND created_at >= NOW() - INTERVAL '1 day') AS gen_today,
                (SELECT COUNT(*) FROM generations WHERE status='completed' AND created_at >= NOW() - INTERVAL '7 days') AS gen_week,
                (SELECT COUNT(*) FROM generations WHERE status='completed' AND created_at >= NOW() - INTERVAL '30 days') AS gen_month,
                (SELECT COALESCE(SUM(amount_kopecks)/100, 0) FROM payments WHERE status='completed' AND created_at >= NOW() - INTERVAL '1 day') AS rev_today,
                (SELECT COALESCE(SUM(amount_kopecks)/100, 0) FROM payments WHERE status='completed' AND created_at >= NOW() - INTERVAL '7 days') AS rev_week,
                (SELECT COALESCE(SUM(amount_kopecks)/100, 0) FROM payments WHERE status='completed' AND created_at >= NOW() - INTERVAL '30 days') AS rev_month
            """
        )
        return dict(row)


# ─── Styles ───────────────────────────────────────────────────────────────────

async def get_styles(active_only: bool = True) -> list[dict]:
    pool = get_pool()
    async with pool.acquire() as conn:
        q = "SELECT * FROM styles"
        if active_only:
            q += " WHERE is_active=TRUE"
        q += " ORDER BY sort_order, id"
        rows = await conn.fetch(q)
        return [dict(r) for r in rows]


async def get_style(style_id: int) -> dict | None:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM styles WHERE id=$1", style_id)
        return dict(row) if row else None


async def add_style(name: str, emoji: str, prompt: str) -> int:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO styles (name, emoji, prompt) VALUES ($1, $2, $3) RETURNING id",
            name, emoji, prompt,
        )
        return row["id"]


async def update_style_name(style_id: int, name: str) -> None:
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE styles SET name=$2 WHERE id=$1", style_id, name)


async def update_style_emoji(style_id: int, emoji: str) -> None:
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE styles SET emoji=$2 WHERE id=$1", style_id, emoji)


async def update_style_prompt(style_id: int, prompt: str) -> None:
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE styles SET prompt=$2 WHERE id=$1", style_id, prompt)


async def delete_style(style_id: int) -> None:
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM styles WHERE id=$1", style_id)


async def ensure_default_styles(default_styles: list[dict]) -> None:
    pool = get_pool()
    async with pool.acquire() as conn:
        existing = {r["name"] for r in await conn.fetch("SELECT name FROM styles")}
        for s in default_styles:
            if s["name"] not in existing:
                await conn.execute(
                    "INSERT INTO styles (name, emoji, prompt, scenes, sort_order) VALUES ($1, $2, $3, $4, $5)",
                    s["name"], s["emoji"], s["prompt"], s.get("scenes", []), s["sort_order"],
                )


# ─── Photo Sessions ───────────────────────────────────────────────────────────

async def get_sessions(active_only: bool = True) -> list[dict]:
    pool = get_pool()
    async with pool.acquire() as conn:
        q = "SELECT * FROM photo_sessions"
        if active_only:
            q += " WHERE is_active=TRUE"
        q += " ORDER BY id"
        rows = await conn.fetch(q)
        return [dict(r) for r in rows]


async def get_session(session_id: int) -> dict | None:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM photo_sessions WHERE id=$1", session_id
        )
        return dict(row) if row else None


async def add_session(
    name: str, description: str, photo_count: int, prompts: list[str]
) -> int:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO photo_sessions (name, description, photo_count, prompts)
               VALUES ($1, $2, $3, $4) RETURNING id""",
            name, description, photo_count, prompts,
        )
        return row["id"]


async def ensure_default_sessions(default_sessions: list[dict]) -> None:
    pool = get_pool()
    async with pool.acquire() as conn:
        count = await conn.fetchval("SELECT COUNT(*) FROM photo_sessions")
        if count == 0:
            await conn.executemany(
                """INSERT INTO photo_sessions (name, description, photo_count, prompts)
                   VALUES ($1, $2, $3, $4)""",
                [
                    (s["name"], s["description"], s["photo_count"], s["prompts"])
                    for s in default_sessions
                ],
            )


# ─── Generations ──────────────────────────────────────────────────────────────

async def create_generation(
    user_id: int,
    gen_type: str,
    prompt: str,
    style_id: int | None = None,
    session_id: int | None = None,
) -> int:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO generations
               (user_id, gen_type, prompt, style_id, session_id)
               VALUES ($1, $2, $3, $4, $5)
               RETURNING id""",
            user_id, gen_type, prompt, style_id, session_id,
        )
        return row["id"]


async def complete_generation(
    gen_id: int, result_file_ids: list[str], was_free: bool
) -> None:
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """UPDATE generations
               SET status='completed', result_file_ids=$2, was_free=$3
               WHERE id=$1""",
            gen_id, result_file_ids, was_free,
        )
        user_id = await conn.fetchval(
            "SELECT user_id FROM generations WHERE id=$1", gen_id
        )
        await conn.execute(
            "UPDATE users SET total_generated = total_generated + $2 WHERE user_id=$1",
            user_id, len(result_file_ids),
        )


async def fail_generation(gen_id: int) -> None:
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE generations SET status='failed' WHERE id=$1", gen_id
        )


# ─── Payments ─────────────────────────────────────────────────────────────────

async def create_payment(
    user_id: int, package_id: str, credits: int, amount_kopecks: int
) -> int:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO payments (user_id, package_id, credits, amount_kopecks)
               VALUES ($1, $2, $3, $4) RETURNING id""",
            user_id, package_id, credits, amount_kopecks,
        )
        return row["id"]


async def complete_payment(payment_id: int, telegram_payment_id: str) -> int:
    """Marks payment complete and returns credited amount."""
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                """UPDATE payments SET status='completed', telegram_payment_id=$2
                   WHERE id=$1 RETURNING credits, user_id""",
                payment_id, telegram_payment_id,
            )
            await conn.execute(
                "UPDATE users SET paid_credits = paid_credits + $2 WHERE user_id=$1",
                row["user_id"], row["credits"],
            )
            return row["credits"]


# ─── Pending Unlocks ──────────────────────────────────────────────────────────

async def get_expired_unlocks() -> list[dict]:
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT user_id, file_id FROM pending_unlocks WHERE created_at < NOW() - INTERVAL '24 hours'"
        )
        return [dict(r) for r in rows]


async def save_pending_unlock(user_id: int, file_id: str) -> None:
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO pending_unlocks (user_id, file_id)
               VALUES ($1, $2)
               ON CONFLICT (user_id) DO UPDATE SET file_id = $2, created_at = NOW()""",
            user_id, file_id,
        )


async def get_pending_unlock(user_id: int) -> str | None:
    pool = get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT file_id FROM pending_unlocks WHERE user_id = $1", user_id
        )


async def delete_pending_unlock(user_id: int) -> None:
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM pending_unlocks WHERE user_id = $1", user_id
        )


# ─── Referrals ────────────────────────────────────────────────────────────────

async def record_referral(referrer_id: int, referred_id: int) -> bool:
    """Returns True if the referral was newly recorded (not duplicate)."""
    pool = get_pool()
    async with pool.acquire() as conn:
        try:
            await conn.execute(
                "INSERT INTO referrals (referrer_id, referred_id) VALUES ($1, $2)",
                referrer_id, referred_id,
            )
            return True
        except asyncpg.UniqueViolationError:
            return False


async def get_referral_count(user_id: int) -> int:
    pool = get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT COUNT(*) FROM referrals WHERE referrer_id=$1", user_id
        )
