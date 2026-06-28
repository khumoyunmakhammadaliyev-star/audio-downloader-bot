import asyncio
import os
import time

from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile, Message

import keyboards as kb
from config import DOWNLOAD_DIR
from database import get_user_language
from locales import t
from utils.downloader import download_video, extract_audio_from_file

router = Router()

# video_id -> mahalliy fayl yo'li.
# ESLATMA: bu RAM'da saqlanadi, bot qayta ishga tushganda tozalanadi.
# Productionda buni Redis yoki DB + TTL bilan almashtirish tavsiya etiladi.
VIDEO_FILE_CACHE: dict[str, str] = {}

# Render kabi bepul serverlarda disk joyi cheklangan, shu sabab yuklangan
# videoni cheksiz saqlamaymiz - "Ovozni ajratish" tugmasi uchun yetarli vaqt
# berib, keyin avtomatik o'chiramiz.
CLEANUP_DELAY_SECONDS = 15 * 60  # 15 daqiqa

# Python'da asyncio.create_task() natijasini hech yerda saqlamasangiz,
# vazifa tugamasdan turib "axlat yig'ish" (garbage collection) tomonidan
# kutilmaganda yo'qolib ketishi mumkin. Shu sabab har bir fon vazifasini
# shu to'plamda ushlab turamiz - bu tozalash 100% ishlashini kafolatlaydi.
_background_tasks: set[asyncio.Task] = set()


def _run_in_background(coro):
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    return task


async def _schedule_cleanup(video_id: str, filepath: str):
    await asyncio.sleep(CLEANUP_DELAY_SECONDS)
    VIDEO_FILE_CACHE.pop(video_id, None)
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except OSError:
        pass


async def handle_video_link(message: Message, url: str):
    lang = await get_user_language(message.from_user.id)
    status_msg = await message.answer(t("downloading_video", lang))

    try:
        filepath, title = await download_video(url, DOWNLOAD_DIR)
    except Exception:
        await status_msg.edit_text(t("video_download_failed", lang))
        return

    video_id = str(int(time.time() * 1000))
    VIDEO_FILE_CACHE[video_id] = filepath

    video_file = FSInputFile(filepath)
    await message.answer_video(
        video_file,
        caption=t("here_is_video", lang, title=title),
        reply_markup=kb.video_action_keyboard(video_id),
    )
    await status_msg.delete()

    _run_in_background(_schedule_cleanup(video_id, filepath))


@router.callback_query(F.data.startswith("extract_audio_"))
async def extract_audio_callback(call: CallbackQuery):
    lang = await get_user_language(call.from_user.id)
    video_id = call.data.replace("extract_audio_", "")
    filepath = VIDEO_FILE_CACHE.get(video_id)

    if not filepath or not os.path.exists(filepath):
        await call.answer(t("file_expired", lang), show_alert=True)
        return

    await call.answer(t("extracting_audio", lang))
    try:
        audio_path = await extract_audio_from_file(filepath, DOWNLOAD_DIR)
        await call.message.answer_audio(FSInputFile(audio_path))
        os.remove(audio_path)
    except Exception:
        await call.message.answer(t("extract_failed", lang))
