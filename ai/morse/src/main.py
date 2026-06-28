#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

MORSE_CODE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".",
    "F": "..-.", "G": "--.", "H": "....", "I": "..", "J": ".---",
    "K": "-.-", "L": ".-..", "M": "--", "N": "-.", "O": "---",
    "P": ".--.", "Q": "--.-", "R": ".-.", "S": "...", "T": "-",
    "U": "..-", "V": "...-", "W": ".--", "X": "-..-", "Y": "-.--",
    "Z": "--..",
    "0": "-----", "1": ".----", "2": "..---", "3": "...--",
    "4": "....-", "5": ".....", "6": "-....", "7": "--...",
    "8": "---..", "9": "----.",
    ".": ".-.-.-", ",": "--..--", "?": "..--..", "'": ".----.",
    "!": "-.-.--", "/": "-..-.", "(": "-.--.", ")": "-.--.-",
    "&": ".-...", ":": "---...", ";": "-.-.-.", "=": "-...-",
    "+": ".-.-.", "-": "-....-", "_": "..--.-", '"': ".-..-.",
    "@": ".--.-.", " ": "/",
}

MORSE_REVERSE = {v: k for k, v in MORSE_CODE.items()}


async def morse_cmd(self):
    """Encode text to Morse code - usage: .morse <text>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.morse <text></code>\n\n"
            "📝 <b>Example:</b> <code>.morse Hello world</code>"
        )
        return

    text = args[1].upper()
    result = " ".join(MORSE_CODE.get(c, "") for c in text)
    result = result.replace("  ", "   ")

    if len(result) > 4096:
        result = result[:4093] + "..."

    await message.edit(
        f"📡 <b>Morse Code</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Text:</b> <code>{text}</code>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<code>{result}</code>"
    )


async def unmorse_cmd(self):
    """Decode Morse code to text - usage: .unmorse <code>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.unmorse <code></code>\n\n"
            "📝 <b>Example:</b> <code>.unmorse .... . .-.. .-.. ---</code>"
        )
        return

    code = args[1].strip()
    words = code.split("   ")
    result_words = []

    try:
        for word in words:
            letters = word.split(" ")
            decoded = "".join(MORSE_REVERSE.get(l, "?") for l in letters)
            result_words.append(decoded)

        result = " ".join(result_words)

        await message.edit(
            f"📡 <b>Morse Decode</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"📝 <b>Code:</b> <code>{code[:200]}</code>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"✅ <b>Text:</b> <code>{result}</code>"
        )
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")
