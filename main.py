from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from groq import Groq
import asyncio

BOT_TOKEN = "8573659438:AAGLCAKbclFYMjtYfybJcWy1GqZtv5iQixU"
GROQ_KEY = "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"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_KEY)

@dp.message()
async def handle_message(message: types.Message):
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": message.text}]
    )
    await message.answer(response.choices[0].message.content)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
