#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

from datetime import datetime

todos_db = {}


async def todo_cmd(self):
    """Manage todos - usage: .todo [action] [args]

    Actions: add, done, list, clear
    """
    message = self.message
    user_id = message.from_user.id
    args = message.text.split(maxsplit=2)

    if user_id not in todos_db:
        todos_db[user_id] = []

    if len(args) < 2:
        return await _list_todos(message, user_id)

    action = args[1].lower()

    if action == "add":
        if len(args) < 3:
            await message.edit(
                "❌ <b>Usage:</b> <code>.todo add <task></code>\n\n"
                "📝 <b>Example:</b> <code>.todo add Buy groceries</code>"
            )
            return

        task = args[2]
        todos_db[user_id].append(
            {"task": task, "done": False, "created": datetime.now()})
        await _list_todos(message, user_id)

    elif action == "done":
        if len(args) < 3:
            await message.edit(
                "❌ <b>Usage:</b> <code>.todo done <number></code>\n\n"
                "📝 <b>Example:</b> <code>.todo done 1</code>"
            )
            return

        try:
            idx = int(args[2]) - 1
            if 0 <= idx < len(todos_db[user_id]):
                todos_db[user_id][idx]["done"] = True
                await _list_todos(message, user_id)
            else:
                await message.edit(f"❌ <b>Invalid number!</b> You have {len(todos_db[user_id])} todos.")
        except ValueError:
            await message.edit("❌ <b>Number required!</b>")

    elif action == "clear":
        todos_db[user_id] = []
        await message.edit("🗑️ <b>All todos cleared!</b>")

    elif action == "list":
        await _list_todos(message, user_id)

    else:
        await message.edit(
            "❌ <b>Unknown action!</b>\n\n"
            "📋 <b>Actions:</b> <code>add</code>, <code>done</code>, <code>list</code>, <code>clear</code>"
        )


async def _list_todos(message, user_id):
    todos = todos_db.get(user_id, [])

    if not todos:
        await message.edit("📭 <b>No todos!</b> Use <code>.todo add <task></code> to add one.")
        return

    lines = []
    for i, t in enumerate(todos, 1):
        status = "✅" if t["done"] else "⬜"
        task_text = t["task"][:50] + ("..." if len(t["task"]) > 50 else "")
        lines.append(f"{status} <b>{i}.</b> <code>{task_text}</code>")

    done_count = sum(1 for t in todos if t["done"])
    total = len(todos)

    await message.edit(
        f"📋 <b>Todo List</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        + "\n".join(lines) +
        f"\n\n━━━━━━━━━━━━━━━\n"
        f"📊 <b>{done_count}/{total}</b> completed"
    )
