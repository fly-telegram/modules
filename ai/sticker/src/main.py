#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

import io
from PIL import Image


async def sticker_cmd(self):
    """Convert photo to sticker - reply to photo with .sticker"""
    message = self.message

    # Check if replying to photo or sticker
    if not message.reply_to_message:
        await message.edit("❌ <b>Reply to a photo or sticker!</b>")
        return

    reply = message.reply_to_message

    if not reply.photo and not reply.sticker:
        await message.edit("❌ <b>Reply to a photo or sticker!</b>")
        return

    try:
        await message.edit("⏳ Converting to sticker...")

        # Download media
        file_path = await self.client.download_media(reply)

        if reply.sticker:
            # Already a sticker, just send it
            await message.delete()
            await self.client.send_sticker(
                chat_id=message.chat.id,
                sticker=file_path
            )
            return

        # Convert photo to sticker (512x512)
        img = Image.open(file_path)

        # Resize to fit 512x512 (Telegram sticker size)
        width, height = img.size

        if width > height:
            new_width = 512
            new_height = int(height * (512 / width))
        else:
            new_height = 512
            new_width = int(width * (512 / height))

        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Convert to RGBA if needed
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        # Save to bytes
        bio = io.BytesIO()
        img.save(bio, format="WEBP")
        bio.name = "sticker.webp"
        bio.seek(0)

        # Send sticker
        await message.delete()
        await self.client.send_sticker(
            chat_id=message.chat.id,
            sticker=bio
        )

    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def emoj_cmd(self):
    """Get emoji info - usage: .emoj <emoji>"""
    message = self.message

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.emoj <emoji></code>\n\n"
            "📝 <b>Example:</b> <code>.emoj 😀</code>"
        )
        return

    emoji = args[1]

    try:
        # Get emoji code points
        code_points = " ".join(f"U+{ord(c):04X}" for c in emoji)

        # Get emoji name (basic)
        import unicodedata
        names = []
        for char in emoji:
            try:
                name = unicodedata.name(char, "Unknown")
                names.append(name)
            except:
                names.append("Unknown")

        text = (
            f"😀 <b>Emoji Info</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"📝 <b>Emoji:</b> <code>{emoji}</code>\n"
            f"🔢 <b>Code points:</b> <code>{code_points}</code>\n"
            f"📛 <b>Name:</b> <code>{', '.join(names)}</code>\n"
            f"📏 <b>Length:</b> <code>{len(emoji)}</code> characters\n"
        )

        await message.edit(text)
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def copy_cmd(self):
    """Copy sticker as photo - reply to sticker with .copy"""
    message = self.message

    if not message.reply_to_message or not message.reply_to_message.sticker:
        await message.edit("❌ <b>Reply to a sticker!</b>")
        return

    try:
        await message.edit("⏳ Converting sticker to photo...")

        # Download sticker
        file_path = await self.client.download_media(message.reply_to_message.sticker)

        # Convert to photo
        img = Image.open(file_path)

        # Convert to RGB if needed
        if img.mode == "RGBA":
            # Create white background
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # Save to bytes
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        bio.name = "photo.png"
        bio.seek(0)

        # Send photo
        await message.delete()
        await self.client.send_photo(
            chat_id=message.chat.id,
            photo=bio,
            caption="📸 <b>Sticker converted to photo</b>"
        )

    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")
