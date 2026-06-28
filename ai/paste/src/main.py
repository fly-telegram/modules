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


async def paste_cmd(self):
    """Upload text to pastebin — usage: .paste <text> or reply to a message"""
    message = self.message

    if message.reply_to:
        content = message.reply_to.text or message.reply_to.caption
        if not content:
            return await message.edit("❌ Replied message has no text")
    else:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            return await message.edit(
                "❌ <b>Usage:</b>\n"
                "  <code>.paste <text></code>\n"
                "  or reply to a message with <code>.paste</code>\n\n"
                "📝 <b>Example:</b> <code>.paste Hello World!</code>"
            )
        content = args[1]

    await message.edit("📤 Uploading to pastebin...")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://batbin.me/api/v2/paste",
            json={"content": content},
        ) as resp:
            if resp.status != 200:
                return await message.edit("❌ Upload failed")
            data = await resp.json()

    key = data.get("key")
    if not key:
        return await message.edit("❌ Failed to get paste URL")

    url = f"https://batbin.me/{key}"
    raw_url = f"https://batbin.me/raw/{key}"

    via = message.client.inline.viamanager
    text = (
        f"✅ <b>Paste uploaded!</b>\n\n"
        f"📄 <b>Content:</b> {len(content)} chars"
    )
    buttons = [
        [{"text": "🔗 Open paste", "url": url}],
        [{"text": "📄 View raw", "url": raw_url}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await message.delete()
    await message.client.inline.say(
        message.client, message, text,
        prefix="paste_", buttons=buttons, chat_id=message.chat.id,
    )


async def _close(call):
    await call.edit_message("🗑 Closed")
