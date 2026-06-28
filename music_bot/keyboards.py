from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")],
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        ]
    )


def song_action_keyboard(song_hash: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔁 Yana yukla", callback_data=f"redownload_{song_hash}"),
                InlineKeyboardButton(text="➕ Pleylistga qo'sh", callback_data=f"addplaylist_{song_hash}"),
            ],
        ]
    )


def video_action_keyboard(video_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎵 Musiqasini yuklab olish / Ovozini ajratish", callback_data=f"extract_audio_{video_id}")],
        ]
    )


def quality_keyboard(song_hash: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="128 kbps", callback_data=f"q_128_{song_hash}"),
                InlineKeyboardButton(text="320 kbps", callback_data=f"q_320_{song_hash}"),
            ]
        ]
    )
