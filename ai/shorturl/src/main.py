#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

import urllib.parse


async def short_cmd(self):
    """Shorten URL \u2014 usage: .short <url> [service]

    Services: isgd (default), tinyurl, vgd
    """
    message = self.message
    args = message.text.split()

    if len(args) < 2:
        await message.edit(
            "\u274c <b>Usage:</b> <code>.short <url> [service]</code>\n\n"
            "\U0001f4dd <b>Example:</b> <code>.short https://example.com</code>\n\n"
            "\U0001f517 <b>Services:</b>\n"
            "\u2022 <code>isgd</code> \u2014 is.gd (default)\n"
            "\u2022 <code>tinyurl</code> \u2014 tinyurl.com\n"
            "\u2022 <code>vgd</code> \u2014 v.gd"
        )
        return

    url = args[1]
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    service = args[2].lower() if len(args) > 2 else "isgd"

    status_msg = await message.edit("\U0001f517 <b>Shortening URL...</b>")

    try:
        import aiohttp

        timeout = aiohttp.ClientTimeout(total=10)

        if service == "isgd":
            api_url = f"https://is.gd/create.php?format=simple&url={urllib.parse.quote(url)}"
        elif service == "vgd":
            api_url = f"https://v.gd/create.php?format=simple&url={urllib.parse.quote(url)}"
        elif service == "tinyurl":
            api_url = f"https://tinyurl.com/api-create.php?url={urllib.parse.quote(url)}"
        else:
            await status_msg.edit(
                f"\u274c <b>Unknown service:</b> <code>{service}</code>\n\n"
                f"\U0001f517 <b>Available:</b> isgd, tinyurl, vgd"
            )
            return

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(api_url) as resp:
                if resp.status != 200:
                    await status_msg.edit(f"\u274c <b>Service returned HTTP {resp.status}</b>")
                    return
                short_url = await resp.text()

        short_url = short_url.strip()

        if not short_url.startswith("http"):
            await status_msg.edit(f"\u274c <b>Service error:</b> <code>{short_url}</code>")
            return

        await status_msg.edit(
            f"\U0001f517 <b>URL Shortened!</b>\n"
            f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"
            f"\U0001f4e8 <b>Original:</b> <code>{url}</code>\n"
            f"\u2705 <b>Short:</b> <code>{short_url}</code>\n"
            f"\U0001f4ca <b>Service:</b> <code>{service}</code>"
        )

    except ImportError:
        await status_msg.edit(
            "\u274c <b>aiohttp is required!</b>\n\n"
            "Install it: <code>pip install aiohttp</code>"
        )
    except Exception as e:
        await status_msg.edit(f"\u274c <b>Error:</b> <code>{e}</code>")


async def expand_cmd(self):
    """Expand shortened URL \u2014 usage: .expand <url>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "\u274c <b>Usage:</b> <code>.expand <url></code>\n\n"
            "\U0001f4dd <b>Example:</b> <code>.expand https://bit.ly/3xyz</code>"
        )
        return

    url = args[1].strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    status_msg = await message.edit("\U0001f504 <b>Expanding URL...</b>")

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
                            from urllib.parse import urlparse
                            parsed = urlparse(current)
                            location = f"{parsed.scheme}://{parsed.netloc}{location}"
                        urls_chain.append(location)
                        current = location
                    else:
                        break

        if len(urls_chain) == 1:
            await status_msg.edit(
                f"\u2705 <b>No redirects \u2014 URL is already final</b>\n\n"
                f"\U0001f517 <code>{url}</code>"
            )
            return

        result = "\U0001f504 <b>Redirect Chain</b>\n"
        result += "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"

        for i, u in enumerate(urls_chain):
            icon = "\U0001f517" if i == 0 else "\u2b07\ufe0f" if i < len(
                urls_chain) - 1 else "\u2705"
            result += f"{icon} <code>{u}</code>\n"

        result += f"\n\U0001f4ca <b>Hops:</b> <code>{len(urls_chain) - 1}</code>"
        await status_msg.edit(result)

    except ImportError:
        await status_msg.edit(
            "\u274c <b>aiohttp is required!</b>\n\n"
            "Install it: <code>pip install aiohttp</code>"
        )
    except Exception as e:
        await status_msg.edit(f"\u274c <b>Error:</b> <code>{e}</code>")
