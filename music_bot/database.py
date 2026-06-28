import time
from typing import Optional

import aiosqlite

from config import DB_PATH


async def init_db():
    """Bot ishga tushganda jadvallarni yaratadi (agar mavjud bo'lmasa)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                language TEXT DEFAULT 'uz',
                created_at INTEGER
            );

            CREATE TABLE IF NOT EXISTS song_cache (
                query_hash TEXT PRIMARY KEY,
                title TEXT,
                file_id TEXT,
                source TEXT,
                created_at INTEGER
            );

            CREATE TABLE IF NOT EXISTS song_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                query TEXT,
                title TEXT,
                created_at INTEGER
            );

            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                created_at INTEGER
            );

            CREATE TABLE IF NOT EXISTS playlist_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_id INTEGER,
                title TEXT,
                file_id TEXT,
                source TEXT
            );
            """
        )
        await db.commit()


# ---------- USERS ----------

async def create_user_if_not_exists(user_id: int, username: Optional[str]):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, created_at) VALUES (?, ?, ?)",
            (user_id, username, int(time.time())),
        )
        await db.commit()


async def get_user_language(user_id: int) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return row[0] if row and row[0] else "uz"


async def set_user_language(user_id: int, lang: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, user_id))
        await db.commit()


# ---------- SONG CACHE (tez-tez so'raladigan qo'shiqlarni qayta yuklamaslik uchun) ----------

async def get_cached_song(query_hash: str) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT title, file_id, source FROM song_cache WHERE query_hash = ?",
            (query_hash,),
        )
        row = await cursor.fetchone()
        if not row:
            return None
        return {"title": row[0], "file_id": row[1], "source": row[2]}


# addplaylist callback'ida ishlatiladi - nomi boshqacha bo'lsa-da, vazifasi bir xil
get_cached_song_by_hash = get_cached_song


async def cache_song(query_hash: str, title: str, file_id: str, source: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT OR REPLACE INTO song_cache (query_hash, title, file_id, source, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (query_hash, title, file_id, source, int(time.time())),
        )
        await db.commit()


async def search_cached_songs(query: str, limit: int = 10) -> list[dict]:
    """Inline qidiruv uchun - faqat avval keshga tushgan qo'shiqlar orasidan qidiradi."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT title, file_id FROM song_cache WHERE title LIKE ? LIMIT ?",
            (f"%{query}%", limit),
        )
        rows = await cursor.fetchall()
        return [{"title": r[0], "file_id": r[1]} for r in rows]


# ---------- TRENDING ----------

async def log_song_request(user_id: int, query: str, title: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO song_requests (user_id, query, title, created_at) VALUES (?, ?, ?, ?)",
            (user_id, query, title, int(time.time())),
        )
        await db.commit()


async def get_trending(period_seconds: int, limit: int = 10) -> list[dict]:
    since = int(time.time()) - period_seconds
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT title, COUNT(*) as cnt FROM song_requests
            WHERE created_at >= ?
            GROUP BY title
            ORDER BY cnt DESC
            LIMIT ?
            """,
            (since, limit),
        )
        rows = await cursor.fetchall()
        return [{"title": r[0], "count": r[1]} for r in rows]


# ---------- PLAYLISTS ----------

async def create_playlist(user_id: int, name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO playlists (user_id, name, created_at) VALUES (?, ?, ?)",
            (user_id, name, int(time.time())),
        )
        await db.commit()


async def get_user_playlists(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id, name FROM playlists WHERE user_id = ?", (user_id,))
        rows = await cursor.fetchall()
        return [{"id": r[0], "name": r[1]} for r in rows]


async def add_song_to_playlist(playlist_id: int, title: str, file_id: str, source: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO playlist_items (playlist_id, title, file_id, source) VALUES (?, ?, ?, ?)",
            (playlist_id, title, file_id, source),
        )
        await db.commit()


async def get_playlist_songs(playlist_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT title, file_id, source FROM playlist_items WHERE playlist_id = ?",
            (playlist_id,),
        )
        rows = await cursor.fetchall()
        return [{"title": r[0], "file_id": r[1], "source": r[2]} for r in rows]
