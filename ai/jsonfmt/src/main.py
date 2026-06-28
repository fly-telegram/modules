#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

import json


async def jsonfmt_cmd(self):
    """Format/pretty-print JSON - usage: .jsonfmt <json>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.jsonfmt <json></code>\n\n"
            "📝 <b>Example:</b> <code>.jsonfmt {\"a\":1,\"b\":2}</code>"
        )
        return

    raw = args[1]

    try:
        parsed = json.loads(raw)
        formatted = json.dumps(parsed, indent=2, ensure_ascii=False)

        if len(formatted) > 4096:
            formatted = formatted[:4093] + "..."

        await message.edit(
            f"📋 <b>JSON Formatted</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"<code>{formatted}</code>"
        )
    except json.JSONDecodeError as e:
        await message.edit(
            f"❌ <b>Invalid JSON!</b>\n\n"
            f"<b>Error:</b> <code>{e}</code>"
        )
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def jsonmin_cmd(self):
    """Minify JSON - usage: .jsonmin <json>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.jsonmin <json></code>\n\n"
            "📝 <b>Example:</b> <code>.jsonmin {\"a\": 1, \"b\": 2}</code>"
        )
        return

    raw = args[1]

    try:
        parsed = json.loads(raw)
        minified = json.dumps(parsed, separators=(
            ",", ":"), ensure_ascii=False)

        if len(minified) > 4096:
            minified = minified[:4093] + "..."

        original_len = len(raw)
        new_len = len(minified)
        saved = original_len - new_len

        await message.edit(
            f"📦 <b>JSON Minified</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"<code>{minified}</code>\n\n"
            f"📊 <b>Original:</b> {original_len}B → <b>Minified:</b> {new_len}B"
            f" ({saved}B saved)"
        )
    except json.JSONDecodeError as e:
        await message.edit(
            f"❌ <b>Invalid JSON!</b>\n\n"
            f"<b>Error:</b> <code>{e}</code>"
        )
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def jsonval_cmd(self):
    """Validate JSON - usage: .jsonval <json>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.jsonval <json></code>\n\n"
            "📝 <b>Example:</b> <code>.jsonval {\"a\":1}</code>"
        )
        return

    raw = args[1]

    try:
        parsed = json.loads(raw)
        json_type = type(parsed).__name__

        if isinstance(parsed, dict):
            items = len(parsed)
        elif isinstance(parsed, (list, tuple)):
            items = len(parsed)
        else:
            items = "N/A"

        await message.edit(
            f"✅ <b>Valid JSON!</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"📋 <b>Type:</b> <code>{json_type}</code>\n"
            f"📏 <b>Length:</b> <code>{len(raw)}</code> chars\n"
            f"📦 <b>Items:</b> <code>{items}</code>"
        )
    except json.JSONDecodeError as e:
        msg = str(e)
        line_info = ""
        if hasattr(e, "lineno") and e.lineno:
            line_info = f"\n📍 <b>Line:</b> {e.lineno}, <b>Col:</b> {e.colno}"

        await message.edit(
            f"❌ <b>Invalid JSON!</b>\n"
            f"━━━━━━━━━━━━━━━{line_info}\n\n"
            f"<b>Error:</b> <code>{msg}</code>"
        )
    except Exception as e:
        await message.edit(f"❌ <b>Error:</b> <code>{e}</code>")
