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
        "newsapi_key",
        "6e4c7c2e1bcf4f2da1d780d5282b741d",
        "NewsAPI key for news headlines",
        validators.String(),
    )
)

API_KEY = config["newsapi_key"]
CATEGORIES = [
    "business", "entertainment", "general", "health",
    "science", "sports", "technology",
]
EMOJIS = {
    "business": "💼", "entertainment": "🎭", "general": "🌍",
    "health": "🏥", "science": "🔬", "sports": "🏆", "technology": "💻",
}


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


async def news_cmd(self):
    """Get latest news headlines — usage: .news [category]"""
    return await _show_category_menu(self.message, self.client)


async def _show_category_menu(message, client):
    via = client.inline.viamanager
    text = "📰 <b>News Categories</b>\n━━━━━━━━━━━━━━━\n\nSelect a category:"
    buttons = []
    for cat in CATEGORIES:
        emoji = EMOJIS.get(cat, "📰")
        buttons.append([{
            "text": f"{emoji} {cat.capitalize()}",
            "callback": _show_news,
            "params": {"category": cat, "chat_id": message.chat.id},
        }])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await message.delete()
    await client.inline.say(
        client, message, text,
        prefix="news_", buttons=buttons, chat_id=message.chat.id,
    )


async def _show_news(call, category: str, chat_id: int):
    await call.answer(f"Loading {category} news...")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://newsapi.org/v2/top-headlines",
            params={
                "category": category,
                "language": "en",
                "pageSize": 5,
                "apiKey": API_KEY,
            },
        ) as resp:
            if resp.status != 200:
                return await call.edit_message("❌ Failed to fetch news")
            data = await resp.json()

    articles = data.get("articles", [])
    if not articles:
        text = f"📭 No news in <b>{category}</b> right now"
    else:
        lines = []
        for i, article in enumerate(articles, 1):
            title = article.get("title", "No title")
            source = (article.get("source") or {}).get("name", "Unknown")
            lines.append(f"{i}. <b>{title}</b> — <code>{source}</code>")
        text = "\n\n".join(lines)

    emoji = EMOJIS.get(category, "📰")
    via = call.client.inline.viamanager
    buttons = []

    for i, article in enumerate(articles[:5], 1):
        url = article.get("url", "")
        if url:
            buttons.append([{
                "text": f"{i}. Read article",
                "url": url,
            }])

    buttons.append([{"text": "⬅️ Back to categories", "callback": _back_categories,
                     "params": {"chat_id": chat_id}}])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    header = f"{emoji} <b>{category.capitalize()} News</b>\n━━━━━━━━━━━━━━━\n\n"
    await call.edit_message(header + text, reply_markup=_kb(via, buttons))


async def _back_categories(call, chat_id: int):
    via = call.client.inline.viamanager
    text = "📰 <b>News Categories</b>\n━━━━━━━━━━━━━━━\n\nSelect a category:"
    buttons = []
    for cat in CATEGORIES:
        emoji = EMOJIS.get(cat, "📰")
        buttons.append([{
            "text": f"{emoji} {cat.capitalize()}",
            "callback": _show_news,
            "params": {"category": cat, "chat_id": chat_id},
        }])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _close(call):
    await call.edit_message("🗑 Closed")
