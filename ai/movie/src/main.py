#     __ __     __  ___      _ ___
#    // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

from uuid import uuid4

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loader import Loader, ConfigValue, ModuleConfig, validators

import aiohttp

loader = Loader()

config = ModuleConfig(
    ConfigValue(
        "omdb_api_key",
        "5a9e0a1c",
        "OMDB API key for movie/TV show search",
        validators.String(),
    )
)

API_BASE = "https://www.omdbapi.com"
API_KEY = config["omdb_api_key"]


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


async def movie_cmd(self):
    """Search movies and TV shows — usage: .movie <title>"""
    message = self.message
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.edit(
            "❌ <b>Usage:</b> <code>.movie <title></code>\n\n"
            "📝 <b>Example:</b> <code>.movie Inception</code>"
        )

    query = args[1].strip()
    await message.edit(f"🔍 Searching for <b>{query}</b>...")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            API_BASE,
            params={"apikey": API_KEY, "s": query, "type": "movie"},
        ) as resp:
            if resp.status != 200:
                return await message.edit("❌ API error")
            data = await resp.json()

    if data.get("Response") != "True":
        return await message.edit(f"❌ No results for <b>{query}</b>")

    results = data.get("Search", [])[:5]

    via = self.client.inline.viamanager
    text = f"🎬 <b>Movies:</b> <code>{query}</code>\n━━━━━━━━━━━━━━━\n\nSelect a movie:"
    buttons = []
    for i, m in enumerate(results, 1):
        title = m.get("Title", "Unknown")
        year = m.get("Year", "?")
        imdb_id = m.get("imdbID", "")
        buttons.append([{
            "text": f"{i}. {title} ({year})",
            "callback": _show_movie_detail,
            "params": {"imdb_id": imdb_id, "chat_id": message.chat.id},
        }])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await message.delete()
    await self.client.inline.say(
        self.client, message, text,
        prefix="movie_", buttons=buttons, chat_id=message.chat.id,
    )


async def _show_movie_detail(call, imdb_id: str, chat_id: int):
    await call.answer("Loading...")
    async with aiohttp.ClientSession() as session:
        async with session.get(
            API_BASE, params={"apikey": API_KEY, "i": imdb_id},
        ) as resp:
            if resp.status != 200:
                return await call.answer("❌ API error")
            data = await resp.json()

    if data.get("Response") != "True":
        return await call.edit_message("❌ Movie not found")

    title = data.get("Title", "Unknown")
    year = data.get("Year", "?")
    rated = data.get("Rated", "N/A")
    runtime = data.get("Runtime", "N/A")
    genre = data.get("Genre", "N/A")
    director = data.get("Director", "N/A")
    actors = data.get("Actors", "N/A")
    plot = data.get("Plot", "No description.")
    imdb_rating = data.get("imdbRating", "?")
    imdb_votes = data.get("imdbVotes", "?")
    metascore = data.get("Metascore", "N/A")
    poster = data.get("Poster", "")
    imdb_url = f"https://www.imdb.com/title/{imdb_id}"
    country = data.get("Country", "N/A")
    box_office = data.get("BoxOffice", "N/A")

    if len(plot) > 400:
        plot = plot[:397] + "..."

    stars = "⭐" * max(1, round(float(imdb_rating) / 2)) if imdb_rating != "N/A" else ""

    text = (
        f"🎬 <b>{title}</b> ({year})\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📖 <i>{plot}</i>\n\n"
        f"{stars} <b>IMDb:</b> <code>{imdb_rating}/10</code> "
        f"(<code>{imdb_votes}</code> votes)\n"
        f"📊 <b>Metascore:</b> <code>{metascore}</code>\n"
        f"🔞 <b>Rated:</b> <code>{rated}</code>\n"
        f"⏱ <b>Runtime:</b> <code>{runtime}</code>\n"
        f"🏷 <b>Genre:</b> <code>{genre}</code>\n"
        f"🎥 <b>Director:</b> <code>{director}</code>\n"
        f"👥 <b>Actors:</b> <code>{actors}</code>\n"
        f"🌍 <b>Country:</b> <code>{country}</code>\n"
        f"💵 <b>Box Office:</b> <code>{box_office}</code>"
    )

    via = call.client.inline.viamanager
    buttons = [
        [{"text": "🌐 View on IMDb", "url": imdb_url}] if imdb_url else [],
        [{"text": "⬅️ Back", "callback": _back_search,
          "params": {"query": title, "chat_id": chat_id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]
    buttons = [b for b in buttons if b]

    if poster and poster != "N/A":
        await call.edit_message(text, reply_markup=_kb(via, buttons),
                                file=poster, file_type="photo")
    else:
        await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _back_search(call, query: str, chat_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            API_BASE,
            params={"apikey": API_KEY, "s": query, "type": "movie"},
        ) as resp:
            if resp.status != 200:
                return
            data = await resp.json()

    if data.get("Response") != "True":
        return await call.edit_message(f"❌ No results for <b>{query}</b>")

    results = data.get("Search", [])[:5]
    via = call.client.inline.viamanager
    text = f"🎬 <b>Movies:</b> <code>{query}</code>\n━━━━━━━━━━━━━━━\n\nSelect a movie:"
    buttons = []
    for i, m in enumerate(results, 1):
        title = m.get("Title", "Unknown")
        year = m.get("Year", "?")
        imdb_id = m.get("imdbID", "")
        buttons.append([{
            "text": f"{i}. {title} ({year})",
            "callback": _show_movie_detail,
            "params": {"imdb_id": imdb_id, "chat_id": chat_id},
        }])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _close(call):
    await call.edit_message("🗑 Closed")
