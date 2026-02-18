from __future__ import annotations

import uuid
import asyncpg
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS, DEFAULT_SUB_TEXT

pool: asyncpg.Pool | None = None


async def create_pool() -> None:
    global pool
    pool = await asyncpg.create_pool(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        min_size=2,
        max_size=10,
    )
    await _init_tables()


async def close_pool() -> None:
    if pool:
        await pool.close()


async def _init_tables() -> None:
    await pool.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id    BIGINT PRIMARY KEY,
            username   TEXT,
            lang_code  TEXT NOT NULL DEFAULT 'en',
            created_at TIMESTAMPTZ DEFAULT now()
        );

        CREATE TABLE IF NOT EXISTS chats (
            chat_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            invite_code TEXT UNIQUE NOT NULL,
            user1_id    BIGINT NOT NULL REFERENCES users(user_id),
            user2_id    BIGINT REFERENCES users(user_id),
            created_at  TIMESTAMPTZ DEFAULT now()
        );

        CREATE TABLE IF NOT EXISTS bot_settings (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_chats_user1  ON chats(user1_id);
        CREATE INDEX IF NOT EXISTS idx_chats_user2  ON chats(user2_id);
        CREATE INDEX IF NOT EXISTS idx_chats_invite ON chats(invite_code);
    """)

    # Инициализируем настройки по умолчанию если их нет
    await pool.execute("""
        INSERT INTO bot_settings (key, value) VALUES ('sub_text', $1)
        ON CONFLICT (key) DO NOTHING
    """, DEFAULT_SUB_TEXT)
    await pool.execute("""
        INSERT INTO bot_settings (key, value) VALUES ('sub_media', '')
        ON CONFLICT (key) DO NOTHING
    """)
    await pool.execute("""
        INSERT INTO bot_settings (key, value) VALUES ('sub_media_type', '')
        ON CONFLICT (key) DO NOTHING
    """)


# ───────── Bot Settings ─────────

async def get_setting(key: str) -> str:
    val = await pool.fetchval(
        "SELECT value FROM bot_settings WHERE key = $1", key,
    )
    return val or ""


async def set_setting(key: str, value: str) -> None:
    await pool.execute("""
        INSERT INTO bot_settings (key, value) VALUES ($1, $2)
        ON CONFLICT (key) DO UPDATE SET value = $2
    """, key, value)


# ───────── Users ─────────

async def upsert_user(user_id: int, username: str | None = None) -> None:
    await pool.execute("""
        INSERT INTO users (user_id, username)
        VALUES ($1, $2)
        ON CONFLICT (user_id) DO UPDATE SET username = COALESCE($2, users.username)
    """, user_id, username)


async def set_language(user_id: int, lang_code: str) -> None:
    await pool.execute(
        "UPDATE users SET lang_code = $1 WHERE user_id = $2",
        lang_code, user_id,
    )


async def get_language(user_id: int) -> str:
    row = await pool.fetchval(
        "SELECT lang_code FROM users WHERE user_id = $1", user_id,
    )
    return row or "en"


async def get_total_users() -> int:
    return await pool.fetchval("SELECT COUNT(*) FROM users")


async def get_active_chats() -> int:
    return await pool.fetchval(
        "SELECT COUNT(*) FROM chats WHERE user2_id IS NOT NULL"
    )


# ───────── Chats / Invites ─────────

async def create_invite(user_id: int) -> str:
    invite_code = uuid.uuid4().hex[:12]
    await pool.execute("""
        INSERT INTO chats (invite_code, user1_id)
        VALUES ($1, $2)
    """, invite_code, user_id)
    return invite_code


async def accept_invite(invite_code: str, user_id: int) -> dict | None:
    row = await pool.fetchrow("""
        UPDATE chats
        SET user2_id = $1
        WHERE invite_code = $2 AND user2_id IS NULL AND user1_id != $1
        RETURNING chat_id, user1_id, user2_id
    """, user_id, invite_code)
    return dict(row) if row else None


async def get_partner_id(user_id: int) -> int | None:
    row = await pool.fetchrow("""
        SELECT user1_id, user2_id FROM chats
        WHERE (user1_id = $1 OR user2_id = $1) AND user2_id IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 1
    """, user_id)
    if not row:
        return None
    return row["user2_id"] if row["user1_id"] == user_id else row["user1_id"]


async def delete_chat(user_id: int) -> int | None:
    partner_id = await get_partner_id(user_id)
    if partner_id:
        await pool.execute("""
            DELETE FROM chats
            WHERE (user1_id = $1 OR user2_id = $1)
              AND user2_id IS NOT NULL
        """, user_id)
    return partner_id
