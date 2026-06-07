from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
import sqlite3
import aiohttp

BOT_TOKEN = "8573659438:AAGLCAKbclFYMjtYfybJcWy1GqZtv5iQixU"
GEMINI_KEY = "AQ.Ab8RN6JzQacjeR9beIAz47kf4N7zFWuD8cXL4XWl1v4dgpifqQ"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def init_db():
    conn = sqlite3.connect("/app/data/memory.db")
    conn.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, role TEXT, content TEXT)")
    conn.commit()
    conn.close()

def get_history(user_id):
    conn = sqlite3.connect("/app/data/memory.db")
    cursor = conn.execute("SELECT role, content FROM messages WHERE user_id=? ORDER BY id DESC LIMIT 50", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def save_message(user_id, role, content):
    conn = sqlite3.connect("/app/data/memory.db")
    conn.execute("INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
    conn.commit()
    conn.close()

async def ask_gemini(history, user_text):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + GEMINI_KEY
    contents = []
    for role, content in history:
        gemini_role = "user" if role == "user" else "model"
        contents.append({"role": gemini_role, "parts": [{"text": content}]})
    contents.append({"role": "user", "parts": [{"text": user_text}]})
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"contents": contents}) as resp:
            data = await resp.json()
            result = data["candidates"]
            return result[0]["content"]["parts"][0]["text"]

@dp.message(Command("clear"))
async def clear_history(message: types.Message):
    conn = sqlite3.connect("/app/data/memory.db")
    conn.execute("DELETE FROM messages WHERE user_id=?", (message.from_user.id,))
    conn.commit()
    conn.close()
    await message.answer("История очищена!")

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    history = get_history(user_id)
    save_message(user_id, "user", message.text)
    reply = await ask_gemini(history, message.text)
    save_message(user_id, "assistant", reply)
    await message.answer(reply)

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
