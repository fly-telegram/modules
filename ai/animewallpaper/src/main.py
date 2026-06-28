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

TAGS = ["waifu", "neko", "shinobu", "megumin",
        "bully", "cuddle", "kiss", "hug"]


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


async def wallpaper_cmd(self):
    """Get random anime wallpaper — usage: .wallpaper [tag]"""
    message = self.message
    args = message.text.split(maxsplit=1)
    tag = args[1].strip() if len(args) > 1 else None

    if tag:
        return await _fetch_wallpaper(message, tag, self.client)
    return await _show_tag_menu(message, self.client)


async def _show_tag_menu(message, client):
    via = client.inline.viamanager
    text = "🖼️ <b>Anime Wallpapers</b>\n━━━━━━━━━━━━━━━\n\nSelect a tag:"
    buttons = []
    for tag in TAGS:
        buttons.append([{
            "text": f"🎨 {tag}",
            "callback": _fetch_wallpaper_tag,
            "params": {"tag": tag, "chat_id": message.chat.id},
        }])
    buttons.append([{"text": "🎲 Random", "callback": _random_wallpaper,
                     "params": {"chat_id": message.chat.id}}])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await message.delete()
    await client.inline.say(
        client, message, text,
        prefix="wall_", buttons=buttons, chat_id=message.chat.id,
    )


async def _fetch_wallpaper_tag(call, tag: str, chat_id: int):
    await call.answer(f"Fetching {tag}...")
    url = await _get_wallpaper_url(tag)
    if not url:
        return await call.edit_message("❌ No wallpaper found")

    text = (
        f"🖼️ <b>Anime Wallpaper</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🏷️ <b>Tag:</b> <code>{tag}</code>"
    )

    via = call.client.inline.viamanager
    buttons = [
        [{"text": "🔄 Next", "callback": _fetch_wallpaper_tag,
          "params": {"tag": tag, "chat_id": chat_id}}],
        [{"text": "⬅️ Tags", "callback": _back_tags,
          "params": {"chat_id": chat_id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await call.edit_message(text, reply_markup=_kb(via, buttons),
                            file=url, file_type="photo")


async def _random_wallpaper(call, chat_id: int):
    tag = random.choice(TAGS)
    await call.answer(f"🎲 {tag}")
    url = await _get_wallpaper_url(tag)
    if not url:
        return await call.edit_message("❌ No wallpaper found")

    text = (
        f"🖼️ <b>Anime Wallpaper</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🏷️ <b>Tag:</b> <code>{tag}</code>"
    )

    via = call.client.inline.viamanager
    buttons = [
        [{"text": "🔄 Next", "callback": _fetch_wallpaper_tag,
          "params": {"tag": tag, "chat_id": chat_id}}],
        [{"text": "⬅️ Tags", "callback": _back_tags,
          "params": {"chat_id": chat_id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await call.edit_message(text, reply_markup=_kb(via, buttons),
                            file=url, file_type="photo")


async def _fetch_wallpaper(message, tag, client):
    await message.edit(f"🖼️ Fetching <b>{tag}</b> wallpaper...")
    url = await _get_wallpaper_url(tag)
    if not url:
        return await message.edit("❌ No wallpaper found")

    text = (
        f"🖼️ <b>Anime Wallpaper</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🏷️ <b>Tag:</b> <code>{tag}</code>"
    )

    via = client.inline.viamanager
    buttons = [
        [{"text": "🔄 Next", "callback": _fetch_wallpaper_tag,
          "params": {"tag": tag, "chat_id": message.chat.id}}],
        [{"text": "⬅️ Tags", "callback": _back_tags,
          "params": {"chat_id": message.chat.id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await message.delete()
    await client.inline.say(
        client, message, text,
        prefix="wall_", buttons=buttons, chat_id=message.chat.id,
        file=url, file_type="photo",
    )


async def _get_wallpaper_url(tag):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.waifu.pics/many/sfw/{tag}",
            params={"q": tag},
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                files = data.get("files", [])
                if files:
                    return random.choice(files)
    return None


async def waifu_cmd(self):
    """Get random waifu image — usage: .waifu"""
    message = self.message
    await message.edit("🖼️ Fetching waifu...")

    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.waifu.pics/sfw/waifu") as resp:
            if resp.status != 200:
                return await message.edit("❌ Failed to fetch waifu")
            data = await resp.json()

    url = data.get("url", "")
    if not url:
        return await message.edit("❌ No waifu found")

    via = self.client.inline.viamanager
    text = "🖼️ <b>Random Waifu</b>\n━━━━━━━━━━━━━━━"
    buttons = [
        [{"text": "🔄 Another", "callback": _random_wallpaper,
          "params": {"chat_id": message.chat.id}}],
        [{"text": "🎨 Wallpapers", "callback": _back_tags,
          "params": {"chat_id": message.chat.id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await message.delete()
    await self.client.inline.say(
        self.client, message, text,
        prefix="wall_", buttons=buttons, chat_id=message.chat.id,
        file=url, file_type="photo",
    )


async def _back_tags(call, chat_id: int):
    via = call.client.inline.viamanager
    text = "🖼️ <b>Anime Wallpapers</b>\n━━━━━━━━━━━━━━━\n\nSelect a tag:"
    buttons = []
    for tag in TAGS:
        buttons.append([{
            "text": f"🎨 {tag}",
            "callback": _fetch_wallpaper_tag,
            "params": {"tag": tag, "chat_id": chat_id},
        }])
    buttons.append([{"text": "🎲 Random", "callback": _random_wallpaper,
                     "params": {"chat_id": chat_id}}])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _close(call):
    await call.edit_message("🗑 Closed")
