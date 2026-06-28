#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

from collections import Counter


async def count_cmd(self):
    """Count characters, words, lines, bytes - usage: .count <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.count <text></code>\n\n"
            "📝 <b>Example:</b> <code>.count Hello world, how are you?</code>"
        )
        return

    text = args[1]
    chars = len(text)
    chars_no_space = len(text.replace(" ", ""))
    words = len(text.split())
    lines = len(text.splitlines())
    bytes_len = len(text.encode("utf-8"))

    preview = text[:100] + ("..." if len(text) > 100 else "")

    await message.edit(
        f"📊 <b>Text Statistics</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Text:</b> <code>{preview}</code>\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🔤 <b>Characters:</b> <code>{chars}</code>\n"
        f"🔤 <b>No spaces:</b> <code>{chars_no_space}</code>\n"
        f"📖 <b>Words:</b> <code>{words}</code>\n"
        f"📄 <b>Lines:</b> <code>{lines}</code>\n"
        f"💾 <b>Bytes (UTF-8):</b> <code>{bytes_len}</code>"
    )


async def freq_cmd(self):
    """Show letter frequency - usage: .freq <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.freq <text></code>\n\n"
            "📝 <b>Example:</b> <code>.freq Hello world</code>"
        )
        return

    text = args[1].lower()
    letters = [c for c in text if c.isalpha()]

    if not letters:
        await message.edit("❌ <b>No letters found in the text!</b>")
        return

    freq = Counter(letters)
    total = len(letters)
    sorted_freq = freq.most_common()

    lines = []
    for char, count in sorted_freq:
        pct = (count / total) * 100
        bar = "█" * int(pct / 2) + "░" * max(0, 50 - int(pct / 2))
        lines.append(f"<code>{char}</code> {bar} {count} ({pct:.1f}%)")

    await message.edit(
        f"📊 <b>Letter Frequency</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Source:</b> {total} letters\n\n"
        + "\n".join(lines)
    )


async def wordfreq_cmd(self):
    """Show word frequency - usage: .wordfreq <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.wordfreq <text></code>\n\n"
            "📝 <b>Example:</b> <code>.wordfreq the cat and the dog</code>"
        )
        return

    text = args[1].lower()
    words_list = text.split()

    if not words_list:
        await message.edit("❌ <b>No words found!</b>")
        return

    freq = Counter(words_list)
    total = len(words_list)
    sorted_freq = freq.most_common(20)

    lines = []
    for word, count in sorted_freq:
        pct = (count / total) * 100
        lines.append(f"• <code>{word}</code> — <b>{count}</b> ({pct:.1f}%)")

    await message.edit(
        f"📊 <b>Word Frequency</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Total words:</b> {total}\n\n"
        + "\n".join(lines)
    )
