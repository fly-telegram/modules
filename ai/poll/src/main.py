#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

async def poll_cmd(self):
    """Create a poll \u2014 usage: .poll <question> | <option1> | <option2> | ...

    Max 10 options. Use "|" as separator.
    """
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "\u274c <b>Usage:</b> <code>.poll <question> | <opt1> | <opt2> | ...</code>\n\n"
            "\U0001f4dd <b>Example:</b> <code>.poll Best language? | Python | JS | Rust | C++</code>\n\n"
            "\u26a0\ufe0f Max 10 options. Use <code>|</code> as separator."
        )
        return

    parts = [p.strip() for p in args[1].split("|")]

    if len(parts) < 3:
        await message.edit(
            "\u274c <b>Need at least 2 options!</b>\n\n"
            "\U0001f4dd <b>Example:</b> <code>.poll Yes or No? | Yes | No</code>"
        )
        return

    if len(parts) > 11:
        await message.edit("\u274c <b>Maximum 10 options allowed!</b>")
        return

    question = parts[0]
    options = parts[1:]

    # Validate option lengths (max 100 chars each)
    for i, opt in enumerate(options):
        if len(opt) > 100:
            options[i] = opt[:97] + "..."
        if not opt:
            options[i] = f"Option {i+1}"

    try:
        await self.client.send_poll(
            chat_id=message.chat.id,
            question=question,
            options=options,
            is_anonymous=True,
        )
        await message.delete()
    except Exception as e:
        await message.edit(f"\u274c <b>Error:</b> <code>{e}</code>")


async def quiz_cmd(self):
    """Create a quiz \u2014 usage: .quiz <question> | <opt1> | <opt2> | ... | <correct_index>

    Correct index is 1-based number of the right answer.
    """
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "\u274c <b>Usage:</b> <code>.quiz <question> | <opt1> | <opt2> | <correct></code>\n\n"
            "\U0001f4dd <b>Example:</b> <code>.quiz 2+2? | 3 | 4 | 5 | 2</code>\n\n"
            "\u26a0\ufe0f Last number = correct option index (1-based)."
        )
        return

    parts = [p.strip() for p in args[1].split("|")]

    if len(parts) < 4:
        await message.edit(
            "\u274c <b>Need at least 2 options + correct index!</b>\n\n"
            "\U0001f4dd <b>Example:</b> <code>.quiz 2+2? | 3 | 4 | 5 | 2</code>"
        )
        return

    # Last part should be the correct index
    try:
        correct_index = int(parts[-1]) - 1  # convert to 0-based
        if correct_index < 0 or correct_index > len(parts) - 2:
            await message.edit("\u274c <b>Correct index is out of range!</b>")
            return
    except ValueError:
        await message.edit(
            "\u274c <b>Last value must be the correct option number!</b>\n\n"
            "\U0001f4dd <b>Example:</b> <code>.quiz 2+2? | 3 | 4 | 5 | 2</code>"
        )
        return

    question = parts[0]
    options = parts[1:-1]

    for i, opt in enumerate(options):
        if len(opt) > 100:
            options[i] = opt[:97] + "..."
        if not opt:
            options[i] = f"Option {i+1}"

    try:
        await self.client.send_poll(
            chat_id=message.chat.id,
            question=question,
            options=options,
            is_anonymous=True,
            type="quiz",
            correct_option_id=correct_index,
        )
        await message.delete()
    except Exception as e:
        await message.edit(f"\u274c <b>Error:</b> <code>{e}</code>")


async def stoppoll_cmd(self):
    """Stop a poll \u2014 reply to poll message with .stoppoll"""
    message = self.message

    if not message.reply_to_message:
        await message.edit("\u274c <b>Reply to a poll message!</b>")
        return

    if not message.reply_to_message.poll:
        await message.edit("\u274c <b>Replied message is not a poll!</b>")
        return

    try:
        await self.client.stop_poll(
            chat_id=message.chat.id,
            message_id=message.reply_to_message.id
        )
        await message.delete()
    except Exception as e:
        await message.edit(f"\u274c <b>Error:</b> <code>{e}</code>")


async def vote_cmd(self):
    """Vote in a poll \u2014 reply to poll with .vote <option_number>"""
    message = self.message
    args = message.text.split()

    if not message.reply_to_message or not message.reply_to_message.poll:
        await message.edit("\u274c <b>Reply to a poll message!</b>")
        return

    if len(args) < 2:
        poll = message.reply_to_message.poll
        opts = "\n".join(f"{i+1}. <code>{opt.text}</code>" for i, opt in enumerate(poll.options))
        await message.edit(
            f"\U0001f4ca <b>Poll:</b> <code>{poll.question}</code>\n\n"
            f"{opts}\n\n"
            f"\U0001f4dd <b>Vote:</b> <code>.vote <number></code>"
        )
        return

    try:
        option = int(args[1]) - 1
    except ValueError:
        await message.edit("\u274c <b>Option must be a number!</b>")
        return

    try:
        await self.client.vote_poll(
            chat_id=message.chat.id,
            message_id=message.reply_to_message.id,
            option=option
        )
        await message.edit("\u2705 <b>Voted!</b>")
    except Exception as e:
        await message.edit(f"\u274c <b>Error:</b> <code>{e}</code>")
