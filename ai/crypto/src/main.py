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


TOP_COINS = [
    ("bitcoin", "BTC"), ("ethereum", "ETH"), ("tether", "USDT"),
    ("solana", "SOL"), ("binancecoin", "BNB"), ("ripple", "XRP"),
    ("cardano", "ADA"), ("dogecoin", "DOGE"), ("avalanche", "AVAX"),
    ("polkadot", "DOT"),
]


async def crypto_cmd(self):
    """Get cryptocurrency prices — usage: .crypto <coin>"""
    message = self.message
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await _show_menu(message, self.client)

    query = args[1].strip().upper()

    if query == "ALL":
        return await _show_menu(message, self.client)

    coin_id = query.lower()
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": coin_id,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_market_cap": "true",
            },
        ) as resp:
            if resp.status != 200:
                async with session.get(
                    "https://api.coingecko.com/api/v3/coins/list"
                ) as list_resp:
                    if list_resp.status != 200:
                        return await message.edit("❌ Failed to fetch data")
                    coins = await list_resp.json()
                    matches = [
                        c for c in coins
                        if query.lower() in c["name"].lower()
                        or query.lower() in c["symbol"].lower()
                    ][:5]

                    if not matches:
                        return await message.edit(
                            f"❌ No coin found for <b>{query}</b>"
                        )

                    lines = ["🔍 <b>Did you mean?</b>\n"]
                    via = self.client.inline.viamanager
                    buttons = []
                    for c in matches:
                        name = c["name"]
                        sym = c["symbol"].upper()
                        buttons.append([{
                            "text": f"{sym} — {name}",
                            "callback": _show_coin_detail,
                            "params": {"coin_id": c["id"], "chat_id": message.chat.id},
                        }])
                    buttons.append([{"text": "🗑 Close", "callback": _close}])

                    await message.delete()
                    await self.client.inline.say(
                        self.client, message,
                        "\n".join(lines),
                        prefix="crypto_", buttons=buttons,
                        chat_id=message.chat.id,
                    )
                    return

            data = await resp.json()

    if coin_id not in data:
        return await message.edit(f"❌ Coin <b>{query}</b> not found")

    coin = data[coin_id]
    price = coin.get("usd", 0)
    change = coin.get("usd_24h_change", 0)
    market_cap = coin.get("usd_market_cap", 0)

    emoji = "📈" if change and change >= 0 else "📉"
    change_str = f"{change:+.2f}%" if change else "N/A"

    text = (
        f"💰 <b>{query.upper()}</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"💵 <b>Price:</b> <code>${price:,.2f}</code>\n"
        f"{emoji} <b>24h Change:</b> <code>{change_str}</code>\n"
        f"🏦 <b>Market Cap:</b> <code>${market_cap:,.0f}</code>"
    )

    via = self.client.inline.viamanager
    buttons = [
        [{"text": "📊 Top 10", "callback": _show_top10,
          "params": {"chat_id": message.chat.id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await message.delete()
    await self.client.inline.say(
        self.client, message, text,
        prefix="crypto_", buttons=buttons, chat_id=message.chat.id,
    )


async def _show_menu(message, client):
    return await _show_top10_inner(None, message.chat.id, client, message=message)


async def _show_top10(call, chat_id: int):
    await call.answer("Loading top 10...")
    await _show_top10_inner(call, chat_id, call.client)


async def _show_top10_inner(call, chat_id: int, client, message=None):
    msg = call.message if call else message

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 10,
                "page": 1,
                "sparkline": "false",
            },
        ) as resp:
            if resp.status != 200:
                text = "❌ Failed to fetch top crypto"
                if call:
                    return await call.edit_message(text)
                return await msg.edit(text)
            data = await resp.json()

    via = client.inline.viamanager
    text = "📊 <b>Top 10 Cryptocurrencies</b>\n━━━━━━━━━━━━━━━\n\nSelect a coin:"
    buttons = []
    for i, coin in enumerate(data, 1):
        name = coin["name"]
        sym = coin["symbol"].upper()
        change = coin.get("price_change_percentage_24h", 0)
        emoji = "📈" if change and change >= 0 else "📉"
        label = f"{i}. {emoji} {sym} — ${coin['current_price']:,.2f}"
        buttons.append([{
            "text": label,
            "callback": _show_coin_detail,
            "params": {"coin_id": coin["id"], "chat_id": chat_id},
        }])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    if call:
        await call.edit_message(text, reply_markup=_kb(via, buttons))
    else:
        await msg.delete()
        await client.inline.say(
            client, msg, text,
            prefix="crypto_", buttons=buttons, chat_id=chat_id,
        )


async def _show_coin_detail(call, coin_id: str, chat_id: int):
    await call.answer("Loading...")
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": coin_id,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_market_cap": "true",
                "include_24hr_vol": "true",
            },
        ) as resp:
            if resp.status != 200:
                return await call.answer("❌ Failed to load")
            data = await resp.json()

    if coin_id not in data:
        return await call.edit_message("❌ Coin not found")

    coin = data[coin_id]
    price = coin.get("usd", 0)
    change = coin.get("usd_24h_change", 0)
    market_cap = coin.get("usd_market_cap", 0)
    volume = coin.get("usd_24h_vol", 0)

    emoji = "📈" if change and change >= 0 else "📉"
    change_str = f"{change:+.2f}%" if change else "N/A"

    text = (
        f"💰 <b>{coin_id.upper()}</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"💵 <b>Price:</b> <code>${price:,.2f}</code>\n"
        f"{emoji} <b>24h Change:</b> <code>{change_str}</code>\n"
        f"🏦 <b>Market Cap:</b> <code>${market_cap:,.0f}</code>\n"
        f"📊 <b>24h Volume:</b> <code>${volume:,.0f}</code>"
    )

    via = call.client.inline.viamanager
    buttons = [
        [{"text": "⬅️ Back to Top 10", "callback": _show_top10,
          "params": {"chat_id": chat_id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _close(call):
    await call.edit_message("🗑 Closed")
