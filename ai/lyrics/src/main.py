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


async def lyrics_cmd(self):
    """Search song lyrics — usage: .lyrics <song> or .lyrics <artist> - <song>"""
    message = self.message
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.edit(
            "❌ <b>Usage:</b>\n"
            "  <code>.lyrics <song name></code>\n"
            "  <code>.lyrics <artist> - <song></code>\n\n"
            "📝 <b>Example:</b> <code>.lyrics Bohemian Rhapsody</code>"
        )

    query = args[1].strip()
    await message.edit(f"🎤 Searching lyrics for <b>{query}</b>...")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.lyrics.ovh/v1/search",
            params={"q": query},
        ) as resp:
            if resp.status != 200:
                async with session.get(
                    f"https://api.lyrics.ovh/v1/search/{query}"
                ) as resp2:
                    if resp2.status != 200:
                        return await message.edit("❌ Search failed")
                    data = await resp2.json()
            else:
                data = await resp.json()

    songs = data if isinstance(data, list) else data.get("data", [])
    if not songs:
        artist, song = query.split(
            " - ", 1) if " - " in query else (None, query)
        return await _fetch_lyrics_direct(message, artist or "", song, self.client)

    via = self.client.inline.viamanager
    text = f"🎤 <b>Lyrics Search:</b> <code>{query}</code>\n━━━━━━━━━━━━━━━\n\nSelect a song:"
    buttons = []
    for i, song in enumerate(songs[:5], 1):
        title = song.get("title", song.get("name", "Unknown"))
        artist = (song.get("artist", {}) if isinstance(song.get("artist"), dict)
                  else song).get("name", "Unknown")
        buttons.append([{
            "text": f"{i}. {title} — {artist}",
            "callback": _show_lyrics,
            "params": {
                "artist": artist, "song": title,
                "chat_id": message.chat.id,
            },
        }])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await message.delete()
    await self.client.inline.say(
        self.client, message, text,
        prefix="lyrics_", buttons=buttons, chat_id=message.chat.id,
    )


async def _fetch_lyrics_direct(message, artist, song, client):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.lyrics.ovh/v1/{artist}/{song}"
        ) as resp:
            if resp.status != 200:
                return await message.edit(
                    f"❌ No lyrics found for <b>{song}</b>"
                )
            data = await resp.json()

    lyrics = data.get("lyrics", "No lyrics found.")
    if len(lyrics) > 3500:
        lyrics = lyrics[:3497] + "..."

    text = (
        f"🎤 <b>{song}</b>\n"
        + (f"👤 <b>Artist:</b> <code>{artist}</code>\n" if artist else "")
        + f"━━━━━━━━━━━━━━━\n\n{lyrics}"
    )

    via = client.inline.viamanager
    buttons = [[{"text": "🗑 Close", "callback": _close}]]

    await message.delete()
    await client.inline.say(
        client, message, text,
        prefix="lyrics_", buttons=buttons, chat_id=message.chat.id,
    )


async def _show_lyrics(call, artist: str, song: str, chat_id: int):
    await call.answer("Loading lyrics...")
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.lyrics.ovh/v1/{artist}/{song}"
        ) as resp:
            if resp.status != 200:
                return await call.edit_message(
                    f"❌ No lyrics found for <b>{song}</b>"
                )
            data = await resp.json()

    lyrics = data.get("lyrics", "No lyrics found.")
    if len(lyrics) > 3500:
        lyrics = lyrics[:3497] + "..."

    text = (
        f"🎤 <b>{song}</b>\n"
        f"👤 <b>Artist:</b> <code>{artist}</code>\n"
        f"━━━━━━━━━━━━━━━\n\n{lyrics}"
    )

    via = call.client.inline.viamanager
    buttons = [[{"text": "🗑 Close", "callback": _close}]]
    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _close(call):
    await call.edit_message("🗑 Closed")
