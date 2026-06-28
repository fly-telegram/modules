#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

# Simple in-memory notes storage
# Structure: {user_id: {note_name: note_content}}
notes_db = {}


async def save_cmd(self):
    """Save a note - usage: .save <name> <text>"""
    message = self.message
    user_id = message.from_user.id

    # Parse command
    args = message.text.split(maxsplit=2)

    if len(args) < 3:
        await message.edit(
            "❌ <b>Usage:</b> <code>.save <name> <text></code>\n\n"
            "📝 <b>Example:</b> <code>.save todo Buy milk</code>"
        )
        return

    note_name = args[1].lower()
    note_content = args[2]

    # Initialize user notes if not exists
    if user_id not in notes_db:
        notes_db[user_id] = {}

    # Save note
    notes_db[user_id][note_name] = note_content

    await message.edit(
        f"✅ <b>Note saved!</b>\n\n"
        f"📝 <b>Name:</b> <code>{note_name}</code>\n"
        f"📄 <b>Content:</b> <code>{note_content}</code>"
    )


async def get_cmd(self):
    """Get a note - usage: .get <name>"""
    message = self.message
    user_id = message.from_user.id

    # Parse command
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.get <name></code>\n\n"
            "📝 <b>Example:</b> <code>.get todo</code>"
        )
        return

    note_name = args[1].lower()

    # Check if note exists
    if user_id not in notes_db or note_name not in notes_db[user_id]:
        await message.edit(f"❌ <b>Note</b> <code>{note_name}</code> <b>not found!</b>")
        return

    note_content = notes_db[user_id][note_name]

    await message.edit(
        f"📝 <b>Note:</b> <code>{note_name}</code>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{note_content}"
    )


async def notes_cmd(self):
    """List all saved notes"""
    message = self.message
    user_id = message.from_user.id

    # Check if user has notes
    if user_id not in notes_db or not notes_db[user_id]:
        await message.edit("📭 <b>You have no saved notes!</b>")
        return

    # Build notes list
    notes_list = []
    for name, content in notes_db[user_id].items():
        # Truncate long content
        preview = content[:50] + "..." if len(content) > 50 else content
        notes_list.append(f"• <code>{name}</code>: {preview}")

    text = (
        "📝 <b>Your Notes</b>\n"
        "━━━━━━━━━━━━━━━\n\n"
        + "\n".join(notes_list)
        + "\n\n━━━━━━━━━━━━━━━\n"
        + f"📊 <b>Total:</b> <code>{len(notes_db[user_id])}</code>"
    )

    await message.edit(text)


async def clear_cmd(self):
    """Delete a note - usage: .clear <name>"""
    message = self.message
    user_id = message.from_user.id

    # Parse command
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.clear <name></code>\n\n"
            "📝 <b>Example:</b> <code>.clear todo</code>"
        )
        return

    note_name = args[1].lower()

    # Check if note exists
    if user_id not in notes_db or note_name not in notes_db[user_id]:
        await message.edit(f"❌ <b>Note</b> <code>{note_name}</code> <b>not found!</b>")
        return

    # Delete note
    del notes_db[user_id][note_name]

    await message.edit(f"🗑️ <b>Note</b> <code>{note_name}</code> <b>deleted!</b>")


async def clearall_cmd(self):
    """Delete all notes"""
    message = self.message
    user_id = message.from_user.id

    if user_id in notes_db:
        count = len(notes_db[user_id])
        notes_db[user_id] = {}
        await message.edit(f"🗑️ <b>Deleted {count} notes!</b>")
    else:
        await message.edit("📭 <b>You have no notes!</b>")
