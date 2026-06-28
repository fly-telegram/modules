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


async def define_cmd(self):
    """Get word definitions — usage: .define <word>"""
    message = self.message
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.edit(
            "❌ <b>Usage:</b> <code>.define <word></code>\n\n"
            "📝 <b>Example:</b> <code>.define serendipity</code>"
        )

    word = args[1].strip().lower()
    await message.edit(f"📖 Looking up <b>{word}</b>...")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        ) as resp:
            if resp.status != 200:
                return await message.edit(
                    f"❌ No definition found for <b>{word}</b>"
                )
            data = await resp.json()

    if not data:
        return await message.edit(f"❌ No definition found for <b>{word}</b>")

    entry = data[0]
    word = entry.get("word", word)
    phonetic = entry.get("phonetic", "")
    phonetics = entry.get("phonetics", [])

    audio_url = ""
    for p in phonetics:
        if p.get("audio"):
            audio_url = p["audio"]
            break

    meanings = entry.get("meanings", [])

    lines = [f"📖 <b>{word}</b>\n━━━━━━━━━━━━━━━\n"]
    if phonetic:
        lines.append(f"🔊 <b>Pronunciation:</b> <code>{phonetic}</code>\n")

    for meaning in meanings[:2]:
        part = meaning.get("partOfSpeech", "unknown")
        defs = meaning.get("definitions", [])[:2]
        lines.append(f"📌 <b>{part}</b>")
        for d in defs:
            definition = d.get("definition", "")
            example = d.get("example", "")
            lines.append(f"  • {definition}")
            if example:
                lines.append(f"    <i>\"{example}\"</i>")
        lines.append("")

    synonyms = set()
    for meaning in meanings:
        for s in meaning.get("synonyms", [])[:3]:
            synonyms.add(s)
    if synonyms:
        lines.append(f"🔗 <b>Synonyms:</b> <code>{', '.join(list(synonyms)[:5])}</code>")

    text = "\n".join(lines)

    via = self.client.inline.viamanager
    buttons = []
    if audio_url:
        buttons.append([{"text": "🔊 Play pronunciation", "url": audio_url}])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await message.delete()
    await self.client.inline.say(
        self.client, message, text,
        prefix="def_", buttons=buttons, chat_id=message.chat.id,
    )


async def _close(call):
    await call.edit_message("🗑 Closed")
