#     __ __     __  ___      _ ___
#    // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

from uuid import uuid4

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import aiohttp
import random

TYPES = ["any", "programming", "dark", "pun", "spooky", "christmas"]


def _kb(via, buttons):
    rows = []
    for row in buttons:
        line = []
        for b in row:
            cb = b.get("callback")
            params = b.get("params", {})
            if callable(cb):
                uid = str(uuid4())
                via.handlers[uid] = {"callback": cb, "params": params}
                line.append(InlineKeyboardButton(
                    text=b["text"], callback_data=uid))
            elif "url" in b:
                line.append(InlineKeyboardButton(text=b["text"], url=b["url"]))
        rows.append(line)
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def joke_cmd(self):
    """Get a random joke — usage: .joke [category]"""
    message = self.message
    args = message.text.split(maxsplit=1)
    category = args[1].strip().lower() if len(args) > 1 else None

    if category and category in TYPES:
        return await _fetch_joke(message, category)
    elif category:
        return await message.edit(
            f"❌ Unknown category: <b>{category}</b>\n"
            f"Available: {', '.join(TYPES)}"
        )

    return await _show_category_menu(message)


async def _show_category_menu(message):
    via = message.client.inline.viamanager
    text = "😂 <b>Joke Categories</b>\n━━━━━━━━━━━━━━━\n\nSelect a category:"
    buttons = []
    for cat in TYPES:
        buttons.append([{
            "text": f"🎭 {cat.capitalize()}",
            "callback": _fetch_joke_cb,
            "params": {"category": cat, "chat_id": message.chat.id},
        }])
    buttons.append([{"text": "🎲 Random", "callback": _random_joke,
                     "params": {"chat_id": message.chat.id}}])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await message.delete()
    await message.client.inline.say(
        message.client, message, text,
        prefix="joke_", buttons=buttons, chat_id=message.chat.id,
    )


async def _fetch_joke(message, category):
    await message.edit(f"😂 Fetching a <b>{category}</b> joke...")
    joke = await _get_joke(category)
    if not joke:
        return await message.edit("❌ Failed to fetch joke")

    text = _format_joke(joke, category)
    via = message.client.inline.viamanager
    buttons = [
        [{"text": "🔄 Another", "callback": _fetch_joke_cb,
          "params": {"category": category, "chat_id": message.chat.id}}],
        [{"text": "⬅️ Categories", "callback": _back_categories,
          "params": {"chat_id": message.chat.id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await message.delete()
    await message.client.inline.say(
        message.client, message, text,
        prefix="joke_", buttons=buttons, chat_id=message.chat.id,
    )


async def _fetch_joke_cb(call, category: str, chat_id: int):
    await call.answer("Loading...")
    joke = await _get_joke(category)
    if not joke:
        return await call.edit_message("❌ Failed to fetch joke")

    text = _format_joke(joke, category)
    via = call.client.inline.viamanager
    buttons = [
        [{"text": "🔄 Another", "callback": _fetch_joke_cb,
          "params": {"category": category, "chat_id": chat_id}}],
        [{"text": "⬅️ Categories", "callback": _back_categories,
          "params": {"chat_id": chat_id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _random_joke(call, chat_id: int):
    category = random.choice(TYPES)
    await call.answer(f"🎲 {category}")
    joke = await _get_joke(category)
    if not joke:
        return await call.edit_message("❌ Failed to fetch joke")

    text = _format_joke(joke, category)
    via = call.client.inline.viamanager
    buttons = [
        [{"text": "🔄 Another", "callback": _fetch_joke_cb,
          "params": {"category": category, "chat_id": chat_id}}],
        [{"text": "⬅️ Categories", "callback": _back_categories,
          "params": {"chat_id": chat_id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _get_joke(category):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://v2.jokeapi.dev/joke/{category}",
            params={"blacklistFlags": "nsfw,religious", "type": "twopart"},
        ) as resp:
            if resp.status != 200:
                return None
            return await resp.json()


def _format_joke(joke, category):
    setup = joke.get("setup", joke.get("joke", ""))
    delivery = joke.get("delivery", "")

    if delivery:
        return (
            f"😂 <b>Joke ({category})</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"{setup}\n\n"
            f"<tg-spoiler>{delivery}</tg-spoiler>"
        )
    return (
        f"😂 <b>Joke ({category})</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{setup}"
    )


async def _back_categories(call, chat_id: int):
    via = call.client.inline.viamanager
    text = "😂 <b>Joke Categories</b>\n━━━━━━━━━━━━━━━\n\nSelect a category:"
    buttons = []
    for cat in TYPES:
        buttons.append([{
            "text": f"🎭 {cat.capitalize()}",
            "callback": _fetch_joke_cb,
            "params": {"category": cat, "chat_id": chat_id},
        }])
    buttons.append([{"text": "🎲 Random", "callback": _random_joke,
                     "params": {"chat_id": chat_id}}])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _close(call):
    await call.edit_message("🗑 Closed")
