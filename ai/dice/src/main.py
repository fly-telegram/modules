#     __ __     __  ___      _ ___
#    // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

from uuid import uuid4

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import secrets

DICE_FACES = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]


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


async def dice_cmd(self):
    """Roll dice — usage: .dice [NdS] like .dice 2d6"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) > 1:
        arg = args[1].strip().lower()
        if arg == "coin":
            return await _flip_coin(message, self.client)
        try:
            if "d" in arg:
                parts = arg.split("d")
                num = int(parts[0]) if parts[0] else 1
                sides = int(parts[1]) if parts[1] else 6
            else:
                num = 1
                sides = int(arg)
            num = max(1, min(num, 10))
            sides = max(2, min(sides, 100))
            return await _roll_dice(message, num, sides, self.client)
        except ValueError:
            pass

    return await _show_dice_menu(message, self.client)


async def _show_dice_menu(message, client):
    via = client.inline.viamanager
    text = "🎲 <b>Dice & Games</b>\n━━━━━━━━━━━━━━━\n\nSelect an option:"
    buttons = [
        [{"text": "🎲 1d6 (Standard)", "callback": _roll_cb,
          "params": {"num": 1, "sides": 6, "chat_id": message.chat.id}}],
        [{"text": "🎲 2d6", "callback": _roll_cb,
          "params": {"num": 2, "sides": 6, "chat_id": message.chat.id}}],
        [{"text": "🎲 1d20", "callback": _roll_cb,
          "params": {"num": 1, "sides": 20, "chat_id": message.chat.id}}],
        [{"text": "🪙 Flip Coin", "callback": _coin_cb,
          "params": {"chat_id": message.chat.id}}],
        [{"text": "🔢 Random Number", "callback": _random_num_menu,
          "params": {"chat_id": message.chat.id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await message.delete()
    await client.inline.say(
        client, message, text,
        prefix="dice_", buttons=buttons, chat_id=message.chat.id,
    )


async def _roll_dice(message, num, sides, client):
    results = [secrets.randbelow(sides) + 1 for _ in range(num)]
    total = sum(results)

    text = f"🎲 <b>Rolling {num}d{sides}</b>\n━━━━━━━━━━━━━━━\n\n"

    if num <= 5:
        for i, r in enumerate(results, 1):
            if sides == 6 and r <= 6:
                text += f"  {DICE_FACES[r-1]} <code>{r}</code>\n"
            else:
                text += f"  🎲 <code>{r}</code>\n"
    else:
        text += f"  Results: {', '.join(str(r) for r in results)}\n"

    if num > 1:
        text += f"\n  📊 <b>Total:</b> <code>{total}</code>"
        text += f"\n  📈 <b>Average:</b> <code>{total / num:.1f}</code>"

    via = client.inline.viamanager
    buttons = [
        [{"text": "🔄 Roll Again", "callback": _roll_cb,
          "params": {"num": num, "sides": sides, "chat_id": message.chat.id}}],
        [{"text": "⬅️ Menu", "callback": _back_menu,
          "params": {"chat_id": message.chat.id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await message.delete()
    await client.inline.say(
        client, message, text,
        prefix="dice_", buttons=buttons, chat_id=message.chat.id,
    )


async def _roll_cb(call, num: int, sides: int, chat_id: int):
    await call.answer(f"Rolling {num}d{sides}...")
    results = [secrets.randbelow(sides) + 1 for _ in range(num)]
    total = sum(results)

    text = f"🎲 <b>Rolling {num}d{sides}</b>\n━━━━━━━━━━━━━━━\n\n"
    for i, r in enumerate(results, 1):
        if sides == 6 and r <= 6:
            text += f"  {DICE_FACES[r-1]} <code>{r}</code>\n"
        else:
            text += f"  🎲 <code>{r}</code>\n"

    if num > 1:
        text += f"\n  📊 <b>Total:</b> <code>{total}</code>"
        text += f"\n  📈 <b>Average:</b> <code>{total / num:.1f}</code>"

    via = call.client.inline.viamanager
    buttons = [
        [{"text": "🔄 Roll Again", "callback": _roll_cb,
          "params": {"num": num, "sides": sides, "chat_id": chat_id}}],
        [{"text": "⬅️ Menu", "callback": _back_menu,
          "params": {"chat_id": chat_id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _flip_coin(message, client):
    result = secrets.choice(["Heads", "Tails"])
    emoji = "🪙"

    text = (
        f"{emoji} <b>Coin Flip</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"  🪄 <code>{result}</code>"
    )

    via = client.inline.viamanager
    buttons = [
        [{"text": "🔄 Flip Again", "callback": _coin_cb,
          "params": {"chat_id": message.chat.id}}],
        [{"text": "⬅️ Menu", "callback": _back_menu,
          "params": {"chat_id": message.chat.id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await message.delete()
    await client.inline.say(
        client, message, text,
        prefix="dice_", buttons=buttons, chat_id=message.chat.id,
    )


async def _coin_cb(call, chat_id: int):
    await call.answer("Flipping...")
    result = secrets.choice(["Heads", "Tails"])

    text = (
        f"🪙 <b>Coin Flip</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"  🪄 <code>{result}</code>"
    )

    via = call.client.inline.viamanager
    buttons = [
        [{"text": "🔄 Flip Again", "callback": _coin_cb,
          "params": {"chat_id": chat_id}}],
        [{"text": "⬅️ Menu", "callback": _back_menu,
          "params": {"chat_id": chat_id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _random_num_menu(call, chat_id: int):
    via = call.client.inline.viamanager
    text = "🔢 <b>Random Number Generator</b>\n━━━━━━━━━━━━━━━\n\nSelect range:"
    buttons = []
    for rng in [(1, 10), (1, 100), (1, 1000), (1, 10000)]:
        buttons.append([{
            "text": f"🔢 1 — {rng[1]}",
            "callback": _random_num_cb,
            "params": {"min_v": rng[0], "max_v": rng[1], "chat_id": chat_id},
        }])
    buttons.append([{"text": "⬅️ Menu", "callback": _back_menu,
                     "params": {"chat_id": chat_id}}])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _random_num_cb(call, min_v: int, max_v: int, chat_id: int):
    result = secrets.randbelow(max_v - min_v + 1) + min_v
    text = (
        f"🔢 <b>Random Number</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"Range: <code>{min_v} — {max_v}</code>\n"
        f"Result: <b>{result}</b>"
    )

    via = call.client.inline.viamanager
    buttons = [
        [{"text": "🔄 Again", "callback": _random_num_cb,
          "params": {"min_v": min_v, "max_v": max_v, "chat_id": chat_id}}],
        [{"text": "⬅️ Back", "callback": _random_num_menu,
          "params": {"chat_id": chat_id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _back_menu(call, chat_id: int):
    via = call.client.inline.viamanager
    text = "🎲 <b>Dice & Games</b>\n━━━━━━━━━━━━━━━\n\nSelect an option:"
    buttons = [
        [{"text": "🎲 1d6 (Standard)", "callback": _roll_cb,
          "params": {"num": 1, "sides": 6, "chat_id": chat_id}}],
        [{"text": "🎲 2d6", "callback": _roll_cb,
          "params": {"num": 2, "sides": 6, "chat_id": chat_id}}],
        [{"text": "🎲 1d20", "callback": _roll_cb,
          "params": {"num": 1, "sides": 20, "chat_id": chat_id}}],
        [{"text": "🪙 Flip Coin", "callback": _coin_cb,
          "params": {"chat_id": chat_id}}],
        [{"text": "🔢 Random Number", "callback": _random_num_menu,
          "params": {"chat_id": chat_id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _close(call):
    await call.edit_message("🗑 Closed")
