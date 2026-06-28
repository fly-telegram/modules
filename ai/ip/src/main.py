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


async def ip_cmd(self):
    """Get your IP or lookup an IP address — usage: .ip [address]"""
    message = self.message
    args = message.text.split(maxsplit=1)
    target = args[1].strip() if len(args) > 1 else None

    await message.edit("🌐 Looking up IP info...")

    if target:
        url = f"https://ipapi.co/{target}/json/"
    else:
        url = "https://ipapi.co/json/"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return await message.edit("❌ Failed to lookup IP")
            data = await resp.json()

    ip = data.get("ip", target or "Unknown")
    city = data.get("city", "Unknown")
    region = data.get("region", "Unknown")
    country = data.get("country_name", "Unknown")
    country_code = data.get("country_code", "")
    org = data.get("org", data.get("asn", "Unknown"))
    postal = data.get("postal", "N/A")
    lat = data.get("latitude", "?")
    lon = data.get("longitude", "?")
    timezone = data.get("timezone", "Unknown")
    currency = data.get("currency", "N/A")
    flag = f"https://flagcdn.com/16x12/{country_code.lower()}.png" if country_code else ""

    flag_line = f"<img src='{flag}'> " if flag else ""

    text = (
        f"🌐 <b>IP Information</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📍 <b>IP:</b> <code>{ip}</code>\n"
        f"{flag_line}<b>Location:</b> {city}, {region}"
        f"\n🌍 <b>Country:</b> {country} ({country_code})"
        f"\n📮 <b>Postal:</b> <code>{postal}</code>"
        f"\n🏢 <b>ISP:</b> <code>{org}</code>"
        f"\n🕐 <b>Timezone:</b> <code>{timezone}</code>"
        f"\n💵 <b>Currency:</b> <code>{currency}</code>"
        f"\n📍 <b>Coordinates:</b> {lat}, {lon}"
    )

    via = message.client.inline.viamanager
    buttons = [
        [{"text": "🔄 My IP", "callback": _my_ip,
          "params": {"chat_id": message.chat.id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await message.delete()
    await message.client.inline.say(
        message.client, message, text,
        prefix="ip_", buttons=buttons, chat_id=message.chat.id,
    )


async def _my_ip(call, chat_id: int):
    await call.answer("Looking up...")
    async with aiohttp.ClientSession() as session:
        async with session.get("https://ipapi.co/json/") as resp:
            if resp.status != 200:
                return await call.edit_message("❌ Failed to lookup")
            data = await resp.json()

    ip = data.get("ip", "Unknown")
    city = data.get("city", "Unknown")
    region = data.get("region", "Unknown")
    country = data.get("country_name", "Unknown")
    country_code = data.get("country_code", "")
    org = data.get("org", "Unknown")

    text = (
        f"🌐 <b>My IP</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📍 <b>IP:</b> <code>{ip}</code>\n"
        f"🌍 <b>Location:</b> {city}, {region}, {country} ({country_code})\n"
        f"🏢 <b>ISP:</b> <code>{org}</code>"
    )

    via = call.client.inline.viamanager
    buttons = [[{"text": "🗑 Close", "callback": _close}]]
    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _close(call):
    await call.edit_message("🗑 Closed")
