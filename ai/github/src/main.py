#     __ __     __  ___      _ ___
#    // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

from uuid import uuid4

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import aiohttp

API_BASE = "https://api.github.com"
HEADERS = {"User-Agent": "FlyTelegram/1.0"}


def _kb(via, buttons):
    rows = []
    for row in buttons:
        line = []
        for b in row:
            cb = b.get("callback")
            params = b.get("params", {})
            if callable(cb):
                uid = str(uuid4())
                via.handlers[uid] = {"callback": cb, "params": params}
                line.append(InlineKeyboardButton(
                    text=b["text"], callback_data=uid))
            elif "url" in b:
                line.append(InlineKeyboardButton(text=b["text"], url=b["url"]))
        rows.append(line)
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def github_cmd(self):
    """Search GitHub — usage: .github <user|repo user/repo>"""
    message = self.message
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.edit(
            "❌ <b>Usage:</b>\n"
            "  <code>.github username</code> — user info\n"
            "  <code>.github user/repo</code> — repo info\n\n"
            "📝 <b>Example:</b> <code>.github torvalds</code>"
        )

    query = args[1].strip()
    await message.edit(f"🔍 Searching <b>{query}</b>...")

    if "/" in query:
        parts = query.split("/")
        if len(parts) >= 2:
            owner, repo = parts[0], parts[1]
            return await _repo_info(self, message, owner, repo)

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(f"{API_BASE}/users/{query}") as resp:
            if resp.status != 200:
                return await message.edit(
                    f"❌ User <b>{query}</b> not found"
                )
            data = await resp.json()

    name = data.get("name") or query
    bio = data.get("bio") or "No bio"
    public_repos = data.get("public_repos", 0)
    followers = data.get("followers", 0)
    following = data.get("following", 0)
    location = data.get("location") or "Unknown"
    blog = data.get("blog") or "—"
    avatar = data.get("avatar_url", "")
    url = data.get("html_url", "")
    login = data.get("login", query)

    text = (
        f"👤 <b>{name}</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Bio:</b> <i>{bio}</i>\n\n"
        f"📦 <b>Repos:</b> <code>{public_repos}</code>\n"
        f"👥 <b>Followers:</b> <code>{followers}</code>\n"
        f"🔗 <b>Following:</b> <code>{following}</code>\n"
        f"📍 <b>Location:</b> <code>{location}</code>\n"
        f"🌐 <b>Blog:</b> <code>{blog}</code>"
    )

    via = self.client.inline.viamanager
    buttons = [
        [{"text": "📦 Repositories", "callback": _user_repos,
          "params": {"login": login, "chat_id": message.chat.id}}],
        [{"text": "🌐 GitHub Profile", "url": url}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await message.delete()
    await self.client.inline.say(
        self.client, message, text,
        prefix="gh_", buttons=buttons, chat_id=message.chat.id,
        file=avatar, file_type="photo" if avatar else None,
    )


async def _user_repos(call, login: str, chat_id: int):
    await call.answer("Loading repositories...")
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(
            f"{API_BASE}/users/{login}/repos",
            params={"sort": "updated", "per_page": 5},
        ) as resp:
            if resp.status != 200:
                return await call.answer("❌ Failed to load repos")
            data = await resp.json()

    if not data:
        return await call.edit_message(f"📭 No public repos for <b>{login}</b>")

    via = call.client.inline.viamanager
    text = f"📦 <b>{login}'s Repositories</b>\n━━━━━━━━━━━━━━━\n\nSelect a repo:"
    buttons = []
    for i, repo in enumerate(data[:5]):
        name = repo.get("name", "Unknown")
        lang = repo.get("language") or "?"
        stars = repo.get("stargazers_count", 0)
        buttons.append([{
            "text": f"{i + 1}. {name} ⭐{stars} ({lang})",
            "callback": _show_repo,
            "params": {"owner": login, "repo": name, "chat_id": chat_id},
        }])
    buttons.append([{"text": "⬅️ Back", "callback": _back_user,
                     "params": {"login": login, "chat_id": chat_id}}])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _show_repo(call, owner: str, repo: str, chat_id: int):
    await call.answer("Loading repo...")
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(f"{API_BASE}/repos/{owner}/{repo}") as resp:
            if resp.status != 200:
                return await call.answer("❌ Repo not found")
            data = await resp.json()

    name = data.get("full_name", f"{owner}/{repo}")
    desc = data.get("description") or "No description"
    stars = data.get("stargazers_count", 0)
    forks = data.get("forks_count", 0)
    issues = data.get("open_issues_count", 0)
    lang = data.get("language") or "Unknown"
    license_name = (data.get("license") or {}).get("spdx_id") or "None"
    url = data.get("html_url", "")

    text = (
        f"📦 <b>{name}</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 {desc}\n\n"
        f"⭐ <b>Stars:</b> <code>{stars}</code>\n"
        f"🍴 <b>Forks:</b> <code>{forks}</code>\n"
        f"⚠️ <b>Issues:</b> <code>{issues}</code>\n"
        f"💻 <b>Language:</b> <code>{lang}</code>\n"
        f"📜 <b>License:</b> <code>{license_name}</code>"
    )

    via = call.client.inline.viamanager
    buttons = [
        [{"text": "🌐 View on GitHub", "url": url}],
        [{"text": "⬅️ Back to repos", "callback": _user_repos,
          "params": {"login": owner, "chat_id": chat_id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _repo_info(self, message, owner, repo):
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(f"{API_BASE}/repos/{owner}/{repo}") as resp:
            if resp.status != 200:
                return await message.edit(
                    f"❌ Repo <b>{owner}/{repo}</b> not found"
                )
            data = await resp.json()

    name = data.get("full_name", f"{owner}/{repo}")
    desc = data.get("description") or "No description"
    stars = data.get("stargazers_count", 0)
    forks = data.get("forks_count", 0)
    issues = data.get("open_issues_count", 0)
    lang = data.get("language") or "Unknown"
    license_name = (data.get("license") or {}).get("spdx_id") or "None"
    url = data.get("html_url", "")

    text = (
        f"📦 <b>{name}</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 {desc}\n\n"
        f"⭐ <b>Stars:</b> <code>{stars}</code>\n"
        f"🍴 <b>Forks:</b> <code>{forks}</code>\n"
        f"⚠️ <b>Issues:</b> <code>{issues}</code>\n"
        f"💻 <b>Language:</b> <code>{lang}</code>\n"
        f"📜 <b>License:</b> <code>{license_name}</code>"
    )

    via = self.client.inline.viamanager
    buttons = [
        [{"text": "🌐 View on GitHub", "url": url}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await message.delete()
    await self.client.inline.say(
        self.client, message, text,
        prefix="gh_", buttons=buttons, chat_id=message.chat.id,
    )


async def _back_user(call, login: str, chat_id: int):
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(f"{API_BASE}/users/{login}") as resp:
            if resp.status != 200:
                return await call.edit_message("❌ User not found")
            data = await resp.json()

    name = data.get("name") or login
    bio = data.get("bio") or "No bio"
    public_repos = data.get("public_repos", 0)
    followers = data.get("followers", 0)
    following = data.get("following", 0)
    location = data.get("location") or "Unknown"
    blog = data.get("blog") or "—"
    url = data.get("html_url", "")

    text = (
        f"👤 <b>{name}</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Bio:</b> <i>{bio}</i>\n\n"
        f"📦 <b>Repos:</b> <code>{public_repos}</code>\n"
        f"👥 <b>Followers:</b> <code>{followers}</code>\n"
        f"🔗 <b>Following:</b> <code>{following}</code>\n"
        f"📍 <b>Location:</b> <code>{location}</code>\n"
        f"🌐 <b>Blog:</b> <code>{blog}</code>"
    )

    via = call.client.inline.viamanager
    buttons = [
        [{"text": "📦 Repositories", "callback": _user_repos,
          "params": {"login": login, "chat_id": chat_id}}],
        [{"text": "🌐 GitHub Profile", "url": url}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _close(call):
    await call.edit_message("🗑 Closed")
