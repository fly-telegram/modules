#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

from pyrogram.types import User
from datetime import datetime


def get_user_status(status) -> str:
    """Convert user status to readable text"""
    if not status:
        return "Unknown"
    
    status_map = {
        "UserStatus.ONLINE": "🟢 Online",
        "UserStatus.OFFLINE": "🔴 Offline",
        "UserStatus.RECENTLY": "🟡 Recently",
        "UserStatus.LAST_WEEK": "🟠 Last week",
        "UserStatus.LAST_MONTH": "🟣 Last month",
        "UserStatus.LONG_AGO": "⚫ Long ago",
    }
    
    status_str = str(status)
    return status_map.get(status_str, status_str)


def get_user_photos_count(user: User) -> str:
    """Get user photos count"""
    if user.photo:
        return "Yes"
    return "No"


async def user_cmd(self):
    """Get information about user - reply to message or use without reply"""
    message = self.message
    
    # Check if replying to message
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
    else:
        user = message.from_user
    
    # Get user info
    user_id = user.id
    first_name = user.first_name or "Not specified"
    last_name = user.last_name or ""
    username = f"@{user.username}" if user.username else "Not specified"
    language = user.language_code or "Not specified"
    status = get_user_status(user.status)
    premium = "⭐ Yes" if user.is_premium else "No"
    verified = "✅ Yes" if user.is_verified else "No"
    bot = "🤖 Yes" if user.is_bot else "No"
    scam = "⚠️ Yes" if user.is_scam else "No"
    fake = "⚠️ Yes" if user.is_fake else "No"
    support = "🛡️ Yes" if user.is_support else "No"
    restricted = "🚫 Yes" if user.is_restricted else "No"
    photo = get_user_photos_count(user)
    
    # Get profile photos count
    try:
        photos = await self.client.get_chat_photos_count(user.id)
    except:
        photos = 0
    
    # Format user info
    full_name = f"{first_name} {last_name}".strip()
    
    text = (
        f"👤 <b>User Information</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📛 <b>Name:</b> <code>{full_name}</code>\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        f"📱 <b>Username:</b> <code>{username}</code>\n"
        f"🌐 <b>Language:</b> <code>{language}</code>\n"
        f"📊 <b>Status:</b> {status}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⭐ <b>Premium:</b> {premium}\n"
        f"✅ <b>Verified:</b> {verified}\n"
        f"🤖 <b>Bot:</b> {bot}\n"
        f"🛡️ <b>Support:</b> {support}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⚠️ <b>Scam:</b> {scam}\n"
        f"⚠️ <b>Fake:</b> {fake}\n"
        f"🚫 <b>Restricted:</b> {restricted}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🖼️ <b>Profile photos:</b> <code>{photos}</code>\n"
    )
    
    await message.edit(text)


async def id_cmd(self):
    """Get user ID - quick command"""
    message = self.message
    
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
        text = f"🆔 <b>User ID:</b> <code>{user.id}</code>"
    else:
        user = message.from_user
        text = f"🆔 <b>Your ID:</b> <code>{user.id}</code>"
    
    await message.edit(text)