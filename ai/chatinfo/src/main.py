#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

from pyrogram.types import Chat


def get_chat_type(chat: Chat) -> str:
    """Convert chat type to readable text"""
    type_map = {
        "ChatType.PRIVATE": "👤 Private",
        "ChatType.BOT": "🤖 Bot",
        "ChatType.GROUP": "👥 Group",
        "ChatType.SUPERGROUP": "👥 Supergroup",
        "ChatType.CHANNEL": "📢 Channel",
    }
    
    chat_type = str(chat.type)
    return type_map.get(chat_type, chat_type)


async def chat_cmd(self):
    """Get information about current chat"""
    message = self.message
    chat = message.chat
    
    # Get basic info
    chat_id = chat.id
    title = chat.title or "Not specified"
    chat_type = get_chat_type(chat)
    username = f"@{chat.username}" if chat.username else "Not specified"
    description = chat.description or "Not specified"
    
    # Get members count
    try:
        members_count = await self.client.get_chat_members_count(chat.id)
    except:
        members_count = "Unknown"
    
    # Get admins count
    try:
        admins = []
        async for member in self.client.get_chat_members(chat.id, filter="ChatMembersFilter.ADMINISTRATORS"):
            admins.append(member)
        admins_count = len(admins)
    except:
        admins_count = "Unknown"
    
    # Get online count (only for groups)
    try:
        online_count = 0
        async for member in self.client.get_chat_members(chat.id, filter="ChatMembersFilter.ONLINE"):
            online_count += 1
    except:
        online_count = "Unknown"
    
    # Get chat photo info
    if chat.photo:
        photo = "Yes"
    else:
        photo = "No"
    
    # Get protected content info
    protected = "🔒 Yes" if chat.has_protected_content else "No"
    
    # Get chat info
    text = (
        f"💬 <b>Chat Information</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📛 <b>Title:</b> <code>{title}</code>\n"
        f"🆔 <b>ID:</b> <code>{chat_id}</code>\n"
        f"📱 <b>Username:</b> <code>{username}</code>\n"
        f"📋 <b>Type:</b> {chat_type}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📝 <b>Description:</b>\n<code>{description}</code>\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👥 <b>Members:</b> <code>{members_count}</code>\n"
        f"👑 <b>Admins:</b> <code>{admins_count}</code>\n"
        f"🟢 <b>Online:</b> <code>{online_count}</code>\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🖼️ <b>Photo:</b> {photo}\n"
        f"🔒 <b>Protected:</b> {protected}\n"
    )
    
    await message.edit(text)


async def members_cmd(self):
    """Get members count in chat"""
    message = self.message
    chat = message.chat
    
    try:
        count = await self.client.get_chat_members_count(chat.id)
        await message.edit(f"👥 <b>Members count:</b> <code>{count}</code>")
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def admins_cmd(self):
    """Get admins list in chat"""
    message = self.message
    chat = message.chat
    
    try:
        admins = []
        async for member in self.client.get_chat_members(chat.id, filter="ChatMembersFilter.ADMINISTRATORS"):
            user = member.user
            name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            username = f"@{user.username}" if user.username else "No username"
            admins.append(f"• {name} ({username}) - <code>{user.id}</code>")
        
        admin_list = "\n".join(admins) if admins else "No admins found"
        
        text = (
            f"👑 <b>Admins List</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"{admin_list}\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📊 <b>Total:</b> <code>{len(admins)}</code>"
        )
        
        await message.edit(text)
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")