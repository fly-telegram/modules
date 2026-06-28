#     __ __     __  ___      _ ___
#    // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

from uuid import uuid4

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import aiohttp


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


async def yt_cmd(self):
    """Search YouTube videos — usage: .yt <query>"""
    message = self.message
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.edit(
            "❌ <b>Usage:</b> <code>.yt <search query></code>\n\n"
            "📝 <b>Example:</b> <code>.yt never gonna give you up</code>"
        )

    query = args[1].strip()
    await message.edit(f"🔍 Searching YouTube for <b>{query}</b>...")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "q": query,
                "maxResults": 5,
                "type": "video",
                "key": "AIzaSyCj0pDv7XEQlH6mDgZbGx7XkZ3n5vL8t9c",
            },
        ) as resp:
            if resp.status != 200:
                async with session.get(
                    "https://inv.nadeko.net/search",
                    params={"q": query},
                ) as resp2:
                    if resp2.status != 200:
                        return await message.edit("❌ Search failed")
                    html = await resp2.text()
                    import re
                    ids = re.findall(r'href="/watch\?v=([a-zA-Z0-9_-]{11})"', html)
                    titles = re.findall(r'title="([^"]+)"', html)
                    results = []
                    for vid, title in zip(ids[:5], titles[:5]):
                        results.append({"id": vid, "title": title})
            else:
                data = await resp.json()
                results = [
                    {"id": item["id"]["videoId"], "title": item["snippet"]["title"]}
                    for item in data.get("items", [])
                ]

    if not results:
        return await message.edit(f"❌ No results for <b>{query}</b>")

    via = message.client.inline.viamanager
    text = f"▶️ <b>YouTube Search:</b> <code>{query}</code>\n━━━━━━━━━━━━━━━\n\nSelect a video:"
    buttons = []
    for i, video in enumerate(results[:5], 1):
        vid = video["id"]
        title = video["title"]
        url = f"https://youtu.be/{vid}"
        buttons.append([{
            "text": f"{i}. {title}",
            "url": url,
        }])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await message.delete()
    await message.client.inline.say(
        message.client, message, text,
        prefix="yt_", buttons=buttons, chat_id=message.chat.id,
    )


async def _close(call):
    await call.edit_message("🗑 Closed")
