#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

import io
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode


async def qr_cmd(self):
    """Generate QR code from text - usage: .qr <text>"""
    message = self.message
    
    # Get text from message
    text = message.text.split(maxsplit=1)
    
    if len(text) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.qr <text></code>\n\n"
            "📝 <b>Example:</b> <code>.qr Hello World</code>"
        )
        return
    
    qr_text = text[1]
    
    # Generate QR code
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_text)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to bytes
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        bio.name = "qrcode.png"
        bio.seek(0)
        
        # Send as photo
        await message.delete()
        await self.client.send_photo(
            chat_id=message.chat.id,
            photo=bio,
            caption=f"📱 <b>QR Code for:</b> <code>{qr_text}</code>"
        )
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def qr_read_cmd(self):
    """Read QR code from photo - reply to photo with .qrread"""
    message = self.message
    
    # Check if replying to photo
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.edit(
            "❌ <b>Reply to a photo with QR code!</b>\n\n"
            "📝 <b>Usage:</b> Reply to photo with <code>.qrread</code>"
        )
        return
    
    try:
        # Download photo
        await message.edit("📥 Downloading photo...")
        photo_path = await self.client.download_media(message.reply_to_message.photo)
        
        
        img = Image.open(photo_path)
        decoded = decode(img)
        
        if decoded:
            results = []
            for obj in decoded:
                data = obj.data.decode("utf-8")
                results.append(f"• <code>{data}</code>")
            
            text = (
                f"📱 <b>QR Code Content</b>\n"
                f"━━━━━━━━━━━━━━━\n\n"
                + "\n".join(results)
            )
            await message.edit(text)
        else:
            await message.edit("❌ <b>No QR code found in image!</b>")
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")