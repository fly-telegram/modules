#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

import asyncio
from datetime import datetime, timedelta


def parse_time(time_str: str) -> int:
    """Parse time string to seconds

    Formats: 10s, 5m, 2h, 1d
    """
    time_str = time_str.lower().strip()

    if time_str.endswith("s"):
        return int(time_str[:-1])
    elif time_str.endswith("m"):
        return int(time_str[:-1]) * 60
    elif time_str.endswith("h"):
        return int(time_str[:-1]) * 3600
    elif time_str.endswith("d"):
        return int(time_str[:-1]) * 86400
    else:
        # Assume seconds
        return int(time_str)


def format_time(seconds: int) -> str:
    """Format seconds to readable string"""
    parts = []

    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)


async def remind_cmd(self):
    """Set a reminder - usage: .remind <time> <message>

    Time formats: 10s, 5m, 2h, 1d
    """
    message = self.message

    # Parse command
    args = message.text.split(maxsplit=2)

    if len(args) < 3:
        await message.edit(
            "❌ <b>Usage:</b> <code>.remind <time> <message></code>\n\n"
            "⏰ <b>Time formats:</b>\n"
            "• <code>s</code> - seconds\n"
            "• <code>m</code> - minutes\n"
            "• <code>h</code> - hours\n"
            "• <code>d</code> - days\n\n"
            "📝 <b>Examples:</b>\n"
            "• <code>.remind 10s Hello!</code>\n"
            "• <code>.remind 5m Check email</code>\n"
            "• <code>.remind 2h Meeting</code>"
        )
        return

    time_str = args[1]
    reminder_text = args[2]

    try:
        seconds = parse_time(time_str)
    except ValueError:
        await message.edit("❌ <b>Invalid time format!</b>")
        return

    if seconds <= 0:
        await message.edit("❌ <b>Time must be positive!</b>")
        return

    if seconds > 604800:  # 7 days
        await message.edit("❌ <b>Maximum reminder time is 7 days!</b>")
        return

    # Confirm reminder set
    remind_time = datetime.now() + timedelta(seconds=seconds)
    remind_time_str = remind_time.strftime("%Y-%m-%d %H:%M:%S")

    await message.edit(
        f"⏰ <b>Reminder set!</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Message:</b> <code>{reminder_text}</code>\n"
        f"⏱️ <b>Time:</b> <code>{format_time(seconds)}</code>\n"
        f"📅 <b>Remind at:</b> <code>{remind_time_str}</code>"
    )

    # Wait and remind
    await asyncio.sleep(seconds)

    await self.client.send_message(
        chat_id=message.chat.id,
        text=(
            f"🔔 <b>Reminder!</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"📝 {reminder_text}\n\n"
            f"⏰ <i>Set {format_time(seconds)} ago</i>"
        )
    )


async def timer_cmd(self):
    """Simple countdown timer - usage: .timer <time>"""
    message = self.message

    # Parse command
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.timer <time></code>\n\n"
            "📝 <b>Example:</b> <code>.timer 10s</code>"
        )
        return

    time_str = args[1]

    try:
        seconds = parse_time(time_str)
    except ValueError:
        await message.edit("❌ <b>Invalid time format!</b>")
        return

    if seconds <= 0 or seconds > 300:
        await message.edit("❌ <b>Timer must be between 1s and 300s!</b>")
        return

    # Countdown
    for remaining in range(seconds, 0, -1):
        progress = "█" * (seconds - remaining) + "░" * remaining
        await message.edit(
            f"⏱️ <b>Timer</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"[{progress}]\n\n"
            f"⏰ <b>Remaining:</b> <code>{format_time(remaining)}</code>"
        )
        await asyncio.sleep(1)

    await message.edit(
        f"⏱️ <b>Timer finished!</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"🔔 <b>Time's up!</b> <code>{format_time(seconds)}</code> passed."
    )
