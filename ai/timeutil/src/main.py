#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

from datetime import datetime, timezone, timedelta


async def epoch_cmd(self):
    """Convert epoch timestamp to human time - usage: .epoch [timestamp]"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) > 1:
        try:
            ts = float(args[1])
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            await message.edit(
                f"⏰ <b>Epoch Converter</b>\n"
                f"━━━━━━━━━━━━━━━\n\n"
                f"🔢 <b>Epoch:</b> <code>{ts}</code>\n"
                f"📅 <b>UTC:</b> <code>{dt.strftime('%Y-%m-%d %H:%M:%S')}</code>\n"
                f"📍 <b>Local:</b> <code>{datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')}</code>"
            )
        except (ValueError, OSError):
            await message.edit("❌ <b>Invalid timestamp!</b>")
    else:
        now = datetime.now()
        utc_now = datetime.now(timezone.utc)
        epoch_now = datetime.now().timestamp()

        await message.edit(
            f"⏰ <b>Current Time</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"📍 <b>Local:</b> <code>{now.strftime('%Y-%m-%d %H:%M:%S')}</code>\n"
            f"🌐 <b>UTC:</b> <code>{utc_now.strftime('%Y-%m-%d %H:%M:%S')}</code>\n"
            f"🔢 <b>Epoch:</b> <code>{int(epoch_now)}</code>\n"
            f"🔢 <b>Epoch (ms):</b> <code>{int(epoch_now * 1000)}</code>"
        )


async def tz_cmd(self):
    """Show time in a timezone - usage: .tz <offset> (e.g. +3, -5)"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.tz <offset></code>\n\n"
            "📝 <b>Examples:</b>\n"
            "• <code>.tz +3</code> (Moscow/UTC+3)\n"
            "• <code>.tz -5</code> (New York/UTC-5)\n"
            "• <code>.tz +5:30</code> (India/UTC+5:30)\n"
            "• <code>.tz utc</code> (UTC)"
        )
        return

    offset_str = args[1].strip().lower()

    if offset_str == "utc":
        dt = datetime.now(timezone.utc)
        label = "UTC"
    else:
        try:
            if ":" in offset_str:
                h, m = offset_str.split(":")
                total_hours = int(h) + int(m) / 60
            else:
                total_hours = float(offset_str)

            tz = timezone(timedelta(hours=total_hours))
            dt = datetime.now(tz)
            label = f"UTC{offset_str}"
        except ValueError:
            await message.edit("❌ <b>Invalid timezone offset!</b>")
            return

    await message.edit(
        f"⏰ <b>Timezone</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📍 <b>{label}:</b> <code>{dt.strftime('%Y-%m-%d %H:%M:%S')}</code>"
    )
