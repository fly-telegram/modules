#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

import colorsys
import random


def _rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"


def _hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


async def randomcolor_cmd(self):
    """Generate a random color - usage: .randomcolor"""
    message = self.message

    r, g, b = random.randint(0, 255), random.randint(
        0, 255), random.randint(0, 255)
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    hex_val = _rgb_to_hex(r, g, b)

    await message.edit(
        f"🎨 <b>Random Color</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"🟥 <b>RGB:</b> <code>({r}, {g}, {b})</code>\n"
        f"#️⃣ <b>HEX:</b> <code>{hex_val}</code>\n"
        f"🎨 <b>HSL:</b> <code>({h * 360:.0f}°, {s * 100:.0f}%, {l * 100:.0f}%)</code>"
    )


async def hex2rgb_cmd(self):
    """Convert HEX to RGB - usage: .hex2rgb <#hex>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.hex2rgb <#hex></code>\n\n"
            "📝 <b>Example:</b> <code>.hex2rgb #ff0000</code>"
        )
        return

    hex_val = args[1].strip()

    try:
        r, g, b = _hex_to_rgb(hex_val)
        await message.edit(
            f"🎨 <b>HEX to RGB</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"#️⃣ <b>HEX:</b> <code>{hex_val}</code>\n"
            f"🟥 <b>RGB:</b> <code>({r}, {g}, {b})</code>"
        )
    except (ValueError, IndexError):
        await message.edit(
            "❌ <b>Invalid hex color!</b>\n\n"
            "📝 <b>Example:</b> <code>.hex2rgb #ff0000</code>"
        )


async def rgb2hex_cmd(self):
    """Convert RGB to HEX - usage: .rgb2hex <r> <g> <b>"""
    message = self.message
    args = message.text.split()

    if len(args) < 4:
        await message.edit(
            "❌ <b>Usage:</b> <code>.rgb2hex <r> <g> <b></code>\n\n"
            "📝 <b>Example:</b> <code>.rgb2hex 255 0 0</code>"
        )
        return

    try:
        r, g, b = int(args[1]), int(args[2]), int(args[3])
        hex_val = _rgb_to_hex(r, g, b)

        await message.edit(
            f"🎨 <b>RGB to HEX</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"🟥 <b>RGB:</b> <code>({r}, {g}, {b})</code>\n"
            f"#️⃣ <b>HEX:</b> <code>{hex_val}</code>"
        )
    except ValueError:
        await message.edit("❌ <b>RGB values must be integers 0-255!</b>")
