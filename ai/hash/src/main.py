#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

import hashlib


async def hash_cmd(self):
    """Generate hashes - usage: .hash <algorithm> <text>

    Algorithms: md5, sha1, sha256, sha512
    """
    message = self.message
    args = message.text.split(maxsplit=2)

    if len(args) < 3:
        await message.edit(
            "❌ <b>Usage:</b> <code>.hash <type> <text></code>\n\n"
            "🔢 <b>Available types:</b>\n"
            "• <code>md5</code>\n"
            "• <code>sha1</code>\n"
            "• <code>sha256</code>\n"
            "• <code>sha512</code>\n\n"
            "📝 <b>Example:</b> <code>.hash sha256 hello</code>"
        )
        return

    alg = args[1].lower()
    text = args[2]

    alg_map = {
        "md5": hashlib.md5,
        "sha1": hashlib.sha1,
        "sha256": hashlib.sha256,
        "sha512": hashlib.sha512,
    }

    if alg not in alg_map:
        algs = ", ".join(f"<code>{a}</code>" for a in alg_map)
        await message.edit(
            f"❌ <b>Unknown algorithm:</b> <code>{alg}</code>\n\n"
            f"📋 <b>Available:</b> {algs}"
        )
        return

    try:
        result = alg_map[alg](text.encode()).hexdigest()

        await message.edit(
            f"🔐 <b>Hash Generator</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"📝 <b>Text:</b> <code>{text}</code>\n"
            f"🔢 <b>Algorithm:</b> <code>{alg.upper()}</code>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"<code>{result}</code>\n\n"
            f"📏 <b>Length:</b> {len(result)} chars"
        )
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def md5_cmd(self):
    """Generate MD5 hash - usage: .md5 <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.md5 <text></code>\n\n"
            "📝 <b>Example:</b> <code>.md5 hello</code>"
        )
        return

    text = args[1]
    result = hashlib.md5(text.encode()).hexdigest()

    await message.edit(
        f"🔐 <b>MD5 Hash</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Text:</b> <code>{text}</code>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<code>{result}</code>"
    )


async def sha256_cmd(self):
    """Generate SHA-256 hash - usage: .sha256 <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.sha256 <text></code>\n\n"
            "📝 <b>Example:</b> <code>.sha256 hello</code>"
        )
        return

    text = args[1]
    result = hashlib.sha256(text.encode()).hexdigest()

    await message.edit(
        f"🔐 <b>SHA-256 Hash</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Text:</b> <code>{text}</code>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<code>{result}</code>"
    )
