#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

import io
import urllib.parse


async def screenshot_cmd(self):
    """Take screenshot of a website \u2014 usage: .ss <url> [width] [height]"""
    message = self.message
    args = message.text.split()

    if len(args) < 2:
        await message.edit(
            "\u274c <b>Usage:</b> <code>.ss <url> [width] [height]</code>\n\n"
            "\U0001f4dd <b>Examples:</b>\n"
            "\u2022 <code>.ss https://google.com</code>\n"
            "\u2022 <code>.ss https://example.com 1920 1080</code>"
        )
        return

    url = args[1]
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    width = int(args[2]) if len(args) > 2 else 1280
    height = int(args[3]) if len(args) > 3 else 720

    status_msg = await message.edit(f"\ud83d\udcf8 <b>Taking screenshot of</b> <code>{url}</code>...")

    try:
        import aiohttp

        # Using screenshot-api service (free, no key)
        encoded_url = urllib.parse.quote(url)
        api_url = f"https://api.screenshotmachine.com/?key=8a1ee2&url={encoded_url}&dimension={width}x{height}&device=desktop&format=PNG&cacheLimit=0"

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(api_url) as resp:
                if resp.status != 200:
                    await status_msg.edit(
                        f"\u274c <b>Screenshot failed (HTTP {resp.status})</b>\n\n"
                        f"\U0001f517 <code>{url}</code>"
                    )
                    return
                data = await resp.read()

        # Check if we got an actual image
        if len(data) < 1000:
            # Fallback: use a different free service
            fallback_url = f"https://image.thum.io/get/width/{width}/crop/{height}/{url}"
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(fallback_url) as resp:
                    if resp.status != 200:
                        await status_msg.edit("\u274c <b>All screenshot services failed!</b>")
                        return
                    data = await resp.read()

        bio = io.BytesIO(data)
        bio.name = "screenshot.png"
        bio.seek(0)

        await message.delete()
        await self.client.send_photo(
            chat_id=message.chat.id,
            photo=bio,
            caption=(
                f"\ud83d\udcf8 <b>Screenshot</b>\n"
                f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"
                f"\U0001f517 <b>URL:</b> <code>{url}</code>\n"
                f"\U0001f5bc\ufe0f <b>Size:</b> <code>{width}x{height}</code>"
            )
        )

    except ImportError:
        await status_msg.edit(
            "\u274c <b>aiohttp is required!</b>\n\n"
            "Install it: <code>pip install aiohttp</code>"
        )
    except Exception as e:
        await status_msg.edit(f"\u274c <b>Error:</b> <code>{e}</code>")
