#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.


async def bold_cmd(self):
    """Format text as bold - usage: .bold <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.bold <text></code>\n\n"
            "📝 <b>Example:</b> <code>.bold Hello World</code>"
        )
        return

    text = args[1]
    await message.edit(
        f"<b>Bold Text</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"<b>{text}</b>"
    )


async def italic_cmd(self):
    """Format text as italic - usage: .italic <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.italic <text></code>\n\n"
            "📝 <b>Example:</b> <code>.italic Hello World</code>"
        )
        return

    text = args[1]
    await message.edit(
        f"<i>Italic Text</i>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"<i>{text}</i>"
    )


async def mono_cmd(self):
    """Format text as monospace - usage: .mono <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.mono <text></code>\n\n"
            "📝 <b>Example:</b> <code>.mono print('hello')</code>"
        )
        return

    text = args[1]
    await message.edit(
        f"<code>Monospace Text</code>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"<code>{text}</code>"
    )


async def strike_cmd(self):
    """Format text as strikethrough - usage: .strike <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.strike <text></code>\n\n"
            "📝 <b>Example:</b> <code>.strike deleted content</code>"
        )
        return

    text = args[1]
    await message.edit(
        f"<s>Strikethrough</s>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"<s>{text}</s>"
    )


async def underline_cmd(self):
    """Format text as underlined - usage: .underline <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.underline <text></code>\n\n"
            "📝 <b>Example:</b> <code>.underline important text</code>"
        )
        return

    text = args[1]
    await message.edit(
        f"<u>Underlined Text</u>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"<u>{text}</u>"
    )


async def quote_cmd(self):
    """Format text as a blockquote - usage: .quote <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.quote <text></code>\n\n"
            "📝 <b>Example:</b> <code>.quote To be or not to be</code>"
        )
        return

    text = args[1]
    await message.edit(
        f"💬 <b>Quote</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"<blockquote>{text}</blockquote>"
    )
