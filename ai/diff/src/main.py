#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

import difflib


async def diff_cmd(self):
    """Compare two texts - usage: .diff <text1> | <text2>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.diff <text1> | <text2></code>\n\n"
            "📝 <b>Example:</b> <code>.diff hello | hallo</code>"
        )
        return

    parts = args[1].split("|")
    if len(parts) != 2:
        await message.edit(
            "❌ <b>Use | to separate the two texts!</b>\n\n"
            "📝 <b>Example:</b> <code>.diff hello | hallo</code>"
        )
        return

    text1 = parts[0].strip()
    text2 = parts[1].strip()

    matcher = difflib.SequenceMatcher(None, text1, text2)
    similarity = matcher.ratio() * 100

    diff = list(difflib.unified_diff(
        text1.splitlines(keepends=True),
        text2.splitlines(keepends=True),
        n=0,
    ))

    diff_text = "".join(diff)
    if len(diff_text) > 3000:
        diff_text = diff_text[:2997] + "..."

    lines1 = text1.count("\n") + 1 if text1 else 0
    lines2 = text2.count("\n") + 1 if text2 else 0

    await message.edit(
        f"📊 <b>Text Diff</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📏 <b>Text 1:</b> <code>{len(text1)}</code> chars, "
        f"<code>{lines1}</code> lines\n"
        f"📏 <b>Text 2:</b> <code>{len(text2)}</code> chars, "
        f"<code>{lines2}</code> lines\n"
        f"🎯 <b>Similarity:</b> <code>{similarity:.1f}%</code>\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<code>{diff_text}</code>"
    )


async def closest_cmd(self):
    """Find closest matching word - usage: .closest <word> | <opt1> | <opt2> | ..."""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.closest <word> | <opt1> | <opt2> | ...</code>\n\n"
            "📝 <b>Example:</b> <code>.closest helo | hello | hallo | help</code>"
        )
        return

    parts = [p.strip() for p in args[1].split("|") if p.strip()]
    if len(parts) < 3:
        await message.edit("❌ <b>Provide a word and at least 2 options!</b>")
        return

    word = parts[0]
    options = parts[1:]

    closest = difflib.get_close_matches(word, options, n=5, cutoff=0.0)
    if not closest:
        await message.edit(f"❌ <b>No matches found for</b> <code>{word}</code>")
        return

    lines = []
    for match in closest:
        ratio = difflib.SequenceMatcher(None, word, match).ratio()
        lines.append(f"• <code>{match}</code> ({ratio:.0%} match)")

    await message.edit(
        f"🎯 <b>Closest Match</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"🔍 <b>Search:</b> <code>{word}</code>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        + "\n".join(lines)
    )
