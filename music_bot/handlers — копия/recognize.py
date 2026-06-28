import os

from aiogram import F, Router
from aiogram.types import Message

from config import DOWNLOAD_DIR
from database import get_user_language
from handlers.music import handle_music_search
from locales import t
from utils.recognizer import recognize_from_file

router = Router()


@router.message(F.voice | F.audio | F.video_note)
async def handle_audio_recognition(message: Message):
    lang = await get_user_language(message.from_user.id)
    status_msg = await message.answer(t("recognizing", lang))

    file_obj = message.voice or message.audio or message.video_note
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{file_obj.file_unique_id}.ogg")

    tg_file = await message.bot.get_file(file_obj.file_id)
    await message.bot.download_file(tg_file.file_path, destination=file_path)

    result = await recognize_from_file(file_path)

    try:
        os.remove(file_path)
    except OSError:
        pass

    if not result or not result.get("title"):
        await status_msg.edit_text(t("recognize_failed", lang))
        return

    await status_msg.edit_text(
        t("recognized", lang, title=result["title"], artist=result["artist"])
    )
    query = f"{result['artist']} {result['title']}".strip()
    await handle_music_search(message, query)
