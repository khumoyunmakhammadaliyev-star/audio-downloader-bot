from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

import keyboards as kb
from database import create_user_if_not_exists, get_user_language, set_user_language
from locales import t

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await create_user_if_not_exists(message.from_user.id, message.from_user.username)
    await message.answer(t("choose_language"), reply_markup=kb.language_keyboard())


@router.message(Command("language"))
async def cmd_language(message: Message):
    await message.answer(t("choose_language"), reply_markup=kb.language_keyboard())


@router.callback_query(F.data.startswith("lang_"))
async def set_language(call: CallbackQuery):
    lang = call.data.split("_")[1]
    await set_user_language(call.from_user.id, lang)
    await call.message.edit_text(t("welcome", lang))
    await call.answer()
