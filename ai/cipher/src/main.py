#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.



ATBASH_MAP = str.maketrans(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBA",
)


def _caesar(text: str, shift: int, decode: bool = False) -> str:
    if decode:
        shift = -shift
    result = []
    for char in text:
        if char.isupper():
            result.append(chr((ord(char) - 65 + shift) % 26 + 65))
        elif char.islower():
            result.append(chr((ord(char) - 97 + shift) % 26 + 97))
        else:
            result.append(char)
    return "".join(result)


def _vigenere(text: str, key: str, decode: bool = False) -> str:
    result = []
    key_idx = 0
    for char in text:
        if char.isalpha():
            shift = ord(key[key_idx % len(key)].lower()) - 97
            if decode:
                shift = -shift
            if char.isupper():
                result.append(chr((ord(char) - 65 + shift) % 26 + 65))
            else:
                result.append(chr((ord(char) - 97 + shift) % 26 + 97))
            key_idx += 1
        else:
            result.append(char)
    return "".join(result)


async def rot13_cmd(self):
    """Apply ROT13 cipher - usage: .rot13 <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.rot13 <text></code>\n\n"
            "📝 <b>Example:</b> <code>.rot13 Hello World</code>"
        )
        return

    text = args[1]
    result = text.translate(str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm",
    ))

    await message.edit(
        f"🔄 <b>ROT13</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Input:</b> <code>{text}</code>\n"
        f"✅ <b>Output:</b> <code>{result}</code>"
    )


async def caesar_cmd(self):
    """Apply Caesar cipher - usage: .caesar <shift> <text>"""
    message = self.message
    args = message.text.split(maxsplit=2)

    if len(args) < 3:
        await message.edit(
            "❌ <b>Usage:</b> <code>.caesar <shift> <text></code>\n\n"
            "📝 <b>Example:</b> <code>.caesar 3 Hello</code>\n\n"
            "🔢 Shift can be negative to decode: <code>.caesar -3 Khoor</code>"
        )
        return

    try:
        shift = int(args[1])
    except ValueError:
        await message.edit("❌ <b>Shift must be a number!</b>")
        return

    text = args[2]
    result = _caesar(text, shift)

    await message.edit(
        f"🔐 <b>Caesar Cipher</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Input:</b> <code>{text}</code>\n"
        f"🔢 <b>Shift:</b> <code>{shift}</code>\n"
        f"✅ <b>Output:</b> <code>{result}</code>"
    )


async def atbash_cmd(self):
    """Apply Atbash cipher - usage: .atbash <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.atbash <text></code>\n\n"
            "📝 <b>Example:</b> <code>.atbash Hello</code>"
        )
        return

    text = args[1]
    result = text.translate(ATBASH_MAP)

    await message.edit(
        f"🔐 <b>Atbash Cipher</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Input:</b> <code>{text}</code>\n"
        f"✅ <b>Output:</b> <code>{result}</code>"
    )


async def vigenere_cmd(self):
    """Apply Vigenère cipher - usage: .vigenere <key> <text>"""
    message = self.message
    args = message.text.split(maxsplit=2)

    if len(args) < 3:
        await message.edit(
            "❌ <b>Usage:</b> <code>.vigenere <key> <text></code>\n\n"
            "📝 <b>Example:</b> <code>.vigenere key Hello</code>"
        )
        return

    key = args[1]
    text = args[2]

    if not key.isalpha():
        await message.edit("❌ <b>Key must contain only letters!</b>")
        return

    result = _vigenere(text, key)

    await message.edit(
        f"🔐 <b>Vigenère Cipher</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Input:</b> <code>{text}</code>\n"
        f"🔑 <b>Key:</b> <code>{key}</code>\n"
        f"✅ <b>Output:</b> <code>{result}</code>"
    )


async def decipher_cmd(self):
    """Try to decode Caesar by showing all 25 shifts - usage: .decipher <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.decipher <text></code>\n\n"
            "📝 <b>Example:</b> <code>.decipher Khoor</code>"
        )
        return

    text = args[1]
    lines = []
    for shift in range(1, 26):
        decoded = _caesar(text, shift, decode=True)
        lines.append(f"<b>Shift {shift:2d}:</b> <code>{decoded}</code>")

    await message.edit(
        f"🔐 <b>Caesar Bruteforce</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Encrypted:</b> <code>{text}</code>\n\n"
        + "\n".join(lines)
    )
