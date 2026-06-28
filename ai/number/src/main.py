#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

import math


async def prime_cmd(self):
    """Check if number is prime - usage: .prime <number>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.prime <number></code>\n\n"
            "📝 <b>Example:</b> <code>.prime 17</code>"
        )
        return

    try:
        n = int(args[1])
    except ValueError:
        await message.edit("❌ <b>Please enter a valid integer!</b>")
        return

    if n < 2:
        result = "❌ Not prime (must be >= 2)"
    else:
        is_prime = all(n % i != 0 for i in range(2, int(math.sqrt(n)) + 1))
        result = "✅ Is prime!" if is_prime else "❌ Not prime"

    await message.edit(
        f"🔢 <b>Prime Check</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"🔢 <b>Number:</b> <code>{n}</code>\n"
        f"📊 <b>Result:</b> {result}"
    )


async def factorial_cmd(self):
    """Calculate factorial - usage: .factorial <number>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.factorial <number></code>\n\n"
            "📝 <b>Example:</b> <code>.factorial 5</code>"
        )
        return

    try:
        n = int(args[1])
    except ValueError:
        await message.edit("❌ <b>Please enter a valid integer!</b>")
        return

    if n < 0 or n > 1000:
        await message.edit("❌ <b>Number must be between 0 and 1000!</b>")
        return

    result = math.factorial(n)
    result_str = str(result)
    if len(result_str) > 400:
        result_str = result_str[:397] + "..."

    await message.edit(
        f"🔢 <b>Factorial</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"🔢 <b>Input:</b> <code>{n}!</code>\n"
        f"✅ <b>Result:</b> <code>{result_str}</code>\n"
        f"📏 <b>Digits:</b> <code>{len(str(result))}</code>"
    )


async def fib_cmd(self):
    """Generate fibonacci sequence - usage: .fib <count>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.fib <count></code>\n\n"
            "📝 <b>Example:</b> <code>.fib 10</code>"
        )
        return

    try:
        n = int(args[1])
    except ValueError:
        await message.edit("❌ <b>Please enter a valid integer!</b>")
        return

    if n < 1 or n > 100:
        await message.edit("❌ <b>Count must be between 1 and 100!</b>")
        return

    seq = [0, 1]
    for i in range(2, n):
        seq.append(seq[-1] + seq[-2])

    seq = seq[:n]
    result = ", ".join(str(x) for x in seq)

    await message.edit(
        f"🔢 <b>Fibonacci</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"🔢 <b>Count:</b> <code>{n}</code>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<code>{result}</code>"
    )


async def gcd_cmd(self):
    """Calculate GCD of two numbers - usage: .gcd <a> <b>"""
    message = self.message
    args = message.text.split(maxsplit=2)

    if len(args) < 3:
        await message.edit(
            "❌ <b>Usage:</b> <code>.gcd <a> <b></code>\n\n"
            "📝 <b>Example:</b> <code>.gcd 12 18</code>"
        )
        return

    try:
        a, b = int(args[1]), int(args[2])
    except ValueError:
        await message.edit("❌ <b>Please enter valid integers!</b>")
        return

    result = math.gcd(a, b)
    lcm = abs(a * b) // result

    await message.edit(
        f"🔢 <b>GCD & LCM</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"🔢 <b>Numbers:</b> <code>{a}</code>, <code>{b}</code>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"✅ <b>GCD:</b> <code>{result}</code>\n"
        f"✅ <b>LCM:</b> <code>{lcm}</code>"
    )


async def factors_cmd(self):
    """Find all factors of a number - usage: .factors <number>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.factors <number></code>\n\n"
            "📝 <b>Example:</b> <code>.factors 12</code>"
        )
        return

    try:
        n = int(args[1])
    except ValueError:
        await message.edit("❌ <b>Please enter a valid integer!</b>")
        return

    if n < 1:
        await message.edit("❌ <b>Number must be positive!</b>")
        return

    factors = [i for i in range(1, abs(n) + 1) if n % i == 0]
    result = ", ".join(str(f) for f in factors)

    await message.edit(
        f"🔢 <b>Factors</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"🔢 <b>Number:</b> <code>{n}</code>\n"
        f"📊 <b>Count:</b> <code>{len(factors)}</code>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"<code>{result}</code>"
    )
