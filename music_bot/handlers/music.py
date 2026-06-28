import hashlib
import os

from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile, Message

import keyboards as kb
from config import DOWNLOAD_DIR
from database import (
    cache_song,
    get_cached_song,
    get_user_language,
    log_song_request,
)
from locales import t
from utils.downloader import search_and_download_audio

router = Router()


async def handle_music_search(message: Message, query: str):
    lang = await get_user_language(message.from_user.id)
    status_msg = await message.answer(t("searching", lang, query=query))

    query_hash = hashlib.md5(query.lower().strip().encode()).hexdigest()
    cached = await get_cached_song(query_hash)

    if cached:
        await message.answer_audio(
            cached["file_id"],
            caption=t("found_cached", lang, title=cached["title"]),
            reply_markup=kb.song_action_keyboard(query_hash),
        )
        await log_song_request(message.from_user.id, query, cached["title"])
        await status_msg.delete()
        return

    try:
        filepath, title = await search_and_download_audio(query, DOWNLOAD_DIR)
    except Exception:
        await status_msg.edit_text(t("not_found", lang))
        return

    audio = FSInputFile(filepath)
    sent = await message.answer_audio(
        audio,
        title=title,
        caption=t("here_is_song", lang, title=title),
        reply_markup=kb.song_action_keyboard(query_hash),
    )
    await cache_song(query_hash, title, sent.audio.file_id, "youtube")
    await log_song_request(message.from_user.id, query, title)

    try:
        os.remove(filepath)
    except OSError:
        pass

    await status_msg.delete()


@router.callback_query(F.data.startswith("redownload_"))
async def redownload_callback(call: CallbackQuery):
    lang = await get_user_language(call.from_user.id)
    query_hash = call.data.replace("redownload_", "")
    cached = await get_cached_song(query_hash)
    if not cached:
        await call.answer(t("song_not_found", lang), show_alert=True)
        return
    await call.message.answer_audio(
        cached["file_id"],
        caption=t("here_is_song", lang, title=cached["title"]),
        reply_markup=kb.song_action_keyboard(query_hash),
    )
    await call.answer()
