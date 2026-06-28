import re

from aiogram import F, Router
from aiogram.types import Message

from handlers.music import handle_music_search
from handlers.video import handle_video_link

router = Router()

URL_RE = re.compile(r"https?://\S+")

VIDEO_DOMAINS = (
    "tiktok.com",
    "vm.tiktok.com",
    "instagram.com",
    "youtube.com",
    "youtu.be",
    "pinterest.com",
    "pin.it",
)


@router.message(F.text & ~F.text.startswith("/"))
async def handle_text(message: Message):
    text = message.text.strip()
    url_match = URL_RE.search(text)

    if url_match and any(domain in url_match.group(0) for domain in VIDEO_DOMAINS):
        await handle_video_link(message, url_match.group(0))
    else:
        await handle_music_search(message, text)
