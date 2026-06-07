from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
import sqlite3
import google.generativeai as genai

BOT_TOKEN = "8573659438:AAGLCAKbclFYMjtYfybJcWy1GqZtv5iQixU"
GEMINI_KEY = "AQ.Ab8RN6KvXq4_xPlza6bi6cMeYTMS-LrNQKVXBi5fgBx9hOf8pw"

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

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
    return [{"role": r, "parts": [c]} for r, c in reversed(rows)]

def save_message(user_id, role, content):
    conn = sqlite3.connect("/app/data/memory.db")
    conn.execute("INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
    conn.commit()
    conn.close()

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
    save_message(user_id, "user", message.text)
    history = get_history(user_id)
    chat = model.start_chat(history=history[:-1])
    response = chat.send_message(message.text)
    reply = response.text
    save_message(user_id, "model", reply)
    await message.answer(reply)

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
