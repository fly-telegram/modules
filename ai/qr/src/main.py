#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

import io


async def qr_cmd(self):
    """Generate QR code - usage: .qr <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.qr <text></code>\n\n"
            "📝 <b>Example:</b> <code>.qr https://example.com</code>"
        )
        return

    text = args[1]

    try:
        import qrcode
        from qrcode.image.pil import PilImage

        status = await message.edit("📱 <b>Generating QR code...</b>")

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        bio.name = "qr.png"
        bio.seek(0)

        await message.delete()
        await self.client.send_photo(
            chat_id=message.chat.id,
            photo=bio,
            caption=(
                f"📱 <b>QR Code</b>\n"
                f"━━━━━━━━━━━━━━━\n\n"
                f"📝 <b>Content:</b> <code>{text}</code>\n"
                f"📐 <b>Size:</b> <code>{img.width}x{img.height}</code>"
            ),
        )
    except ImportError:
        await status.edit(
            "❌ <b>qrcode library required!</b>\n\n"
            "Install: <code>pip install qrcode[pil]</code>"
        )
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")
