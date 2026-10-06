import asyncio
import logging

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart

TOKEN = "8855052424:AAEN6FfISYMEJ0aw4WFzZ1w__v9G-_eNVd0"
ADMIN_ID = 1837808427  # твой Telegram ID

bot = Bot(TOKEN)
dp = Dispatcher()

# Здесь храним связь:
# ID сообщения у админа -> ID пользователя
message_users = {}


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "Гав!\n"
        "Отправь сюда сообщение, и собака передаст его мне."
    )


@dp.message(F.from_user.id == ADMIN_ID)
async def admin_reply(message: types.Message):
    """
    Если ты отвечаешь реплаем на сообщение бота,
    бот отправляет твой ответ исходному пользователю.
    """

    if not message.reply_to_message:
        return

    original_admin_message_id = message.reply_to_message.message_id

    user_id = message_users.get(original_admin_message_id)

    if not user_id:
        await message.answer(
            "❌ Не удалось определить получателя."
        )
        return

    try:
        # Копируем твое сообщение пользователю.
        # copy_to не показывает твой username как отправителя.
        await bot.copy_message(
            chat_id=user_id,
            from_chat_id=ADMIN_ID,
            message_id=message.message_id
        )

        await message.answer(" Собака отправила ответ.")

    except Exception as e:
        logging.exception(e)
        await message.answer(
            " Собаке не удалось отправить ответ."
        )


@dp.message(F.from_user.id != ADMIN_ID)
async def anonymous_message(message: types.Message):
    """
    Получаем сообщение от пользователя
    и отправляем его админу.
    """

    try:
        # Сначала отправляем небольшую пометку.
        info = await bot.send_message(
            ADMIN_ID,
            "<b>Собака принесла сообщение!</b>\n"
            "↩️ Ответь на это сообщение, чтобы отправить ответ пользователю.",
            parse_mode="HTML"
        )

        # Копируем оригинальное сообщение.
        copied = await bot.copy_message(
            chat_id=ADMIN_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )

        # Запоминаем, какому пользователю соответствует сообщение.
        message_users[copied.message_id] = message.from_user.id

        await message.answer(
            "Собака отправила сообщение анонимно."
        )

    except Exception as e:
        logging.exception(e)

        await message.answer(
            " Произошла ошибка при отправке сообщения."
        )


async def main():
    logging.basicConfig(level=logging.INFO)

    print("Бот запущен!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())