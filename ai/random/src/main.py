#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

import random
import secrets


async def pick_cmd(self):
    """Pick a random item - usage: .pick <item1> | <item2> | ..."""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.pick <item1> | <item2> | ...</code>\n\n"
            "📝 <b>Example:</b> <code>.pick pizza | sushi | tacos</code>"
        )
        return

    items = [i.strip() for i in args[1].split("|") if i.strip()]

    if len(items) < 2:
        await message.edit("❌ <b>Please provide at least 2 items separated by |</b>")
        return

    chosen = secrets.choice(items)

    items_list = "\n".join(f"• {i}" for i in items)

    await message.edit(
        f"🎯 <b>Random Pick</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📋 <b>Options:</b>\n{items_list}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"✅ <b>Chosen:</b> <b>{chosen}</b>"
    )


async def choose_cmd(self):
    """Choose yes/no/maybe - usage: .choose <question>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.choose <question></code>\n\n"
            "📝 <b>Example:</b> <code>.choose Should I go out today?</code>"
        )
        return

    question = args[1]
    answers = [
        "Yes ✅", "No ❌", "Maybe 🤔", "Definitely! 💯",
        "Absolutely not 🚫", "Ask again later 🔮",
        "I wouldn't count on it 😬", "It is certain ✨",
        "Better not tell you now 🤐", "Yes, do it! 🎯",
        "No way! 😤", "Of course! 👍", "Never! 👎",
        "Go for it! 🚀", "Think twice 🤨",
    ]

    answer = secrets.choice(answers)

    await message.edit(
        f"🔮 <b>Magic 8-Ball</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"❓ <b>Question:</b> <code>{question}</code>\n\n"
        f"🎱 <b>Answer:</b> <b>{answer}</b>"
    )


async def team_cmd(self):
    """Split into teams - usage: .team <num_teams> <item1> | <item2> | ..."""
    message = self.message
    args = message.text.split(maxsplit=2)

    if len(args) < 3:
        await message.edit(
            "❌ <b>Usage:</b> <code>.team <num> <item1> | <item2> | ...</code>\n\n"
            "📝 <b>Example:</b> <code>.team 2 Alice | Bob | Charlie | Dave</code>"
        )
        return

    try:
        num_teams = int(args[1])
    except ValueError:
        await message.edit("❌ <b>Number of teams must be a valid integer!</b>")
        return

    if num_teams < 2 or num_teams > 10:
        await message.edit("❌ <b>Number of teams must be between 2 and 10!</b>")
        return

    items = [i.strip() for i in args[2].split("|") if i.strip()]

    if len(items) < num_teams:
        await message.edit(
            f"❌ <b>Not enough items!</b> Need at least {num_teams}, got {len(items)}."
        )
        return

    random.shuffle(items)
    teams = [[] for _ in range(num_teams)]

    for i, item in enumerate(items):
        teams[i % num_teams].append(item)

    result_lines = []
    for idx, team in enumerate(teams, 1):
        members = "\n".join(f"  • {m}" for m in team)
        result_lines.append(f"<b>Team {idx}</b> ({len(team)}):\n{members}")

    await message.edit(
        "👥 <b>Team Splitter</b>\n"
        "━━━━━━━━━━━━━━━\n\n"
        + "\n\n".join(result_lines)
    )


async def shuffle_cmd(self):
    """Shuffle items - usage: .shuffle <item1> | <item2> | ..."""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.shuffle <item1> | <item2> | ...</code>\n\n"
            "📝 <b>Example:</b> <code>.shuffle A | B | C | D</code>"
        )
        return

    items = [i.strip() for i in args[1].split("|") if i.strip()]

    if len(items) < 2:
        await message.edit("❌ <b>Please provide at least 2 items!</b>")
        return

    random.shuffle(items)
    result = "\n".join(f"• {i}" for i in items)

    await message.edit(
        f"🔀 <b>Shuffled</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{result}"
    )


async def coin_cmd(self):
    """Flip a coin - usage: .coin"""
    message = self.message
    result = secrets.choice(["Heads", "Tails"])

    await message.edit(
        f"🪙 <b>Coin Flip</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"Result: <b>{result}</b>"
    )
