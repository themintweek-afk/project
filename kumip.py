import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

# --- КОНФИГУРАЦИЯ ---
API_TOKEN = '8200955458:AAFxaLvxWWIf80Oow-H2bBAz6esY5YOuSz4'
ADMIN_ID = '8353076802' # Твой личный ID
CHANNEL_ID = '-1003604960312' # ID твоего канала

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- ЛОГИКА ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Пришли мне текст, фото или видео, и я отправлю это на модерацию анонимно.")

# Обработка ЛЮБОГО контента (текст, фото, видео, анимация) в личке
@dp.message(F.chat.type == "private", (F.text | F.photo | F.video | F.animation))
async def handle_anon_content(message: types.Message):
    # Создаем кнопки
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Опубликовать", callback_data="approve"))
    builder.add(InlineKeyboardButton(text="❌ Отклонить", callback_data="reject"))

    # Сначала уведомляем админа, что пришел новый запрос
    await bot.send_message(ADMIN_ID, "📩 **Новое сообщение на модерацию:**")

    # Копируем само сообщение админу с кнопками
    # copy_to сохраняет описание (caption) у фото/видео и само медиа
    await message.copy_to(
        chat_id=ADMIN_ID,
        reply_markup=builder.as_markup()
    )
    
    await message.answer("Принято! Ваше сообщение отправлено на модерацию. 🤫")

# Обработка кнопок модерации
@dp.callback_query(F.data.in_({"approve", "reject"}))
async def process_moderation(callback: types.CallbackQuery):
    # Если нажали "Опубликовать"
    if callback.data == "approve":
        # Копируем сообщение из чата админа прямо в канал (без кнопок)
        await callback.message.copy_to(chat_id=CHANNEL_ID)
        
        # Обновляем сообщение у админа, чтобы он видел результат
        await callback.message.edit_reply_markup(reply_markup=None) # Убираем кнопки
        await bot.send_message(ADMIN_ID, "✅ Опубликовано в канал.")
    
    # Если нажали "Отклонить"
    else:
        await callback.message.delete() # Удаляем само сообщение из чата админа
        await bot.send_message(ADMIN_ID, "❌ Сообщение отклонено и удалено.")
    
    await callback.answer()

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
