from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database import get_trending, get_user_language
from locales import t

router = Router()

DAY = 24 * 60 * 60
WEEK = 7 * DAY


@router.message(Command("top"))
async def show_top(message: Message):
    """/top - kunlik top
    /top week - haftalik top"""
    lang = await get_user_language(message.from_user.id)
    args = message.text.split()
    is_week = len(args) > 1 and args[1].lower() in ("week", "hafta", "неделя")

    period = WEEK if is_week else DAY
    period_label = t("this_week", lang) if is_week else t("today", lang)

    rows = await get_trending(period_seconds=period, limit=10)
    if not rows:
        await message.answer(t("no_trending", lang))
        return

    lines = [f"{i + 1}. {row['title']} — {row['count']}x" for i, row in enumerate(rows)]
    text = t("trending_title", lang, period=period_label) + "\n\n" + "\n".join(lines)
    await message.answer(text)
