import asyncio
import io
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from google import genai
from google.genai import types as genai_types
from PIL import Image

# API kalitlarni Railway o'zgaruvchilaridan olamiz
# E'tibor bering: Railway'da BOT_TOKEN deb kiritgansiz
TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN", "8790403365:AAHJNDNe5bBl_sG2aPeJozY8IEBTY4BIZpQ")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6LoRoJR1NUtG5F0H7Wr2w2Tmc5m3T1KzwNwLj8T_TDEtw")

bot = Bot(token=8790403365:AAHJNDNe5bBl_sG2aPeJozY8IEBTY4BIZpQ)
dp = Dispatcher()
ai_client = genai.Client(api_key=AQ.Ab8RN6LoRoJR1NUtG5F0H7Wr2w2Tmc5m3T1KzwNwLj8T_TDEtw)

user_chats = {}

SYSTEM_INSTRUCTION = (
    "Siz ChatGPT, Claude va Gemini kabi o'ta aqlli, do'stona va har tomonlama yordam beruvchi "
    "AI yordamchisiz. Foydalanuvchi bilan o'zbek tilida ravon, aniq va tushunarli muloqot qiling. "
    "Dasturlash, matn yozish, tahlil qilish va umumiy savollarga professional darajada javob bering."
)

def get_or_create_chat(user_id: int):
    if user_id not in user_chats:
        user_chats[user_id] = ai_client.chats.create(
            model="gemini-1.5-flash",
            config=genai_types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION
            )
        )
    return user_chats[user_id]

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_chats[user_id] = ai_client.chats.create(
        model="gemini-1.5-flash",
        config=genai_types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION
        )
    )
    await message.answer(
        f"Salom, {message.from_user.first_name}! Assalomu alaykum.\n\n"
        "Men sizning shaxsiy AI yordamchingizman. Menga xohlagan matnli savolingizni berishingiz "
        "yoki rasm yuborishingiz mumkin. Suhbat tarixini tozalash uchun /clear buyrug'ini yuboring."
    )

@dp.message(Command("clear"))
async def clear_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_chats:
        del user_chats[user_id]
    await message.answer("Suhbat xotirasi tozalandi! Yangi savolingizni berishingiz mumkin.")

@dp.message(lambda msg: msg.photo)
async def photo_handler(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        image = Image.open(io.BytesIO(downloaded_file.read()))
        
        prompt = message.caption if message.caption else "Bu rasmda nima tasvirlangan? Batafsil tushuntirib ber."
        
        response = ai_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[image, prompt],
            config=genai_types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION
            )
        )
        await message.answer(response.text)
    except Exception as e:
        await message.answer("Kechirasiz, rasmni tahlil qilishda xatolik yuz berdi.")
        print(f"Xatolik: {e}")

@dp.message()
async def text_handler(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        chat = get_or_create_chat(message.from_user.id)
        response = chat.send_message(message.text)
        await message.answer(response.text)
    except Exception as e:
        await message.answer("Kechirasiz, xatolik yuz berdi. Qaytadan urinib ko'ring.")
        print(f"Xatolik: {e}")

async def main():
    print("AI Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
