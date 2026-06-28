import asyncio
import os

import yt_dlp

from config import MAX_VIDEO_HEIGHT


def _run_audio_search(opts: dict, query: str):
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(query, download=True)
        if "entries" in info:
            info = info["entries"][0]
        filename = ydl.prepare_filename(info)
        base, _ = os.path.splitext(filename)
        mp3_path = base + ".mp3"
        return mp3_path, info.get("title", query)


async def search_and_download_audio(query: str, out_dir: str, quality: str = "192") -> tuple[str, str]:
    """Qo'shiq nomi bo'yicha YouTube'dan qidirib, MP3 formatida yuklab oladi.

    Eslatma: agar boshqa manba (masalan SoundCloud) qo'shmoqchi bo'lsangiz,
    default_search'ni o'zgartirish o'rniga to'g'ridan-to'g'ri scsearch1: prefiksidan
    foydalanishingiz mumkin.
    """
    os.makedirs(out_dir, exist_ok=True)
    outtmpl = os.path.join(out_dir, "%(id)s.%(ext)s")
    opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch1",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": quality,
            }
        ],
    }
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _run_audio_search, opts, query)


def _run_video_download(opts: dict, url: str):
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        base, _ = os.path.splitext(filename)
        mp4_path = base + ".mp4"
        if not os.path.exists(mp4_path):
            mp4_path = filename
        return mp4_path, info.get("title", "video")


async def download_video(url: str, out_dir: str, max_height: int = MAX_VIDEO_HEIGHT) -> tuple[str, str]:
    """TikTok / Instagram / YouTube / Pinterest va boshqa yt-dlp qo'llab-quvvatlaydigan
    manbalardan videoni yuklab oladi (default: 720p gacha)."""
    os.makedirs(out_dir, exist_ok=True)
    outtmpl = os.path.join(out_dir, "%(id)s.%(ext)s")
    opts = {
        "format": f"bestvideo[height<={max_height}]+bestaudio/best[height<={max_height}]/best",
        "outtmpl": outtmpl,
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _run_video_download, opts, url)


async def extract_audio_from_file(video_path: str, out_dir: str) -> str:
    """Mahalliy diskdagi video fayldan ffmpeg yordamida audio ajratib oladi."""
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(video_path))[0]
    audio_path = os.path.join(out_dir, f"{base}_audio.mp3")

    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-acodec", "libmp3lame", "-q:a", "2",
        audio_path,
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
    )
    await proc.wait()

    if proc.returncode != 0 or not os.path.exists(audio_path):
        raise RuntimeError("ffmpeg orqali audio ajratib bo'lmadi")

    return audio_path
