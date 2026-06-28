#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.


async def ban_cmd(self):
    """Ban user - reply to message with .ban [reason]"""
    message = self.message

    if not message.reply_to_message:
        await message.edit("❌ <b>Reply to user message!</b>")
        return

    user = message.reply_to_message.from_user
    args = message.text.split(maxsplit=1)
    reason = args[1] if len(args) > 1 else "No reason"

    try:
        await self.client.ban_chat_member(
            chat_id=message.chat.id,
            user_id=user.id
        )
        await message.edit(
            f"🔨 <b>User banned!</b>\n\n"
            f"👤 <b>User:</b> <code>{user.first_name}</code>\n"
            f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
            f"📝 <b>Reason:</b> <code>{reason}</code>"
        )
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def unban_cmd(self):
    """Unban user - reply to message with .unban"""
    message = self.message

    if not message.reply_to_message:
        await message.edit("❌ <b>Reply to user message!</b>")
        return

    user = message.reply_to_message.from_user

    try:
        await self.client.unban_chat_member(
            chat_id=message.chat.id,
            user_id=user.id
        )
        await message.edit(
            f"✅ <b>User unbanned!</b>\n\n"
            f"👤 <b>User:</b> <code>{user.first_name}</code>\n"
            f"🆔 <b>ID:</b> <code>{user.id}</code>"
        )
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def mute_cmd(self):
    """Mute user - reply to message with .mute [duration]

    Duration: 10s, 5m, 2h, 1d (default: permanent)
    """
    message = self.message

    if not message.reply_to_message:
        await message.edit("❌ <b>Reply to user message!</b>")
        return

    user = message.reply_to_message.from_user
    args = message.text.split(maxsplit=1)

    # Parse duration
    from datetime import datetime, timedelta

    until_date = None
    duration_str = "Permanent"

    if len(args) > 1:
        time_str = args[1].lower().strip()
        seconds = 0

        if time_str.endswith("s"):
            seconds = int(time_str[:-1])
        elif time_str.endswith("m"):
            seconds = int(time_str[:-1]) * 60
        elif time_str.endswith("h"):
            seconds = int(time_str[:-1]) * 3600
        elif time_str.endswith("d"):
            seconds = int(time_str[:-1]) * 86400
        else:
            seconds = int(time_str)

        if seconds > 0:
            until_date = datetime.now() + timedelta(seconds=seconds)
            duration_str = time_str

    try:
        from pyrogram.types import ChatPermissions

        await self.client.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user.id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
            ),
            until_date=until_date
        )

        await message.edit(
            f"🔇 <b>User muted!</b>\n\n"
            f"👤 <b>User:</b> <code>{user.first_name}</code>\n"
            f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
            f"⏰ <b>Duration:</b> <code>{duration_str}</code>"
        )
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def unmute_cmd(self):
    """Unmute user - reply to message with .unmute"""
    message = self.message

    if not message.reply_to_message:
        await message.edit("❌ <b>Reply to user message!</b>")
        return

    user = message.reply_to_message.from_user

    try:
        from pyrogram.types import ChatPermissions

        await self.client.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            )
        )

        await message.edit(
            f"🔊 <b>User unmuted!</b>\n\n"
            f"👤 <b>User:</b> <code>{user.first_name}</code>\n"
            f"🆔 <b>ID:</b> <code>{user.id}</code>"
        )
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def kick_cmd(self):
    """Kick user (ban + unban) - reply to message with .kick [reason]"""
    message = self.message

    if not message.reply_to_message:
        await message.edit("❌ <b>Reply to user message!</b>")
        return

    user = message.reply_to_message.from_user
    args = message.text.split(maxsplit=1)
    reason = args[1] if len(args) > 1 else "No reason"

    try:
        # Ban then unban to kick
        await self.client.ban_chat_member(
            chat_id=message.chat.id,
            user_id=user.id
        )
        await self.client.unban_chat_member(
            chat_id=message.chat.id,
            user_id=user.id
        )

        await message.edit(
            f"👢 <b>User kicked!</b>\n\n"
            f"👤 <b>User:</b> <code>{user.first_name}</code>\n"
            f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
            f"📝 <b>Reason:</b> <code>{reason}</code>"
        )
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def pin_cmd(self):
    """Pin message - reply to message with .pin"""
    message = self.message

    if not message.reply_to_message:
        await message.edit("❌ <b>Reply to message to pin!</b>")
        return

    try:
        await self.client.pin_chat_message(
            chat_id=message.chat.id,
            message_id=message.reply_to_message.id
        )
        await message.edit("📌 <b>Message pinned!</b>")
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def unpin_cmd(self):
    """Unpin message - reply to message with .unpin"""
    message = self.message

    if not message.reply_to_message:
        await message.edit("❌ <b>Reply to message to unpin!</b>")
        return

    try:
        await self.client.unpin_chat_message(
            chat_id=message.chat.id,
            message_id=message.reply_to_message.id
        )
        await message.edit("📌 <b>Message unpinned!</b>")
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def purge_cmd(self):
    """Delete multiple messages - reply to message with .purge"""
    message = self.message

    if not message.reply_to_message:
        await message.edit("❌ <b>Reply to first message to purge!</b>")
        return

    try:
        start_id = message.reply_to_message.id
        end_id = message.id

        deleted = 0
        for msg_id in range(start_id, end_id + 1):
            try:
                await self.client.delete_messages(
                    chat_id=message.chat.id,
                    message_ids=msg_id
                )
                deleted += 1
            except:
                pass

        await message.edit(f"🗑️ <b>Purged {deleted} messages!</b>")
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def settitle_cmd(self):
    """Set chat title - usage: .settitle <title>"""
    message = self.message

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.settitle <title></code>"
        )
        return

    title = args[1]

    try:
        await self.client.set_chat_title(
            chat_id=message.chat.id,
            title=title
        )
        await message.edit(f"✅ <b>Chat title changed to:</b> <code>{title}</code>")
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def setdesc_cmd(self):
    """Set chat description - usage: .setdesc <description>"""
    message = self.message

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.setdesc <description></code>"
        )
        return

    desc = args[1]

    try:
        await self.client.set_chat_description(
            chat_id=message.chat.id,
            description=desc
        )
        await message.edit("✅ <b>Chat description updated!</b>")
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")
