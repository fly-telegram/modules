#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

import base64
import random
import string
import re


async def upper_cmd(self):
    """Convert text to UPPERCASE - usage: .upper <text>"""
    message = self.message

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.upper <text></code>\n\n"
            "📝 <b>Example:</b> <code>.upper hello world</code>"
        )
        return

    text = args[1]
    result = text.upper()

    await message.edit(
        f"🔠 <b>Uppercase</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Original:</b> <code>{text}</code>\n"
        f"✅ <b>Result:</b> <code>{result}</code>"
    )


async def lower_cmd(self):
    """Convert text to lowercase - usage: .lower <text>"""
    message = self.message

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.lower <text></code>\n\n"
            "📝 <b>Example:</b> <code>.lower HELLO WORLD</code>"
        )
        return

    text = args[1]
    result = text.lower()

    await message.edit(
        f"🔡 <b>Lowercase</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Original:</b> <code>{text}</code>\n"
        f"✅ <b>Result:</b> <code>{result}</code>"
    )


async def title_cmd(self):
    """Convert text to Title Case - usage: .title <text>"""
    message = self.message

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.title <text></code>\n\n"
            "📝 <b>Example:</b> <code>.title hello world</code>"
        )
        return

    text = args[1]
    result = text.title()

    await message.edit(
        f"📝 <b>Title Case</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Original:</b> <code>{text}</code>\n"
        f"✅ <b>Result:</b> <code>{result}</code>"
    )


async def reverse_cmd(self):
    """Reverse text - usage: .reverse <text>"""
    message = self.message

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.reverse <text></code>\n\n"
            "📝 <b>Example:</b> <code>.reverse hello</code>"
        )
        return

    text = args[1]
    result = text[::-1]

    await message.edit(
        f"🔄 <b>Reversed</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Original:</b> <code>{text}</code>\n"
        f"✅ <b>Result:</b> <code>{result}</code>"
    )


async def count_cmd(self):
    """Count characters, words and lines - usage: .count <text>"""
    message = self.message

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.count <text></code>\n\n"
            "📝 <b>Example:</b> <code>.count Hello world</code>"
        )
        return

    text = args[1]

    chars = len(text)
    chars_no_spaces = len(text.replace(" ", ""))
    words = len(text.split())
    lines = len(text.split("\n"))

    preview = text[:100] + ("..." if len(text) > 100 else "")

    await message.edit(
        f"📊 <b>Text Statistics</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Text:</b> <code>{preview}</code>\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🔤 <b>Characters:</b> <code>{chars}</code>\n"
        f"🔤 <b>Characters (no spaces):</b> <code>{chars_no_spaces}</code>\n"
        f"📖 <b>Words:</b> <code>{words}</code>\n"
        f"📄 <b>Lines:</b> <code>{lines}</code>"
    )


async def b64enc_cmd(self):
    """Encode text to Base64 - usage: .b64enc <text>"""
    message = self.message

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.b64enc <text></code>\n\n"
            "📝 <b>Example:</b> <code>.b64enc hello world</code>"
        )
        return

    text = args[1]

    try:
        encoded = base64.b64encode(text.encode("utf-8")).decode("utf-8")

        await message.edit(
            f"🔐 <b>Base64 Encoded</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"📝 <b>Original:</b> <code>{text}</code>\n"
            f"✅ <b>Encoded:</b> <code>{encoded}</code>"
        )
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def b64dec_cmd(self):
    """Decode Base64 to text - usage: .b64dec <encoded>"""
    message = self.message

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.b64dec <encoded></code>\n\n"
            "📝 <b>Example:</b> <code>.b64dec aGVsbG8=</code>"
        )
        return

    encoded = args[1]

    try:
        decoded = base64.b64decode(encoded.encode("utf-8")).decode("utf-8")

        await message.edit(
            f"🔓 <b>Base64 Decoded</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"📝 <b>Encoded:</b> <code>{encoded}</code>\n"
            f"✅ <b>Decoded:</b> <code>{decoded}</code>"
        )
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def rand_cmd(self):
    """Generate random string - usage: .rand <length> [type]

    Types: alpha (letters), num (digits), alphanum (both), all (with symbols)
    """
    message = self.message

    args = message.text.split()

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.rand <length> [type]</code>\n\n"
            "📋 <b>Types:</b>\n"
            "• <code>alpha</code> - letters only\n"
            "• <code>num</code> - digits only\n"
            "• <code>alphanum</code> - letters + digits\n"
            "• <code>all</code> - letters + digits + symbols\n\n"
            "📝 <b>Example:</b> <code>.rand 16 alphanum</code>"
        )
        return

    try:
        length = int(args[1])
    except ValueError:
        await message.edit("❌ <b>Length must be a number!</b>")
        return

    if length <= 0 or length > 4096:
        await message.edit("❌ <b>Length must be between 1 and 4096!</b>")
        return

    str_type = args[2].lower() if len(args) > 2 else "alphanum"

    if str_type == "alpha":
        chars = string.ascii_letters
    elif str_type == "num":
        chars = string.digits
    elif str_type == "alphanum":
        chars = string.ascii_letters + string.digits
    elif str_type == "all":
        chars = string.ascii_letters + string.digits + string.punctuation
    else:
        await message.edit(
            f"❌ <b>Unknown type:</b> <code>{str_type}</code>\n\n"
            f"📋 <b>Available:</b> alpha, num, alphanum, all"
        )
        return

    result = "".join(random.choice(chars) for _ in range(length))

    await message.edit(
        f"🎲 <b>Random String</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📏 <b>Length:</b> <code>{length}</code>\n"
        f"📋 <b>Type:</b> <code>{str_type}</code>\n\n"
        f"✅ <b>Result:</b>\n<code>{result}</code>"
    )


async def repeat_cmd(self):
    """Repeat text multiple times - usage: .repeat <count> <text>"""
    message = self.message

    args = message.text.split(maxsplit=2)

    if len(args) < 3:
        await message.edit(
            "❌ <b>Usage:</b> <code>.repeat <count> <text></code>\n\n"
            "📝 <b>Example:</b> <code>.repeat 3 Hello!</code>"
        )
        return

    try:
        count = int(args[1])
    except ValueError:
        await message.edit("❌ <b>Count must be a number!</b>")
        return

    if count <= 0 or count > 100:
        await message.edit("❌ <b>Count must be between 1 and 100!</b>")
        return

    text = args[2]
    result = (text + " ") * count
    result = result.strip()

    # Telegram message limit
    if len(result) > 4096:
        result = result[:4093] + "..."

    await message.edit(
        f"🔁 <b>Repeated {count} times</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Original:</b> <code>{text}</code>\n\n"
        f"✅ <b>Result:</b>\n<code>{result}</code>"
    )


async def replace_cmd(self):
    """Replace text - usage: .replace <old> | <new> | <text>"""
    message = self.message

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.replace <old> | <new> | <text></code>\n\n"
            "📝 <b>Example:</b> <code>.replace cat | dog | I love cats</code>"
        )
        return

    parts = args[1].split("|")

    if len(parts) != 3:
        await message.edit(
            "❌ <b>Wrong format!</b>\n\n"
            "📝 <b>Example:</b> <code>.replace cat | dog | I love cats</code>"
        )
        return

    old = parts[0].strip()
    new = parts[1].strip()
    text = parts[2].strip()

    result = text.replace(old, new)
    count = text.count(old)

    await message.edit(
        f"🔄 <b>Replace</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Original:</b> <code>{text}</code>\n"
        f"🔍 <b>Find:</b> <code>{old}</code>\n"
        f"✏️ <b>Replace with:</b> <code>{new}</code>\n"
        f"📊 <b>Replacements:</b> <code>{count}</code>\n\n"
        f"✅ <b>Result:</b> <code>{result}</code>"
    )


async def capitalize_cmd(self):
    """Capitalize first letter of each sentence - usage: .capitalize <text>"""
    message = self.message

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.capitalize <text></code>\n\n"
            "📝 <b>Example:</b> <code>.capitalize hello. world.</code>"
        )
        return

    text = args[1]

    # Capitalize after sentence endings
    sentences = re.split(r'([.!?]\s*)', text)
    result = ""
    for i, s in enumerate(sentences):
        if i == 0 or (i > 0 and sentences[i-1] in [". ", "! ", "? "]):
            result += s.capitalize()
        else:
            result += s

    await message.edit(
        f"✏️ <b>Capitalized</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Original:</b> <code>{text}</code>\n"
        f"✅ <b>Result:</b> <code>{result}</code>"
    )


async def spoiler_cmd(self):
    """Wrap text in spoiler tags - usage: .spoiler <text>"""
    message = self.message

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.spoiler <text></code>\n\n"
            "📝 <b>Example:</b> <code>.spoiler secret text</code>"
        )
        return

    text = args[1]

    await message.edit(
        f"👻 <b>Spoiler</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"|| {text} ||"
    )


async def code_cmd(self):
    """Wrap text in code block - usage: .code <text>"""
    message = self.message

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.code <text></code>\n\n"
            "📝 <b>Example:</b> <code>.code some code here</code>"
        )
        return

    text = args[1]

    await message.edit(
        f"💻 <b>Code Block</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"<code>{text}</code>"
    )
