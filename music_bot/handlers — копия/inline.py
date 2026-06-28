import hashlib

from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultCachedAudio

from database import search_cached_songs

router = Router()


@router.inline_query()
async def inline_search(inline_query: InlineQuery):
    """ESLATMA: inline qidiruv faqat avval botda kamida bir marta so'ralib,
    keshga tushgan qo'shiqlar orasida ishlaydi - chunki Telegram inline
    natijalari darhol qaytishi kerak, real vaqtda yuklab bo'lmaydi."""
    query = inline_query.query.strip()
    if not query:
        return

    results = await search_cached_songs(query, limit=10)
    answers = [
        InlineQueryResultCachedAudio(
            id=hashlib.md5(f"{r['title']}_{i}".encode()).hexdigest(),
            audio_file_id=r["file_id"],
        )
        for i, r in enumerate(results)
        if r.get("file_id")
    ]
    await inline_query.answer(answers, cache_time=30)
