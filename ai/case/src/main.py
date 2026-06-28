#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

import re


async def camel_cmd(self):
    """Convert to camelCase - usage: .camel <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.camel <text></code>\n\n"
            "📝 <b>Example:</b> <code>.camel hello world</code>"
        )
        return

    text = args[1]
    words = re.split(r"[\s_-]+", text)
    result = words[0].lower() + "".join(w.capitalize() for w in words[1:])

    await message.edit(
        f"🐪 <b>camelCase</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Input:</b> <code>{text}</code>\n"
        f"✅ <b>Output:</b> <code>{result}</code>"
    )


async def snake_cmd(self):
    """Convert to snake_case - usage: .snake <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.snake <text></code>\n\n"
            "📝 <b>Example:</b> <code>.snake helloWorld</code>"
        )
        return

    text = args[1]
    text = re.sub(r"([A-Z])", r"_\1", text)
    result = re.sub(r"[\s-]+", "_", text).strip("_").lower()

    await message.edit(
        f"🐍 <b>snake_case</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Input:</b> <code>{text}</code>\n"
        f"✅ <b>Output:</b> <code>{result}</code>"
    )


async def kebab_cmd(self):
    """Convert to kebab-case - usage: .kebab <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.kebab <text></code>\n\n"
            "📝 <b>Example:</b> <code>.kebab helloWorld</code>"
        )
        return

    text = args[1]
    text = re.sub(r"([A-Z])", r"-\1", text)
    result = re.sub(r"[\s_]+", "-", text).strip("-").lower()

    await message.edit(
        f"🥖 <b>kebab-case</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Input:</b> <code>{text}</code>\n"
        f"✅ <b>Output:</b> <code>{result}</code>"
    )


async def pascal_cmd(self):
    """Convert to PascalCase - usage: .pascal <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.pascal <text></code>\n\n"
            "📝 <b>Example:</b> <code>.pascal hello world</code>"
        )
        return

    text = args[1]
    words = re.split(r"[\s_-]+", text)
    result = "".join(w.capitalize() for w in words)

    await message.edit(
        f"👑 <b>PascalCase</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Input:</b> <code>{text}</code>\n"
        f"✅ <b>Output:</b> <code>{result}</code>"
    )


async def const_cmd(self):
    """Convert to CONSTANT_CASE - usage: .const <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.const <text></code>\n\n"
            "📝 <b>Example:</b> <code>.const hello world</code>"
        )
        return

    text = args[1]
    text = re.sub(r"([A-Z])", r"_\1", text)
    result = re.sub(r"[\s-]+", "_", text).strip("_").upper()

    await message.edit(
        f"🔠 <b>CONSTANT_CASE</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Input:</b> <code>{text}</code>\n"
        f"✅ <b>Output:</b> <code>{result}</code>"
    )


async def toggle_cmd(self):
    """Toggle text case (tOGGLE cASE) - usage: .toggle <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.toggle <text></code>\n\n"
            "📝 <b>Example:</b> <code>.toggle Hello World</code>"
        )
        return

    text = args[1]
    result = "".join(c.lower() if c.isupper() else c.upper() for c in text)

    await message.edit(
        f"🔄 <b>tOGGLE cASE</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Input:</b> <code>{text}</code>\n"
        f"✅ <b>Output:</b> <code>{result}</code>"
    )


async def invert_cmd(self):
    """Invert text (reverse case) - usage: .invert <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.invert <text></code>\n\n"
            "📝 <b>Example:</b> <code>.invert Hello</code>"
        )
        return

    text = args[1]
    result = text[::-1]

    await message.edit(
        f"↩️ <b>Inverted</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Input:</b> <code>{text}</code>\n"
        f"✅ <b>Output:</b> <code>{result}</code>"
    )
