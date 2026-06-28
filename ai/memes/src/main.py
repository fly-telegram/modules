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

SUBREDDITS = ["memes", "dankmemes", "wholesomememes", "me_irl", "ProgrammerHumor"]


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


async def meme_cmd(self):
    """Get a random meme — usage: .meme [subreddit]"""
    message = self.message
    args = message.text.split(maxsplit=1)
    subreddit = args[1].strip() if len(args) > 1 else None

    if subreddit:
        return await _fetch_meme(message, subreddit)
    return await _show_sub_menu(message)


async def _show_sub_menu(message):
    via = message.client.inline.viamanager
    text = "😂 <b>Meme Subreddits</b>\n━━━━━━━━━━━━━━━\n\nSelect a subreddit:"
    buttons = []
    for sub in SUBREDDITS:
        buttons.append([{
            "text": f"r/{sub}",
            "callback": _fetch_meme_sub,
            "params": {"subreddit": sub, "chat_id": message.chat.id},
        }])
    buttons.append([{"text": "🎲 Random", "callback": _random_meme,
                     "params": {"chat_id": message.chat.id}}])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await message.delete()
    await message.client.inline.say(
        message.client, message, text,
        prefix="meme_", buttons=buttons, chat_id=message.chat.id,
    )


async def _fetch_meme_sub(call, subreddit: str, chat_id: int):
    await call.answer(f"Fetching from r/{subreddit}...")
    await _fetch_and_show(call, subreddit, chat_id)


async def _random_meme(call, chat_id: int):
    subreddit = random.choice(SUBREDDITS)
    await call.answer(f"🎲 r/{subreddit}")
    await _fetch_and_show(call, subreddit, chat_id)


async def _fetch_meme(message, subreddit):
    await message.edit(f"😂 Fetching meme from <b>r/{subreddit}</b>...")
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://www.reddit.com/r/{subreddit}/hot.json",
            params={"limit": 50},
            headers={"User-Agent": "FlyTelegram/1.0"},
        ) as resp:
            if resp.status != 200:
                return await message.edit(
                    f"❌ Subreddit <b>r/{subreddit}</b> not found"
                )
            data = await resp.json()

    posts = data.get("data", {}).get("children", [])
    image_posts = _get_image_posts(posts)
    if not image_posts:
        return await message.edit(
            f"📭 No image memes in <b>r/{subreddit}</b>"
        )

    post = random.choice(image_posts)
    await _send_meme(message, post, subreddit)


async def _fetch_and_show(call, subreddit, chat_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://www.reddit.com/r/{subreddit}/hot.json",
            params={"limit": 50},
            headers={"User-Agent": "FlyTelegram/1.0"},
        ) as resp:
            if resp.status != 200:
                return await call.edit_message(
                    f"❌ Subreddit <b>r/{subreddit}</b> not found"
                )
            data = await resp.json()

    posts = data.get("data", {}).get("children", [])
    image_posts = _get_image_posts(posts)
    if not image_posts:
        return await call.edit_message(
            f"📭 No image memes in <b>r/{subreddit}</b>"
        )

    post = random.choice(image_posts)
    await _send_meme_inline(call, post, subreddit, chat_id)


def _get_image_posts(posts):
    return [
        p["data"] for p in posts
        if p["data"].get("url")
        and any(
            ext in p["data"]["url"].lower()
            for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]
        )
        and not p["data"].get("over_18", False)
    ]


async def _send_meme(message, post, subreddit):
    title = post.get("title", "No title")
    url = post.get("url", "")
    permalink = post.get("permalink", "")
    reddit_url = f"https://reddit.com{permalink}"
    author = post.get("author", "unknown")
    ups = post.get("ups", 0)

    text = (
        f"😂 <b>{title}</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>by</b> <code>u/{author}</code>  |  👍 <code>{ups}</code>\n"
        f"subreddit: r/{subreddit}"
    )

    via = message.client.inline.viamanager
    buttons = [
        [{"text": "🔗 View on Reddit", "url": reddit_url}],
        [{"text": "🔄 Next", "callback": _fetch_meme_sub,
          "params": {"subreddit": subreddit, "chat_id": message.chat.id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await message.delete()
    await message.client.inline.say(
        message.client, message, text,
        prefix="meme_", buttons=buttons, chat_id=message.chat.id,
        file=url, file_type="photo",
    )


async def _send_meme_inline(call, post, subreddit, chat_id):
    title = post.get("title", "No title")
    url = post.get("url", "")
    permalink = post.get("permalink", "")
    reddit_url = f"https://reddit.com{permalink}"
    author = post.get("author", "unknown")
    ups = post.get("ups", 0)

    text = (
        f"😂 <b>{title}</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>by</b> <code>u/{author}</code>  |  👍 <code>{ups}</code>\n"
        f"subreddit: r/{subreddit}"
    )

    via = call.client.inline.viamanager
    buttons = [
        [{"text": "🔗 View on Reddit", "url": reddit_url}],
        [{"text": "🔄 Next", "callback": _fetch_meme_sub,
          "params": {"subreddit": subreddit, "chat_id": chat_id}}],
        [{"text": "🎲 Random", "callback": _random_meme,
          "params": {"chat_id": chat_id}}],
        [{"text": "⬅️ Menu", "callback": _back_menu,
          "params": {"chat_id": chat_id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await call.edit_message(text, reply_markup=_kb(via, buttons),
                            file=url, file_type="photo")


async def _back_menu(call, chat_id: int):
    via = call.client.inline.viamanager
    text = "😂 <b>Meme Subreddits</b>\n━━━━━━━━━━━━━━━\n\nSelect a subreddit:"
    buttons = []
    for sub in SUBREDDITS:
        buttons.append([{
            "text": f"r/{sub}",
            "callback": _fetch_meme_sub,
            "params": {"subreddit": sub, "chat_id": chat_id},
        }])
    buttons.append([{"text": "🎲 Random", "callback": _random_meme,
                     "params": {"chat_id": chat_id}}])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _close(call):
    await call.edit_message("🗑 Closed")
