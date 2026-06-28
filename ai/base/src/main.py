#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.


def _to_base(num: int, base: int, prefix: str = "") -> str:
    if num == 0:
        return prefix + "0"
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = ""
    n = abs(num)
    while n > 0:
        result = digits[n % base] + result
        n //= base
    return prefix + result


async def bin_cmd(self):
    """Convert decimal to binary - usage: .bin <number>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.bin <number></code>\n\n"
            "📝 <b>Example:</b> <code>.bin 42</code>"
        )
        return

    try:
        num = int(args[1])
        result = bin(num)

        await message.edit(
            f"💻 <b>Binary Conversion</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"🔢 <b>Decimal:</b> <code>{num}</code>\n"
            f"✅ <b>Binary:</b> <code>{result}</code>"
        )
    except ValueError:
        await message.edit("❌ <b>Please enter a valid integer!</b>")


async def oct_cmd(self):
    """Convert decimal to octal - usage: .oct <number>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.oct <number></code>\n\n"
            "📝 <b>Example:</b> <code>.oct 42</code>"
        )
        return

    try:
        num = int(args[1])
        result = oct(num)

        await message.edit(
            f"💻 <b>Octal Conversion</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"🔢 <b>Decimal:</b> <code>{num}</code>\n"
            f"✅ <b>Octal:</b> <code>{result}</code>"
        )
    except ValueError:
        await message.edit("❌ <b>Please enter a valid integer!</b>")


async def hex_cmd(self):
    """Convert decimal to hexadecimal - usage: .hex <number>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.hex <number></code>\n\n"
            "📝 <b>Example:</b> <code>.hex 42</code>"
        )
        return

    try:
        num = int(args[1])
        result = hex(num)

        await message.edit(
            f"💻 <b>Hexadecimal Conversion</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"🔢 <b>Decimal:</b> <code>{num}</code>\n"
            f"✅ <b>Hexadecimal:</b> <code>{result}</code>"
        )
    except ValueError:
        await message.edit("❌ <b>Please enter a valid integer!</b>")


async def base_cmd(self):
    """Convert between bases - usage: .base <base_from> <base_to> <value>

    Supported bases: 2-36
    """
    message = self.message
    args = message.text.split(maxsplit=3)

    if len(args) < 4:
        await message.edit(
            "❌ <b>Usage:</b> <code>.base <from> <to> <value></code>\n\n"
            "📝 <b>Examples:</b>\n"
            "• <code>.base 16 10 ff</code>\n"
            "• <code>.base 2 10 1010</code>\n"
            "• <code>.base 10 16 255</code>"
        )
        return

    try:
        base_from = int(args[1])
        base_to = int(args[2])
        value = args[3].strip()

        if base_from < 2 or base_from > 36 or base_to < 2 or base_to > 36:
            await message.edit("❌ <b>Bases must be between 2 and 36!</b>")
            return

        decimal = int(value, base_from)
        result = _to_base(decimal, base_to)

        await message.edit(
            f"💻 <b>Base Conversion</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"📝 <b>Input:</b> <code>{value}</code> (base {base_from})\n"
            f"✅ <b>Output:</b> <code>{result}</code> (base {base_to})\n"
            f"🔢 <b>Decimal:</b> <code>{decimal}</code>"
        )
    except ValueError:
        await message.edit(
            "❌ <b>Invalid input!</b>\n\n"
            "Make sure the value is valid for the source base."
        )
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")
