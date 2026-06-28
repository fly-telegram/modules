#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

from uuid import uuid4
from typing import Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

API_BASE = "https://api.jikan.moe/v4"


async def _search_anime(query: str) -> Optional[list]:
    try:
        import aiohttp
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                f"{API_BASE}/anime", params={"q": query, "limit": 5}
            ) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                return data.get("data", [])
    except ImportError:
        return None


async def _search_manga(query: str) -> Optional[list]:
    try:
        import aiohttp
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                f"{API_BASE}/manga", params={"q": query, "limit": 5}
            ) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                return data.get("data", [])
    except ImportError:
        return None


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


# ─── Anime search ───


async def ani_cmd(self):
    """Search anime on MyAnimeList — usage: .ani <name>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.ani <anime name></code>\n\n"
            "📝 <b>Example:</b> <code>.ani Attack on Titan</code>"
        )
        return

    query = args[1].strip()
    await message.edit(f"🔍 Searching for <b>{query}</b>...")

    results = await _search_anime(query)
    if results is None:
        await message.edit("❌ <b>Search failed.</b> Make sure <code>aiohttp</code> is installed.")
        return

    if not results:
        await message.edit(f"❌ <b>No results for</b> <code>{query}</code>")
        return

    chat_id = message.chat.id
    await message.delete()

    via = self.client.inline.viamanager
    text = (
        f"📺 <b>Anime Search:</b> <code>{query}</code>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"Select a result:"
    )
    buttons = []
    for i, anime in enumerate(results[:5]):
        title = anime.get("title", "Unknown")
        year = (anime.get("year") or "?")
        typ = anime.get("type") or "?"
        buttons.append([{
            "text": f"{i + 1}. {title} ({typ}, {year})",
            "callback": _show_anime,
            "params": {"mal_id": anime["mal_id"], "chat_id": chat_id, "query": query},
        }])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await self.client.inline.say(
        self.client, message, text,
        prefix="ani_", buttons=buttons, chat_id=chat_id,
    )


async def _show_anime(call, mal_id: int, chat_id: int, query: str):
    await call.answer("Loading...")
    try:
        import aiohttp
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"{API_BASE}/anime/{mal_id}") as resp:
                if resp.status != 200:
                    await call.answer("❌ Failed to load details")
                    return
                data = await resp.json()
                anime = data.get("data", {})
    except ImportError:
        await call.answer("❌ aiohttp required")
        return

    title = anime.get("title", "Unknown")
    title_jp = anime.get("title_japanese", "")
    typ = anime.get("type") or "?"
    episodes = anime.get("episodes") or "?"
    status = anime.get("status") or "?"
    score = anime.get("score") or "?"
    rank = anime.get("rank") or "?"
    synopsis = anime.get("synopsis") or "No description."
    year = anime.get("year") or "?"
    season = anime.get("season") or ""
    url = anime.get("url") or ""
    genres = ", ".join(g["name"] for g in anime.get("genres", []))

    if len(synopsis) > 500:
        synopsis = synopsis[:497] + "..."

    jp_line = f"🇯🇵 <i>{title_jp}</i>\n" if title_jp else ""
    season_line = f"{season} " if season else ""
    genres_line = f"🏷️ <b>Genres:</b> <code>{genres}</code>\n" if genres else ""

    text = (
        f"📺 <b>{title}</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{jp_line}"
        f"━━━━━━━━━━━━━━━\n"
        f"📊 <b>Score:</b> <code>{score}</code>  |  <b>Rank:</b> <code>#{rank}</code>\n"
        f"📺 <b>Type:</b> <code>{typ}</code>  |  <b>Episodes:</b> <code>{episodes}</code>\n"
        f"📅 <b>{season_line}{year}</b>\n"
        f"📌 <b>Status:</b> <code>{status}</code>\n"
        f"{genres_line}"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{synopsis}"
    )

    via = call.client.inline.viamanager
    buttons = [
        [{"text": "🌐 MAL page", "url": url}] if url else [],
        [{"text": "⬅️ Back", "callback": _back_to_anime_results,
          "params": {"query": query, "chat_id": chat_id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]
    buttons = [b for b in buttons if b]

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _back_to_anime_results(call, query: str, chat_id: int):
    results = await _search_anime(query)
    if not results:
        await call.edit_message(f"❌ <b>No results for</b> <code>{query}</code>")
        return

    via = call.client.inline.viamanager
    text = (
        f"📺 <b>Anime Search:</b> <code>{query}</code>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"Select a result:"
    )
    buttons = []
    for i, anime in enumerate(results[:5]):
        title = anime.get("title", "Unknown")
        year = (anime.get("year") or "?")
        typ = anime.get("type") or "?"
        buttons.append([{
            "text": f"{i + 1}. {title} ({typ}, {year})",
            "callback": _show_anime,
            "params": {"mal_id": anime["mal_id"], "chat_id": chat_id, "query": query},
        }])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await call.edit_message(text, reply_markup=_kb(via, buttons))


# ─── Manga search ───


async def manga_cmd(self):
    """Search manga on MyAnimeList — usage: .manga <name>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.manga <manga name></code>\n\n"
            "📝 <b>Example:</b> <code>.manga One Piece</code>"
        )
        return

    query = args[1].strip()
    await message.edit(f"🔍 Searching for <b>{query}</b>...")

    results = await _search_manga(query)
    if results is None:
        await message.edit("❌ <b>Search failed.</b> Make sure <code>aiohttp</code> is installed.")
        return

    if not results:
        await message.edit(f"❌ <b>No results for</b> <code>{query}</code>")
        return

    chat_id = message.chat.id
    await message.delete()

    via = self.client.inline.viamanager
    text = (
        f"📖 <b>Manga Search:</b> <code>{query}</code>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"Select a result:"
    )
    buttons = []
    for i, manga in enumerate(results[:5]):
        title = manga.get("title", "Unknown")
        typ = manga.get("type") or "?"
        volumes = manga.get("volumes") or "?"
        chapters = manga.get("chapters") or "?"
        buttons.append([{
            "text": f"{i + 1}. {title} ({typ}, {chapters}ch)",
            "callback": _show_manga,
            "params": {"mal_id": manga["mal_id"], "chat_id": chat_id, "query": query},
        }])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await self.client.inline.say(
        self.client, message, text,
        prefix="manga_", buttons=buttons, chat_id=chat_id,
    )


async def _show_manga(call, mal_id: int, chat_id: int, query: str):
    await call.answer("Loading...")
    try:
        import aiohttp
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"{API_BASE}/manga/{mal_id}") as resp:
                if resp.status != 200:
                    await call.answer("❌ Failed to load details")
                    return
                data = await resp.json()
                manga = data.get("data", {})
    except ImportError:
        await call.answer("❌ aiohttp required")
        return

    title = manga.get("title", "Unknown")
    title_jp = manga.get("title_japanese", "")
    typ = manga.get("type") or "?"
    status = manga.get("status") or "?"
    score = manga.get("score") or "?"
    rank = manga.get("rank") or "?"
    synopsis = manga.get("synopsis") or "No description."
    chapters = manga.get("chapters") or "?"
    volumes = manga.get("volumes") or "?"
    url = manga.get("url") or ""
    genres = ", ".join(g["name"] for g in manga.get("genres", []))

    if len(synopsis) > 500:
        synopsis = synopsis[:497] + "..."

    jp_line = f"🇯🇵 <i>{title_jp}</i>\n" if title_jp else ""
    genres_line = f"🏷️ <b>Genres:</b> <code>{genres}</code>\n" if genres else ""

    text = (
        f"📖 <b>{title}</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{jp_line}"
        f"━━━━━━━━━━━━━━━\n"
        f"📊 <b>Score:</b> <code>{score}</code>  |  <b>Rank:</b> <code>#{rank}</code>\n"
        f"📖 <b>Type:</b> <code>{typ}</code>  |  📄 <b>Chapters:</b> <code>{chapters}</code>\n"
        f"📚 <b>Volumes:</b> <code>{volumes}</code>\n"
        f"📌 <b>Status:</b> <code>{status}</code>\n"
        f"{genres_line}"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{synopsis}"
    )

    via = call.client.inline.viamanager
    buttons = [
        [{"text": "🌐 MAL page", "url": url}] if url else [],
        [{"text": "⬅️ Back", "callback": _back_to_manga_results,
          "params": {"query": query, "chat_id": chat_id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]
    buttons = [b for b in buttons if b]

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _back_to_manga_results(call, query: str, chat_id: int):
    results = await _search_manga(query)
    if not results:
        await call.edit_message(f"❌ <b>No results for</b> <code>{query}</code>")
        return

    via = call.client.inline.viamanager
    text = (
        f"📖 <b>Manga Search:</b> <code>{query}</code>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"Select a result:"
    )
    buttons = []
    for i, manga in enumerate(results[:5]):
        title = manga.get("title", "Unknown")
        typ = manga.get("type") or "?"
        chapters = manga.get("chapters") or "?"
        buttons.append([{
            "text": f"{i + 1}. {title} ({typ}, {chapters}ch)",
            "callback": _show_manga,
            "params": {"mal_id": manga["mal_id"], "chat_id": chat_id, "query": query},
        }])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _close(call):
    await call.edit_message("🗑 Closed")
