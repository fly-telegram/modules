#     __ __     __  ___      _ ___
#    // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

from uuid import uuid4

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import secrets
import string


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


async def password_cmd(self):
    """Generate secure passwords — usage: .password [length]"""
    message = self.message
    args = message.text.split(maxsplit=1)
    length = 16
    if len(args) > 1:
        try:
            length = max(4, min(int(args[1]), 128))
        except ValueError:
            pass

    return await _generate_and_show(message, length)


async def _generate_and_show(message, length):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    password = "".join(secrets.choice(chars) for _ in range(length))

    text = (
        f"🔐 <b>Generated Password</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"<code>{password}</code>\n\n"
        f"📏 <b>Length:</b> {length}\n"
        f"🔢 <b>Entropy:</b> ~{length * 6:.0f} bits"
    )

    via = message.client.inline.viamanager
    buttons = [
        [{"text": "🔄 Regenerate", "callback": _regenerate,
          "params": {"length": length, "chat_id": message.chat.id}}],
        [{"text": "🔢 Change length", "callback": _change_length_menu,
          "params": {"chat_id": message.chat.id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await message.delete()
    await message.client.inline.say(
        message.client, message, text,
        prefix="pwd_", buttons=buttons, chat_id=message.chat.id,
    )


async def _regenerate(call, length: int, chat_id: int):
    await call.answer("Generating new password...")
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    password = "".join(secrets.choice(chars) for _ in range(length))

    text = (
        f"🔐 <b>Generated Password</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"<code>{password}</code>\n\n"
        f"📏 <b>Length:</b> {length}\n"
        f"🔢 <b>Entropy:</b> ~{length * 6:.0f} bits"
    )

    via = call.client.inline.viamanager
    buttons = [
        [{"text": "🔄 Regenerate", "callback": _regenerate,
          "params": {"length": length, "chat_id": chat_id}}],
        [{"text": "🔢 Change length", "callback": _change_length_menu,
          "params": {"chat_id": chat_id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _change_length_menu(call, chat_id: int):
    via = call.client.inline.viamanager
    text = "🔐 <b>Password Length</b>\n━━━━━━━━━━━━━━━\n\nSelect length:"
    buttons = []
    for l in [8, 12, 16, 20, 24, 32, 64]:
        buttons.append([{
            "text": f"🔢 {l} characters",
            "callback": _generate_with_length,
            "params": {"length": l, "chat_id": chat_id},
        }])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _generate_with_length(call, length: int, chat_id: int):
    await call.answer(f"Generating {length} char password...")
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    password = "".join(secrets.choice(chars) for _ in range(length))

    text = (
        f"🔐 <b>Generated Password</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"<code>{password}</code>\n\n"
        f"📏 <b>Length:</b> {length}\n"
        f"🔢 <b>Entropy:</b> ~{length * 6:.0f} bits"
    )

    via = call.client.inline.viamanager
    buttons = [
        [{"text": "🔄 Regenerate", "callback": _regenerate,
          "params": {"length": length, "chat_id": chat_id}}],
        [{"text": "🔢 Change length", "callback": _change_length_menu,
          "params": {"chat_id": chat_id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _close(call):
    await call.edit_message("🗑 Closed")
