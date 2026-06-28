#     __ __     __  ___      _ ___
#    // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

from uuid import uuid4

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import aiohttp
import html
import random

CATEGORIES = {
    "general": 9, "books": 10, "film": 11, "music": 12,
    "tv": 14, "games": 15, "science": 17, "computers": 18,
    "math": 19, "sports": 21, "geography": 22, "history": 23,
    "animals": 27,
}


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


async def trivia_cmd(self):
    """Get a trivia question — usage: .trivia [category]"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) > 1:
        cat = args[1].strip().lower()
        if cat in CATEGORIES:
            return await _fetch_trivia(message, cat)
        return await message.edit(
            f"❌ Unknown category: <b>{cat}</b>"
        )

    return await _show_categories(message)


async def _show_categories(message):
    via = message.client.inline.viamanager
    text = "❓ <b>Trivia Categories</b>\n━━━━━━━━━━━━━━━\n\nSelect a category:"
    buttons = []
    for name in CATEGORIES:
        buttons.append([{
            "text": f"❓ {name.capitalize()}",
            "callback": _fetch_trivia_cb,
            "params": {"category": name, "chat_id": message.chat.id},
        }])
    buttons.append([{"text": "🎲 Random", "callback": _random_trivia_cb,
                     "params": {"chat_id": message.chat.id}}])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await message.delete()
    await message.client.inline.say(
        message.client, message, text,
        prefix="trivia_", buttons=buttons, chat_id=message.chat.id,
    )


async def _fetch_trivia(message, category):
    await message.edit(f"❓ Fetching a <b>{category}</b> question...")
    cat_id = CATEGORIES[category]
    question_data = await _get_question(cat_id)
    if not question_data:
        return await message.edit("❌ Failed to fetch question")
    await _show_question(message, question_data, category)


async def _fetch_trivia_cb(call, category: str, chat_id: int):
    await call.answer("Loading...")
    cat_id = CATEGORIES[category]
    question_data = await _get_question(cat_id)
    if not question_data:
        return await call.edit_message("❌ Failed to fetch question")
    await _show_question_cb(call, question_data, category, chat_id)


async def _random_trivia_cb(call, chat_id: int):
    category = random.choice(list(CATEGORIES.keys()))
    await call.answer(f"🎲 {category}")
    cat_id = CATEGORIES[category]
    question_data = await _get_question(cat_id)
    if not question_data:
        return await call.edit_message("❌ Failed to fetch question")
    await _show_question_cb(call, question_data, category, chat_id)


async def _get_question(category_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://opentdb.com/api.php",
            params={
                "amount": 1,
                "category": category_id,
                "type": "multiple",
                "encode": "base64",
            },
        ) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()

    import base64

    results = data.get("results", [])
    if not results:
        return None

    q = results[0]
    question = base64.b64decode(q["question"]).decode()
    correct = base64.b64decode(q["correct_answer"]).decode()
    incorrect = [
        base64.b64decode(a).decode() for a in q["incorrect_answers"]
    ]
    difficulty = base64.b64decode(q["difficulty"]).decode()

    return {
        "question": question,
        "correct": correct,
        "incorrect": incorrect,
        "difficulty": difficulty,
    }


async def _show_question(message, q_data, category):
    question = q_data["question"]
    correct = q_data["correct"]
    incorrect = q_data["incorrect"]
    difficulty = q_data["difficulty"]

    answers = incorrect + [correct]
    random.shuffle(answers)
    correct_index = answers.index(correct)

    diff_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}
    emoji = diff_emoji.get(difficulty, "❓")

    text = (
        f"❓ <b>Trivia ({category})</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{question}\n\n"
        f"{emoji} <b>Difficulty:</b> <code>{difficulty}</code>\n\n"
        f"Select an answer:"
    )

    via = message.client.inline.viamanager
    buttons = []
    for i, ans in enumerate(answers):
        buttons.append([{
            "text": f"{chr(65 + i)}. {html.escape(ans)}",
            "callback": _check_answer,
            "params": {
                "selected": i, "correct": correct_index,
                "category": category, "chat_id": message.chat.id,
            },
        }])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await message.delete()
    await message.client.inline.say(
        message.client, message, text,
        prefix="trivia_", buttons=buttons, chat_id=message.chat.id,
    )


async def _show_question_cb(call, q_data, category, chat_id):
    question = q_data["question"]
    correct = q_data["correct"]
    incorrect = q_data["incorrect"]
    difficulty = q_data["difficulty"]

    answers = incorrect + [correct]
    random.shuffle(answers)
    correct_index = answers.index(correct)

    diff_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}
    emoji = diff_emoji.get(difficulty, "❓")

    text = (
        f"❓ <b>Trivia ({category})</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{question}\n\n"
        f"{emoji} <b>Difficulty:</b> <code>{difficulty}</code>\n\n"
        f"Select an answer:"
    )

    via = call.client.inline.viamanager
    buttons = []
    for i, ans in enumerate(answers):
        buttons.append([{
            "text": f"{chr(65 + i)}. {html.escape(ans)}",
            "callback": _check_answer,
            "params": {
                "selected": i, "correct": correct_index,
                "category": category, "chat_id": chat_id,
            },
        }])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _check_answer(call, selected: int, correct: int,
                        category: str, chat_id: int):
    if selected == correct:
        text = "✅ <b>Correct!</b> 🎉\n\nGreat job! Want another question?"
    else:
        text = f"❌ <b>Wrong!</b>\n\nThe correct answer was: <b>{chr(65 + correct)}</b>\n\nWant to try another?"

    via = call.client.inline.viamanager
    buttons = [
        [{"text": "🔄 Another", "callback": _fetch_trivia_cb,
          "params": {"category": category, "chat_id": chat_id}}],
        [{"text": "⬅️ Categories", "callback": _back_categories,
          "params": {"chat_id": chat_id}}],
        [{"text": "🎲 Random", "callback": _random_trivia_cb,
          "params": {"chat_id": chat_id}}],
        [{"text": "🗑 Close", "callback": _close}],
    ]

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _back_categories(call, chat_id: int):
    via = call.client.inline.viamanager
    text = "❓ <b>Trivia Categories</b>\n━━━━━━━━━━━━━━━\n\nSelect a category:"
    buttons = []
    for name in CATEGORIES:
        buttons.append([{
            "text": f"❓ {name.capitalize()}",
            "callback": _fetch_trivia_cb,
            "params": {"category": name, "chat_id": chat_id},
        }])
    buttons.append([{"text": "🎲 Random", "callback": _random_trivia_cb,
                     "params": {"chat_id": chat_id}}])
    buttons.append([{"text": "🗑 Close", "callback": _close}])

    await call.edit_message(text, reply_markup=_kb(via, buttons))


async def _close(call):
    await call.edit_message("🗑 Closed")
