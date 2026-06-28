#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

import uuid


async def uuid_cmd(self):
    """Generate UUIDs - usage: .uuid [type]

    Types: v1, v4 (default), v5, v7
    """
    message = self.message
    args = message.text.split(maxsplit=2)

    ver = "v4"
    name = ""

    if len(args) > 1:
        ver = args[1].lower()
    if len(args) > 2:
        name = args[2]

    if ver == "v1":
        result = str(uuid.uuid1())
    elif ver == "v4":
        result = str(uuid.uuid4())
    elif ver == "v5":
        if not name:
            await message.edit(
                "❌ <b>UUID v5 requires a name!</b>\n\n"
                "📝 <b>Usage:</b> <code>.uuid v5 <namespace> <name></code>"
            )
            return
        result = str(uuid.uuid5(uuid.NAMESPACE_DNS, name))
    elif ver == "v7":
        try:
            result = str(uuid.uuid7())
        except AttributeError:
            await message.edit(
                "❌ <b>UUID v7 requires Python 3.14+</b>\n\n"
                "Use <code>.uuid v4</code> instead."
            )
            return
    else:
        await message.edit(
            f"❌ <b>Unknown type:</b> <code>{ver}</code>\n\n"
            "📋 <b>Available:</b> v1, v4, v5, v7"
        )
        return

    await message.edit(
        f"🆔 <b>UUID Generator</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"🔢 <b>Version:</b> <code>{ver.upper()}</code>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<code>{result}</code>\n\n"
        f"📏 <b>Length:</b> {len(result)} chars"
    )


async def uuid4_cmd(self):
    """Generate UUID v4 - usage: .uuid4"""
    message = self.message
    result = str(uuid.uuid4())

    await message.edit(
        f"🆔 <b>UUID v4</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"<code>{result}</code>"
    )


async def uuid7_cmd(self):
    """Generate UUID v7 - usage: .uuid7"""
    message = self.message

    try:
        result = str(uuid.uuid7())
    except AttributeError:
        await message.edit(
            "❌ <b>UUID v7 requires Python 3.14+</b>\n\n"
            "Use <code>.uuid4</code> instead."
        )
        return

    await message.edit(
        f"🆔 <b>UUID v7</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"<code>{result}</code>"
    )
