import asyncio
import logging
import os
import shutil
import time

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web

from config import BOT_TOKEN, DOWNLOAD_DIR, PORT
from database import init_db
from handlers import inline, music, playlist, recognize, search, start, trending, video

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def clean_downloads_folder():
    """Bot ishga tushganda 'downloads' papkasini tozalaydi.
    Bu - oldingi sessiyadan qolib ketgan (masalan, bot kutilmaganda
    qulab tushib, 15 daqiqalik tozalash ishlamay qolgan) fayllarga
    qarshi qo'shimcha himoya. Disk hech qachon to'lib qolmasligini
    kafolatlaydi."""
    if os.path.exists(DOWNLOAD_DIR):
        shutil.rmtree(DOWNLOAD_DIR)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    logger.info("downloads/ papkasi tozalandi (xavfsiz boshlanish)")


async def health(request):
    """Render health-check va keep-alive ping uchun oddiy endpoint."""
    return web.Response(text="Bot ishlayapti ✅")


async def run_web_server():
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"Web-server {PORT}-portda ishga tushdi (keep-alive uchun)")


async def periodic_cleanup_loop():
    """Ikkilamchi himoya: har 30 daqiqada 'downloads' papkasini tekshirib,
    20 daqiqadan ko'p turgan har qanday faylni o'chiradi. Bu - har bir
    funksiya o'zining vazifasini to'g'ri bajarganiga qaramay, disk hech
    qachon to'lib qolmasligi uchun mustaqil ishlaydigan qo'shimcha qatlam."""
    STALE_AGE_SECONDS = 20 * 60
    while True:
        await asyncio.sleep(30 * 60)
        try:
            removed = 0
            for fname in os.listdir(DOWNLOAD_DIR):
                fpath = os.path.join(DOWNLOAD_DIR, fname)
                if not os.path.isfile(fpath):
                    continue
                age = time.time() - os.path.getmtime(fpath)
                if age > STALE_AGE_SECONDS:
                    os.remove(fpath)
                    removed += 1
            if removed:
                logger.info(f"Davriy tozalash: {removed} ta eski fayl o'chirildi")
        except Exception as e:
            logger.warning(f"Davriy tozalashda xato: {e}")


async def main():
    clean_downloads_folder()
    await init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Tartib muhim: oldin maxsus handlerlar (start, video callbacklar va h.k.),
    # eng oxirida umumiy matn handleri (search) bo'lishi kerak.
    dp.include_router(start.router)
    dp.include_router(recognize.router)
    dp.include_router(video.router)
    dp.include_router(music.router)
    dp.include_router(playlist.router)
    dp.include_router(trending.router)
    dp.include_router(inline.router)
    dp.include_router(search.router)

    await run_web_server()
    cleanup_task = asyncio.create_task(periodic_cleanup_loop())  # noqa: F841 - dasturning butun umri davomida ishlaydi

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot polling rejimida ishga tushdi")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
