from typing import Optional

from shazamio import Shazam


async def recognize_from_file(file_path: str) -> Optional[dict]:
    """Audio/video fragmentdan qo'shiqni aniqlaydi (Shazam uslubida).

    Eslatma: shazamio kutubxonasining versiyalari orasida metod nomi
    o'zgargan (recognize_song -> recognize), shu sabab ikkisi ham tekshiriladi.
    Agar ishlamasa, muqobil sifatida AudD.io (https://audd.io) API'sidan
    foydalanish mumkin - u rasmiy, pullik/bepul limitli xizmat.
    """
    shazam = Shazam()
    try:
        if hasattr(shazam, "recognize"):
            result = await shazam.recognize(file_path)
        else:
            result = await shazam.recognize_song(file_path)
    except Exception:
        return None

    track = result.get("track") if result else None
    if not track:
        return None

    return {
        "title": track.get("title", "").strip(),
        "artist": track.get("subtitle", "").strip(),
    }
