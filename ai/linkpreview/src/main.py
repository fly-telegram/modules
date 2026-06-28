#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

import re
import html
from urllib.parse import urlparse


URL_REGEX = re.compile(
    r"https?://[^\s<>\")\]]+"
)


def _extract_urls(text: str) -> list:
    urls = URL_REGEX.findall(text)
    cleaned = []
    for url in urls:
        while url and url[-1] in ".,;:!?)'\"":
            url = url[:-1]
        cleaned.append(url)
    return cleaned


def _validate_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    if not parsed.netloc:
        return ""
    return url


async def preview_cmd(self):
    """Fetch link preview (title, description, image) - usage: .preview <url> or reply"""
    message = self.message
    args = message.text.split(maxsplit=1)

    url = None
    if message.reply_to_message and message.reply_to_message.text:
        urls = _extract_urls(message.reply_to_message.text)
        if urls:
            url = urls[0]

    if not url and len(args) > 1:
        url = args[1].strip()

    if not url:
        await message.edit(
            "❌ <b>Usage:</b> <code>.preview <url></code>\n\n"
            "📝 <b>Example:</b> <code>.preview https://example.com</code>\n"
            "💡 Or reply to a message containing a URL"
        )
        return

    url = _validate_url(url)
    if not url:
        await message.edit("❌ <b>Invalid URL!</b>")
        return

    status_msg = await message.edit("🔍 <b>Fetching preview...</b>")

    try:
        import aiohttp

        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }) as resp:
                if resp.status != 200:
                    await status_msg.edit(
                        f"⚠️ <b>HTTP {resp.status}</b>\n\n"
                        f"🔗 <b>URL:</b> <code>{url}</code>"
                    )
                    return

                content_type = resp.headers.get("Content-Type", "")
                if "text/html" not in content_type:
                    await status_msg.edit(
                        f"📄 <b>Non-HTML content</b>\n\n"
                        f"🔗 <b>URL:</b> <code>{url}</code>\n"
                        f"📋 <b>Type:</b> <code>{content_type}</code>"
                    )
                    return

                body = await resp.text()

        title = ""
        description = ""
        image = ""

        title_match = re.search(
            r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']',
            body, re.IGNORECASE
        )
        if not title_match:
            title_match = re.search(
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:title["\']',
                body, re.IGNORECASE
            )
        if not title_match:
            title_match = re.search(
                r"<title>(.*?)</title>", body, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = html.unescape(title_match.group(1).strip())

        desc_match = re.search(
            r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']',
            body, re.IGNORECASE
        )
        if not desc_match:
            desc_match = re.search(
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:description["\']',
                body, re.IGNORECASE
            )
        if not desc_match:
            desc_match = re.search(
                r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
                body, re.IGNORECASE
            )
        if desc_match:
            description = html.unescape(desc_match.group(1).strip())

        img_match = re.search(
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
            body, re.IGNORECASE
        )
        if not img_match:
            img_match = re.search(
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
                body, re.IGNORECASE
            )
        if img_match:
            image = html.unescape(img_match.group(1).strip())

        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        result = "🔗 <b>Link Preview</b>\n"
        result += "━━━━━━━━━━━━━━━\n\n"

        if title:
            result += f"📌 <b>Title:</b> {title}\n"
        if description:
            if len(description) > 300:
                description = description[:297] + "..."
            result += f"📝 <b>Description:</b> {description}\n"

        result += f"🌐 <b>Domain:</b> <code>{domain}</code>\n"
        result += f"🔗 <b>URL:</b> <code>{url}</code>"

        if not title and not description:
            result += "\n\n⚠️ <b>No OpenGraph tags found on this page.</b>"

        await status_msg.edit(result)

    except ImportError:
        await status_msg.edit(
            "❌ <b>aiohttp is required!</b>\n\n"
            "Install it: <code>pip install aiohttp</code>"
        )
    except Exception as e:
        await status_msg.edit(
            f"❌ <b>Error fetching preview:</b>\n<code>{e}</code>"
        )


async def expand_cmd(self):
    """Expand shortened URL - usage: .expand <url>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.expand <url></code>\n\n"
            "📝 <b>Example:</b> <code>.expand https://bit.ly/3xyz</code>"
        )
        return

    url = args[1].strip()
    url = _validate_url(url)

    if not url:
        await message.edit("❌ <b>Invalid URL!</b>")
        return

    status_msg = await message.edit("🔄 <b>Expanding URL...</b>")

    try:
        import aiohttp

        timeout = aiohttp.ClientTimeout(total=15)
        urls_chain = [url]
        current = url

        async with aiohttp.ClientSession(timeout=timeout) as session:
            for _ in range(10):
                async with session.head(
                    current,
                    allow_redirects=False,
                    headers={"User-Agent": "Mozilla/5.0"}
                ) as resp:
                    if resp.status in (301, 302, 303, 307, 308):
                        location = resp.headers.get("Location", "")
                        if not location:
                            break
                        if not location.startswith("http"):
                            parsed = urlparse(current)
                            location = f"{parsed.scheme}://{parsed.netloc}{location}"
                        urls_chain.append(location)
                        current = location
                    else:
                        break

        if len(urls_chain) == 1:
            await status_msg.edit(
                f"✅ <b>No redirects - URL is already final</b>\n\n"
                f"🔗 <code>{url}</code>"
            )
            return

        result = "🔄 <b>Redirect Chain</b>\n"
        result += "━━━━━━━━━━━━━━━\n\n"

        for i, u in enumerate(urls_chain):
            icon = "🔗" if i == 0 else "⬇️" if i < len(urls_chain) - 1 else "✅"
            result += f"{icon} <code>{u}</code>\n"

        result += f"\n📊 <b>Hops:</b> <code>{len(urls_chain) - 1}</code>"
        await status_msg.edit(result)

    except ImportError:
        await status_msg.edit(
            "❌ <b>aiohttp is required!</b>\n\n"
            "Install it: <code>pip install aiohttp</code>"
        )
    except Exception as e:
        await status_msg.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def check_cmd(self):
    """Check if URL is reachable - usage: .check <url>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.check <url></code>\n\n"
            "📝 <b>Example:</b> <code>.check https://google.com</code>"
        )
        return

    url = args[1].strip()
    url = _validate_url(url)

    if not url:
        await message.edit("❌ <b>Invalid URL!</b>")
        return

    status_msg = await message.edit("🔍 <b>Checking URL...</b>")

    try:
        import aiohttp
        import time

        timeout = aiohttp.ClientTimeout(total=10)
        start = time.time()

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }) as resp:
                elapsed = round((time.time() - start) * 1000)
                content_type = resp.headers.get("Content-Type", "unknown")
                content_length = resp.headers.get("Content-Length", "unknown")
                server = resp.headers.get("Server", "unknown")
                status_code = resp.status
                reason = resp.reason

        if status_code < 300:
            icon = "✅"
        elif status_code < 400:
            icon = "🔄"
        else:
            icon = "❌"

        result = f"{icon} <b>URL Status</b>\n"
        result += "━━━━━━━━━━━━━━━\n\n"
        result += f"🔗 <b>URL:</b> <code>{url}</code>\n"
        result += f"📊 <b>Status:</b> <code>{status_code} {reason}</code>\n"
        result += f"⏱️ <b>Response time:</b> <code>{elapsed}ms</code>\n"
        result += f"📋 <b>Content-Type:</b> <code>{content_type}</code>\n"

        if content_length != "unknown":
            size = int(content_length)
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f} MB"
            result += f"📦 <b>Size:</b> <code>{size_str}</code>\n"

        result += f"🖥️ <b>Server:</b> <code>{server}</code>"

        await status_msg.edit(result)

    except ImportError:
        await status_msg.edit(
            "❌ <b>aiohttp is required!</b>\n\n"
            "Install it: <code>pip install aiohttp</code>"
        )
    except Exception as e:
        await status_msg.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def extract_cmd(self):
    """Extract all URLs from text - usage: .extract <text> or reply"""
    message = self.message
    args = message.text.split(maxsplit=1)

    text = None
    if message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text

    if not text and len(args) > 1:
        text = args[1]

    if not text:
        await message.edit(
            "❌ <b>Usage:</b> <code>.extract <text></code>\n\n"
            "📝 <b>Example:</b> <code>.extract Check https://google.com and https://github.com</code>\n"
            "💡 Or reply to a message"
        )
        return

    urls = _extract_urls(text)

    if not urls:
        await message.edit("🔍 <b>No URLs found in text.</b>")
        return

    result = f"🔗 <b>Extracted {len(urls)} URL(s)</b>\n"
    result += "━━━━━━━━━━━━━━━\n\n"

    for i, url in enumerate(urls, 1):
        parsed = urlparse(url)
        domain = parsed.netloc
        result += f"{i}. <b>{domain}</b>\n   <code>{url}</code>\n"

    await message.edit(result)


async def headers_cmd(self):
    """Show HTTP response headers - usage: .headers <url>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.headers <url></code>\n\n"
            "📝 <b>Example:</b> <code>.headers https://example.com</code>"
        )
        return

    url = args[1].strip()
    url = _validate_url(url)

    if not url:
        await message.edit("❌ <b>Invalid URL!</b>")
        return

    status_msg = await message.edit("🔍 <b>Fetching headers...</b>")

    try:
        import aiohttp

        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.head(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }, allow_redirects=True) as resp:
                headers = resp.headers
                status = resp.status

        result = f"📋 <b>HTTP Headers</b> - <code>{status}</code>\n"
        result += "━━━━━━━━━━━━━━━\n\n"

        priority = ["content-type", "content-length", "server", "location",
                    "cache-control", "set-cookie", "x-frame-options",
                    "strict-transport-security", "content-security-policy"]

        shown = set()
        for key in priority:
            if key in headers:
                shown.add(key)
                val = headers[key]
                if len(val) > 100:
                    val = val[:97] + "..."
                result += f"🔹 <b>{key.title()}:</b> <code>{val}</code>\n"

        for key, val in headers.items():
            if key not in shown:
                if len(val) > 100:
                    val = val[:97] + "..."
                result += f"   <b>{key}:</b> <code>{val}</code>\n"

        if len(result) > 4000:
            result = result[:3990] + "\n..."

        await status_msg.edit(result)

    except ImportError:
        await status_msg.edit(
            "❌ <b>aiohttp is required!</b>\n\n"
            "Install it: <code>pip install aiohttp</code>"
        )
    except Exception as e:
        await status_msg.edit(f"❌ <b>Error:</b> <code>{e}</code>")
