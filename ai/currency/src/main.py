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


POPULAR = ["EUR", "GBP", "JPY", "RUB", "CNY", "KRW", "INR", "BRL", "CHF", "CAD", "AUD", "TRY"]


async def currency_cmd(self):
    """Convert currencies — usage: .currency <amount> <from> <to>"""
    message = self.message
    args = message.text.split()
    if len(args) < 2:
        return await _show_currency_menu(message)

    if args[1].upper() == "RATES":
        return await _show_rates(message)

    if len(args) < 4:
        return await message.edit(
            "❌ <b>Usage:</b> <code>.currency <amount> <from> <to></code>\n\n"
            "📝 <b>Examples:</b>\n"
            "  <code>.currency 100 USD EUR</code>\n"
            "  <code>.currency 50 RUB USD</code>"
        )

    try:
        amount = float(args[1])
    except ValueError:
        return await message.edit(f"❌ Invalid amount: <b>{args[1]}</b>")

    from_cur = args[2].upper()
    to_cur = args[3].upper()

    result = await _convert(amount, from_cur, to_cur)
    if result is None:
        return

    via = message.client.inline.viamanager
    text = (
        f"💱 <b>Currency Conversion</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"<b>{amount:,.2f}</b> {from_cur}\n"
        f"     👇\n"
        f"<b>{result:,.2f}</b> {to_cur}\n\n"
    )

    buttons = [
        [{"text": "🔄 Swap", "callback": _swap_convert,
          "params": {
              "amount": result, "from_cur": to_cur, "to_cur": from_cur,
              "chat_id": message.chat.id,
          }}],
        [{"text": "💱 Show rates", "callback": _show_rates_inline,
          "params": {"chat_id": message.chat.id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await message.delete()
    await message.client.inline.say(
        message.client, message, text,
        prefix="cur_", buttons=buttons, chat_id=message.chat.id,
    )


async def _convert(amount, from_cur, to_cur, call=None, message=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.exchangerate-api.com/v4/latest/USD"
        ) as resp:
            if resp.status != 200:
                if call:
                    await call.answer("❌ Failed to fetch rates")
                elif message:
                    await message.edit("❌ Failed to fetch rates")
                return None
            data = await resp.json()

    rates = data.get("rates", {})
    if from_cur not in rates:
        if call:
            await call.answer(f"❌ Unknown currency: {from_cur}")
        elif message:
            message.edit(f"❌ Unknown currency: <b>{from_cur}</b>")
        return None
    if to_cur not in rates:
        if call:
            await call.answer(f"❌ Unknown currency: {to_cur}")
        elif message:
            message.edit(f"❌ Unknown currency: <b>{to_cur}</b>")
        return None

    usd_amount = amount / rates[from_cur]
    return usd_amount * rates[to_cur]


async def _swap_convert(call, amount: float, from_cur: str, to_cur: str, chat_id: int):
    await call.answer(f"Converting {amount:,.2f} {from_cur} to {to_cur}...")
    result = await _convert(amount, from_cur, to_cur, call=call)
    if result is None:
        return

    text = (
        f"💱 <b>Currency Conversion</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"<b>{amount:,.2f}</b> {from_cur}\n"
        f"     👇\n"
        f"<b>{result:,.2f}</b> {to_cur}\n\n"
    )

    via = call.client.inline.viamanager
    buttons = [
        [{"text": "🔄 Swap", "callback": _swap_convert,
          "params": {
              "amount": result, "from_cur": to_cur, "to_cur": from_cur,
              "chat_id": chat_id,
          }}],
        [{"text": "💱 Show rates", "callback": _show_rates_inline,
          "params": {"chat_id": chat_id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _show_currency_menu(message):
    via = message.client.inline.viamanager
    text = "💱 <b>Currency Converter</b>\n━━━━━━━━━━━━━━━\n\n"
    text += "Use <code>.currency 100 USD EUR</code>\nor select a popular pair:"

    buttons = []
    pairs = [("USD", "EUR"), ("USD", "RUB"), ("EUR", "USD"), ("USD", "JPY"),
             ("USD", "GBP"), ("EUR", "RUB")]
    for f, t in pairs:
        buttons.append([{
            "text": f"💱 1 {f} → {t}",
            "callback": _show_pair_rate,
            "params": {"from_cur": f, "to_cur": t, "chat_id": message.chat.id},
        }])
    buttons.append([{"text": "📊 All rates", "callback": _show_rates_inline,
                     "params": {"chat_id": message.chat.id}}])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await message.delete()
    await message.client.inline.say(
        message.client, message, text,
        prefix="cur_", buttons=buttons, chat_id=message.chat.id,
    )


async def _show_pair_rate(call, from_cur: str, to_cur: str, chat_id: int):
    await call.answer("Loading...")
    result = await _convert(1, from_cur, to_cur, call=call)
    if result is None:
        return

    text = (
        f"💱 <b>Exchange Rate</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"1 {from_cur} = <b>{result:,.4f}</b> {to_cur}\n\n"
    )

    via = call.client.inline.viamanager
    buttons = [
        [{"text": "🔄 Swap", "callback": _show_pair_rate,
          "params": {"from_cur": to_cur, "to_cur": from_cur, "chat_id": chat_id}}],
        [{"text": "⬅️ Menu", "callback": _back_currency_menu,
          "params": {"chat_id": chat_id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _show_rates(message):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.exchangerate-api.com/v4/latest/USD"
        ) as resp:
            if resp.status != 200:
                return await message.edit("❌ Failed to fetch rates")
            data = await resp.json()

    rates = data.get("rates", {})
    lines = ["💱 <b>Popular Exchange Rates</b>\n━━━━━━━━━━━━━━━\n<b>Base: USD</b>\n"]
    for cur in POPULAR:
        if cur in rates:
            lines.append(f"  • <code>{cur}</code>: {rates[cur]:,.4f}")

    via = message.client.inline.viamanager
    buttons = [
        [{"text": "💱 Convert", "callback": _back_currency_menu,
          "params": {"chat_id": message.chat.id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await message.delete()
    await message.client.inline.say(
        message.client, message, "\n".join(lines),
        prefix="cur_", buttons=buttons, chat_id=message.chat.id,
    )


async def _show_rates_inline(call, chat_id: int):
    await call.answer("Loading rates...")
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.exchangerate-api.com/v4/latest/USD"
        ) as resp:
            if resp.status != 200:
                return await call.answer("❌ Failed to fetch")
            data = await resp.json()

    rates = data.get("rates", {})
    lines = ["💱 <b>Popular Exchange Rates</b>\n━━━━━━━━━━━━━━━\n<b>Base: USD</b>\n"]
    for cur in POPULAR:
        if cur in rates:
            lines.append(f"  • <code>{cur}</code>: {rates[cur]:,.4f}")

    via = call.client.inline.viamanager
    buttons = [
        [{"text": "💱 Convert", "callback": _back_currency_menu,
          "params": {"chat_id": chat_id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await call.edit_message("\n".join(lines), reply_markup=_kb(via, buttons))


async def _back_currency_menu(call, chat_id: int):
    via = call.client.inline.viamanager
    text = "💱 <b>Currency Converter</b>\n━━━━━━━━━━━━━━━\n\nSelect a popular pair:"
    buttons = []
    pairs = [("USD", "EUR"), ("USD", "RUB"), ("EUR", "USD"), ("USD", "JPY"),
             ("USD", "GBP"), ("EUR", "RUB")]
    for f, t in pairs:
        buttons.append([{
            "text": f"💱 1 {f} → {t}",
            "callback": _show_pair_rate,
            "params": {"from_cur": f, "to_cur": t, "chat_id": chat_id},
        }])
    buttons.append([{"text": "📊 All rates", "callback": _show_rates_inline,
                     "params": {"chat_id": chat_id}}])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _close(call):
    await call.edit_message("🗑 Closed")
