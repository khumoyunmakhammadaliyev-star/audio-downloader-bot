from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from database import (
    add_song_to_playlist,
    create_playlist,
    get_cached_song_by_hash,
    get_user_language,
    get_user_playlists,
)
from locales import t

router = Router()


@router.message(Command("playlists"))
async def show_playlists(message: Message):
    lang = await get_user_language(message.from_user.id)
    playlists = await get_user_playlists(message.from_user.id)
    if not playlists:
        await message.answer(t("no_playlists", lang))
        return
    text = t("your_playlists", lang) + "\n\n" + "\n".join(f"📁 {p['name']}" for p in playlists)
    await message.answer(text)


@router.message(Command("newplaylist"))
async def new_playlist(message: Message):
    lang = await get_user_language(message.from_user.id)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(t("playlist_name_prompt", lang))
        return
    name = args[1].strip()
    await create_playlist(message.from_user.id, name)
    await message.answer(t("playlist_created", lang, name=name))


@router.callback_query(F.data.startswith("addplaylist_"))
async def add_to_playlist_callback(call: CallbackQuery):
    """Soddalashtirilgan MVP: agar pleylist bo'lmasa avtomatik 'Sevimlilar'
    nomli pleylist yaratiladi va qo'shiq shu yerga qo'shiladi."""
    lang = await get_user_language(call.from_user.id)
    query_hash = call.data.replace("addplaylist_", "")
    song = await get_cached_song_by_hash(query_hash)
    if not song:
        await call.answer(t("song_not_found", lang), show_alert=True)
        return

    playlists = await get_user_playlists(call.from_user.id)
    if not playlists:
        await create_playlist(call.from_user.id, "Sevimlilar")
        playlists = await get_user_playlists(call.from_user.id)

    await add_song_to_playlist(playlists[0]["id"], song["title"], song["file_id"], song["source"])
    await call.answer(t("added_to_playlist", lang), show_alert=True)
