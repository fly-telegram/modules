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


async def color_cmd(self):
    """Get color info — usage: .color <hex|rgb|name>"""
    message = self.message
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.edit(
            "❌ <b>Usage:</b> <code>.color <hex/rgb/name></code>\n\n"
            "📝 <b>Examples:</b>\n"
            "  <code>.color #FF5733</code>\n"
            "  <code>.color 255 87 51</code>\n"
            "  <code>.color red</code>"
        )

    query = args[1].strip()
    await message.edit(f"🎨 Looking up color <b>{query}</b>...")

    hex_color = None
    if query.startswith("#"):
        hex_color = query[1:]
    elif query.count(" ") == 2:
        parts = query.split()
        try:
            r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
            hex_color = f"{r:02x}{g:02x}{b:02x}"
        except ValueError:
            pass
    else:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://www.thecolorapi.com/id",
                params={"name": query, "format": "json"},
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    hex_color = data.get("hex", {}).get("clean", "")

    if not hex_color:
        return await message.edit(
            f"❌ Could not parse color: <b>{query}</b>"
        )

    hex_color = hex_color.lstrip("#")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://www.thecolorapi.com/id",
            params={"hex": hex_color, "format": "json"},
        ) as resp:
            if resp.status != 200:
                return await message.edit("❌ Failed to get color info")
            data = await resp.json()

    name = data.get("name", {}).get("value", "Unknown")
    hex_val = data.get("hex", {}).get("value", f"#{hex_color}")
    rgb = data.get("rgb", {})
    rgb_val = rgb.get("value", "")
    r, g, b = rgb.get("r", 0), rgb.get("g", 0), rgb.get("b", 0)
    hsl = data.get("hsl", {})
    h, s, l = hsl.get("h", 0), hsl.get("s", 0), hsl.get("l", 0)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    contrast = "#FFFFFF" if luminance < 0.5 else "#000000"
    image_url = f"https://www.thecolorapi.com/id?format=png&hex={hex_color}"

    text = (
        f"🎨 <b>Color: {name}</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"⬛ <b>HEX:</b> <code>{hex_val}</code>\n"
        f"🔴 <b>RGB:</b> <code>{rgb_val}</code>\n"
        f"🟡 <b>HSL:</b> <code>{h}°, {s}%, {l}%</code>\n"
        f"💡 <b>Luminance:</b> <code>{luminance:.2%}</code>"
    )

    via = self.client.inline.viamanager
    buttons = [
        [{"text": "🖼️ View color", "url": image_url}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await message.delete()
    await self.client.inline.say(
        self.client, message, text,
        prefix="color_", buttons=buttons, chat_id=message.chat.id,
    )


async def _close(call):
    await call.edit_message("🗑 Closed")
