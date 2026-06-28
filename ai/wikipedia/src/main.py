#     __ __     __  ___      _ ___
#    // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

from uuid import uuid4

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import aiohttp

API_BASE = "https://en.wikipedia.org/api/rest_v1"


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


async def wiki_cmd(self):
    """Search Wikipedia — usage: .wiki <query>"""
    message = self.message
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.edit(
            "❌ <b>Usage:</b> <code>.wiki <search term></code>\n\n"
            "📝 <b>Example:</b> <code>.wiki Python programming</code>"
        )

    query = args[1].strip()
    await message.edit(f"🔍 Searching Wikipedia for <b>{query}</b>...")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{API_BASE}/search/title",
            params={"q": query, "limit": 5},
        ) as resp:
            if resp.status != 200:
                return await message.edit("❌ Search failed")
            data = await resp.json()

    pages = data.get("pages", [])
    if not pages:
        return await message.edit(
            f"❌ No Wikipedia articles found for <b>{query}</b>"
        )

    via = self.client.inline.viamanager
    text = f"📚 <b>Wikipedia:</b> <code>{query}</code>\n━━━━━━━━━━━━━━━\n\nSelect an article:"
    buttons = []
    for i, page in enumerate(pages[:5], 1):
        title = page.get("title", "Unknown")
        desc = page.get("description") or page.get("excerpt", "")
        if len(desc) > 80:
            desc = desc[:77] + "..."
        buttons.append([{
            "text": f"{i}. {title}",
            "callback": _show_article,
            "params": {"title": title, "chat_id": message.chat.id},
        }])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await message.delete()
    await self.client.inline.say(
        self.client, message, text,
        prefix="wiki_", buttons=buttons, chat_id=message.chat.id,
    )


async def _show_article(call, title: str, chat_id: int):
    await call.answer("Loading article...")
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{API_BASE}/page/summary/{title.replace(' ', '_')}"
        ) as resp:
            if resp.status != 200:
                return await call.edit_message(
                    f"❌ Article <b>{title}</b> not found"
                )
            data = await resp.json()

    page_title = data.get("title", title)
    extract = data.get("extract", "No content available.")
    url = data.get("content_urls", {}).get(
        "desktop", {}
    ).get("page", f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}")

    if len(extract) > 3500:
        extract = extract[:3497] + "..."

    text = (
        f"📖 <b>{page_title}</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{extract}"
    )

    via = call.client.inline.viamanager
    buttons = [
        [{"text": "🌐 Open in browser", "url": url}],
        [{"text": "⬅️ Back", "callback": _back_search,
          "params": {"query": page_title, "chat_id": chat_id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    thumbnail = data.get("thumbnail", {}).get("source", "")
    if thumbnail:
        await call.edit_message(text, reply_markup=_kb(via, buttons),
                                file=thumbnail, file_type="photo")
    else:
        await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _back_search(call, query: str, chat_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{API_BASE}/search/title",
            params={"q": query, "limit": 5},
        ) as resp:
            if resp.status != 200:
                return
            data = await resp.json()

    pages = data.get("pages", [])
    if not pages:
        return await call.edit_message(
            f"❌ No articles found for <b>{query}</b>"
        )

    via = call.client.inline.viamanager
    text = f"📚 <b>Wikipedia:</b> <code>{query}</code>\n━━━━━━━━━━━━━━━\n\nSelect an article:"
    buttons = []
    for i, page in enumerate(pages[:5], 1):
        title = page.get("title", "Unknown")
        buttons.append([{
            "text": f"{i}. {title}",
            "callback": _show_article,
            "params": {"title": title, "chat_id": chat_id},
        }])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _close(call):
    await call.edit_message("🗑 Closed")
