#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

import urllib.parse


# Common language codes for quick reference
LANG_CODES = {
    "en": "English", "ru": "Russian", "es": "Spanish", "fr": "French",
    "de": "German", "it": "Italian", "pt": "Portuguese", "zh": "Chinese",
    "ja": "Japanese", "ko": "Korean", "ar": "Arabic", "hi": "Hindi",
    "tr": "Turkish", "pl": "Polish", "uk": "Ukrainian", "nl": "Dutch",
    "sv": "Swedish", "fi": "Finnish", "cs": "Czech", "ro": "Romanian",
    "hu": "Hungarian", "bg": "Bulgarian", "el": "Greek", "he": "Hebrew",
    "th": "Thai", "vi": "Vietnamese", "id": "Indonesian", "ms": "Malay",
    "auto": "Auto-detect",
}


def _detect_lang_name(code: str) -> str:
    """Get language name from code."""
    return LANG_CODES.get(code.lower(), code.upper())


async def tr_cmd(self):
    """Translate text — usage: .tr <lang> <text> or reply with .tr <lang>

    Examples: .tr en Привет | .tr ru Hello | reply: .tr en
    """
    message = self.message
    args = message.text.split(maxsplit=2)

    target_lang = None
    text = None

    # Check reply for text source
    if message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
        if len(args) >= 2:
            target_lang = args[1].strip().lower()
        else:
            target_lang = "en"  # default
    else:
        if len(args) < 3:
            await message.edit(
                "❌ <b>Usage:</b> <code>.tr <lang> <text></code>\n\n"
                "📝 <b>Examples:</b>\n"
                "• <code>.tr en Привет мир</code>\n"
                "• <code>.tr ru Hello world</code>\n"
                "• Reply to message: <code>.tr en</code>\n\n"
                "🌐 <b>Common codes:</b> en, ru, es, fr, de, it, pt, zh, ja, ko, ar, tr, pl, uk"
            )
            return
        target_lang = args[1].strip().lower()
        text = args[2]

    if target_lang not in LANG_CODES and target_lang != "auto":
        await message.edit(
            f"❌ <b>Unknown language code:</b> <code>{target_lang}</code>\n\n"
            f"🌐 <b>Common codes:</b> en, ru, es, fr, de, it, pt, zh, ja, ko, ar, tr, pl, uk"
        )
        return

    status_msg = await message.edit("🔄 <b>Translating...</b>")

    try:
        import aiohttp

        encoded_text = urllib.parse.quote(text)
        url = (
            f"https://translate.googleapis.com/translate_a/single"
            f"?client=gtx&sl=auto&tl={target_lang}&dt=t&q={encoded_text}"
        )

        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await status_msg.edit(f"❌ <b>Translation failed (HTTP {resp.status})</b>")
                    return
                data = await resp.json()

        # Parse response — translated text is in data[0]
        translated_parts = []
        for part in data[0]:
            if part[0]:
                translated_parts.append(part[0])
        translated = "".join(translated_parts)

        # Source language
        source_lang = data[2] if len(data) > 2 else "unknown"
        source_name = _detect_lang_name(source_lang)
        target_name = _detect_lang_name(target_lang)

        # Truncate long texts for display
        orig_display = text[:200] + ("..." if len(text) > 200 else "")
        trans_display = translated[:200] + \
            ("..." if len(translated) > 200 else "")

        result = (
            f"🌐 <b>Translation</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"📥 <b>{source_name} → {target_name}</b>\n\n"
            f"📝 <b>Original:</b>\n<code>{orig_display}</code>\n\n"
            f"✅ <b>Translated:</b>\n<code>{trans_display}</code>"
        )

        await status_msg.edit(result)

    except ImportError:
        await status_msg.edit(
            "❌ <b>aiohttp is required!</b>\n\n"
            "Install it: <code>pip install aiohttp</code>"
        )
    except Exception as e:
        await status_msg.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def langs_cmd(self):
    """Show available language codes"""
    message = self.message

    lines = []
    for code, name in sorted(LANG_CODES.items(), key=lambda x: x[1]):
        lines.append(f"• <code>{code}</code> — {name}")

    result = (
        "🌐 <b>Available Languages</b>\n"
        "━━━━━━━━━━━━━━━\n\n"
        + "\n".join(lines)
    )

    await message.edit(result)
