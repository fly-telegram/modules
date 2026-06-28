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


async def music_cmd(self):
    """Search music, albums, or artists — usage: .music <query>"""
    message = self.message
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.edit(
            "❌ <b>Usage:</b> <code>.music <song/artist/album></code>\n\n"
            "📝 <b>Example:</b> <code>.music Bohemian Rhapsody</code>"
        )

    query = args[1].strip()
    await message.edit(f"🎵 Searching for <b>{query}</b>...")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.deezer.com/search",
            params={"q": query, "limit": 5},
        ) as resp:
            if resp.status != 200:
                return await message.edit("❌ Search failed")
            data = await resp.json()

    tracks = data.get("data", [])
    if not tracks:
        return await message.edit(f"❌ No results for <b>{query}</b>")

    via = message.client.inline.viamanager
    text = f"🎵 <b>Music Search:</b> <code>{query}</code>\n━━━━━━━━━━━━━━━\n\nSelect a track:"
    buttons = []
    for i, track in enumerate(tracks[:5], 1):
        title = track.get("title", "Unknown")
        artist = (track.get("artist") or {}).get("name", "Unknown")
        buttons.append([{
            "text": f"{i}. {title} — {artist}",
            "callback": _show_track,
            "params": {
                "track_id": track.get("id", 0),
                "chat_id": message.chat.id,
            },
        }])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await message.delete()
    await message.client.inline.say(
        message.client, message, text,
        prefix="music_", buttons=buttons, chat_id=message.chat.id,
    )


async def _show_track(call, track_id: int, chat_id: int):
    await call.answer("Loading...")
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.deezer.com/track/{track_id}"
        ) as resp:
            if resp.status != 200:
                return await call.answer("❌ Failed to load")
            data = await resp.json()

    title = data.get("title", "Unknown")
    artist = (data.get("artist") or {}).get("name", "Unknown")
    album = (data.get("album") or {}).get("title", "Unknown")
    duration = data.get("duration", 0)
    preview = data.get("preview", "")
    link = data.get("link", "")
    cover = (data.get("album") or {}).get("cover_medium", "")

    mins, secs = divmod(duration, 60)

    text = (
        f"🎵 <b>{title}</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>Artist:</b> <code>{artist}</code>\n"
        f"💿 <b>Album:</b> <code>{album}</code>\n"
        f"⏱ <b>Duration:</b> <code>{mins}:{secs:02d}</code>"
    )

    via = call.client.inline.viamanager
    buttons = []
    if preview:
        buttons.append([{"text": "🎧 Preview", "url": preview}])
    if link:
        buttons.append([{"text": "🔗 Open on Deezer", "url": link}])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    if cover:
        await call.edit_message(text, reply_markup=_kb(via, buttons),
                                file=cover, file_type="photo")
    else:
        await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _close(call):
    await call.edit_message("🗑 Closed")
