#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

import random

LOREM_WORDS = [
    "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing",
    "elit", "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore",
    "et", "dolore", "magna", "aliqua", "enim", "ad", "minim", "veniam",
    "quis", "nostrud", "exercitation", "ullamco", "laboris", "nisi", "ut",
    "aliquip", "ex", "ea", "commodo", "consequat", "duis", "aute", "irure",
    "dolor", "in", "reprehenderit", "voluptate", "velit", "esse", "cillum",
    "eu", "fugiat", "nulla", "pariatur", "excepteur", "sint", "occaecat",
    "cupidatat", "non", "proident", "sunt", "culpa", "qui", "officia",
    "deserunt", "mollit", "anim", "id", "est", "laborum",
]

LOREM_PARAGRAPH = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do "
    "eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad "
    "minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip "
    "ex ea commodo consequat. Duis aute irure dolor in reprehenderit in "
    "voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur "
    "sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt "
    "mollit anim id est laborum."
)


async def lorem_cmd(self):
    """Generate lorem ipsum - usage: .lorem [words|paragraphs] [count]

    Default: 1 paragraph
    """
    message = self.message
    args = message.text.split(maxsplit=2)

    mode = "paragraphs"
    count = 1

    if len(args) > 1:
        if args[1].isdigit():
            count = int(args[1])
        elif args[1] in ("words", "paragraphs"):
            mode = args[1]
            if len(args) > 2 and args[2].isdigit():
                count = int(args[2])

    if mode == "words":
        count = max(1, min(count, 500))
        words = [random.choice(LOREM_WORDS) for _ in range(count)]
        result = " ".join(words).capitalize() + "."
    else:
        count = max(1, min(count, 10))
        result = "\n\n".join(LOREM_PARAGRAPH for _ in range(count))

    if len(result) > 4096:
        result = result[:4093] + "..."

    await message.edit(
        f"📝 <b>Lorem Ipsum</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{result}"
    )
