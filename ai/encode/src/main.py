#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

import base64
import urllib.parse


async def b64enc_cmd(self):
    """Encode to Base64 - usage: .b64enc <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.b64enc <text></code>\n\n"
            "📝 <b>Example:</b> <code>.b64enc Hello World</code>"
        )
        return

    text = args[1]

    try:
        encoded = base64.b64encode(text.encode()).decode()

        await message.edit(
            f"🔐 <b>Base64 Encode</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"📝 <b>Input:</b> <code>{text}</code>\n"
            f"✅ <b>Output:</b> <code>{encoded}</code>"
        )
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def b64dec_cmd(self):
    """Decode Base64 - usage: .b64dec <encoded>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.b64dec <encoded></code>\n\n"
            "📝 <b>Example:</b> <code>.b64dec SGVsbG8=</code>"
        )
        return

    encoded = args[1]

    try:
        decoded = base64.b64decode(encoded).decode()

        await message.edit(
            f"🔓 <b>Base64 Decode</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"📝 <b>Input:</b> <code>{encoded}</code>\n"
            f"✅ <b>Output:</b> <code>{decoded}</code>"
        )
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def b32enc_cmd(self):
    """Encode to Base32 - usage: .b32enc <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.b32enc <text></code>\n\n"
            "📝 <b>Example:</b> <code>.b32enc Hello World</code>"
        )
        return

    text = args[1]

    try:
        encoded = base64.b32encode(text.encode()).decode()

        await message.edit(
            f"🔐 <b>Base32 Encode</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"📝 <b>Input:</b> <code>{text}</code>\n"
            f"✅ <b>Output:</b> <code>{encoded}</code>"
        )
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def b32dec_cmd(self):
    """Decode Base32 - usage: .b32dec <encoded>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.b32dec <encoded></code>\n\n"
            "📝 <b>Example:</b> <code>.b32dec NBSWY3DP</code>"
        )
        return

    encoded = args[1]

    try:
        decoded = base64.b32decode(encoded).decode()

        await message.edit(
            f"🔓 <b>Base32 Decode</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"📝 <b>Input:</b> <code>{encoded}</code>\n"
            f"✅ <b>Output:</b> <code>{decoded}</code>"
        )
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def hexenc_cmd(self):
    """Encode to Hex - usage: .hexenc <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.hexenc <text></code>\n\n"
            "📝 <b>Example:</b> <code>.hexenc Hello</code>"
        )
        return

    text = args[1]

    try:
        encoded = text.encode().hex()

        await message.edit(
            f"🔐 <b>Hex Encode</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"📝 <b>Input:</b> <code>{text}</code>\n"
            f"✅ <b>Output:</b> <code>{encoded}</code>"
        )
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def hexdec_cmd(self):
    """Decode Hex - usage: .hexdec <encoded>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.hexdec <encoded></code>\n\n"
            "📝 <b>Example:</b> <code>.hexdec 48656c6c6f</code>"
        )
        return

    encoded = args[1]

    try:
        decoded = bytes.fromhex(encoded).decode()

        await message.edit(
            f"🔓 <b>Hex Decode</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"📝 <b>Input:</b> <code>{encoded}</code>\n"
            f"✅ <b>Output:</b> <code>{decoded}</code>"
        )
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def urlenc_cmd(self):
    """URL-encode text - usage: .urlenc <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.urlenc <text></code>\n\n"
            "📝 <b>Example:</b> <code>.urlenc hello world</code>"
        )
        return

    text = args[1]
    encoded = urllib.parse.quote(text)

    await message.edit(
        f"🔐 <b>URL Encode</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Input:</b> <code>{text}</code>\n"
        f"✅ <b>Output:</b> <code>{encoded}</code>"
    )


async def urldec_cmd(self):
    """URL-decode text - usage: .urldec <encoded>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.urldec <encoded></code>\n\n"
            "📝 <b>Example:</b> <code>.urldec hello+world</code>"
        )
        return

    encoded = args[1]

    try:
        decoded = urllib.parse.unquote(encoded)

        await message.edit(
            f"🔓 <b>URL Decode</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"📝 <b>Input:</b> <code>{encoded}</code>\n"
            f"✅ <b>Output:</b> <code>{decoded}</code>"
        )
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")
