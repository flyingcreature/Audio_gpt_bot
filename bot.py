import telebot

from telebot.types import Message, ReplyKeyboardRemove

from config import TOKEN, MAX_USER_TTS_SYMBOLS, MAX_TTS_SYMBOLS, ADMINS, LOGS_PATH, MAX_USERS
from utils import create_keyboard, logging

from database import create_table, create_db, add_user, insert_row, count_all_symbol, is_user_in_db, get_all_users_data

from speechkit import text_to_speech

bot = telebot.TeleBot(TOKEN)

create_db()
create_table()


@bot.message_handler(commands=["start"])
def start(message):
    user_name = message.from_user.username
    user_id = message.chat.id

    if not is_user_in_db(user_id):  # Если пользователя в базе нет
        if len(get_all_users_data()) < MAX_USERS:  # Если число зарегистрированных пользователей меньше допустимого
            add_user(
                user_id=int(user_id),
                message="",
                tts_symbols=0
            )
        else:
            text = "К сожалению, лимит пользователей исчерпан. Вы не сможете воспользоваться ботом:("

            bot.send_message(
                chat_id=user_id,
                text=text
            )
            return

    bot.send_message(
        chat_id=user_id,
        text=f"Привет, {user_name} 👋! Я бот-помощник для конвертирования твоего текста в ГС!\n"
             f"Для этого воспользуйся командной /tts.\n"
             "Если текст будет слишком большим, пожалуйста укороти его.",
        reply_markup=create_keyboard(["/tts"]),
    )


def is_tts_symbol_limit(message, text):
    user_id = message.from_user.id
    text_symbols = len(text)

    # Функция из БД для подсчёта всех потраченных пользователем символов
    all_symbols = count_all_symbol(user_id) + text_symbols

    # Сравниваем all_symbols с количеством доступных пользователю символов
    if all_symbols >= MAX_USER_TTS_SYMBOLS:
        msg = (
            f"Превышен общий лимит SpeechKit TTS {MAX_USER_TTS_SYMBOLS}."
            f" Использовано: {all_symbols} символов. Доступно: {MAX_USER_TTS_SYMBOLS - all_symbols}"
        )
        bot.send_message(
            chat_id=user_id,
            text=msg
        )
        return None

    # Сравниваем количество символов в тексте с максимальным количеством символов в тексте
    if text_symbols >= MAX_TTS_SYMBOLS:
        msg = f"Превышен лимит SpeechKit TTS на запрос {MAX_TTS_SYMBOLS}, в сообщении {text_symbols} символов"
        bot.send_message(
            chat_id=user_id,
            text=msg
        )
        return None
    return len(text)


@bot.message_handler(commands=['tts'])
def tts_handler(message):
    user_id = message.from_user.id
    bot.send_message(
        chat_id=user_id,
        text='Отправь следующим сообщением текст💬, чтобы я его озвучил!🔊'
    )
    bot.register_next_step_handler(message, tts)


def tts(message):
    user_id = message.from_user.id
    text = message.text

    # Проверка, что сообщение действительно текстовое
    if message.content_type != 'text':
        bot.send_message(
            chat_id=user_id,
            text='Отправь текстовое сообщение'
        )
        return

        # Считаем символы в тексте и проверяем сумму потраченных символов
    text_symbol = is_tts_symbol_limit(message, text)
    if text_symbol is None:
        return

    # Записываем сообщение и кол-во символов в БД
    insert_row(user_id, text, text_symbol)

    # Получаем статус и содержимое ответа от SpeechKit
    status, content = text_to_speech(text)

    # Если статус True - отправляем голосовое сообщение, иначе - сообщение об ошибке
    if status:
        bot.send_voice(
            chat_id=user_id,
            voice=content
        )
    else:
        bot.send_message(
            chat_id=user_id,
            text=content
        )


@bot.message_handler(commands=['debug'])
def send_logs(message):
    user_id = message.from_user.id
    if user_id in ADMINS:
        try:
            with open(LOGS_PATH, "rb") as f:
                bot.send_document(
                    message.chat.id,
                    f
                )
        except telebot.apihelper.ApiTelegramException:
            bot.send_message(
                chat_id=message.chat.id,
                text="Логов нет!"
            )
    else:
        print(f"{user_id} захотел посмотреть логи")
        logging.info(f"{user_id} захотел посмотреть логи")


@bot.message_handler(commands=['help'])
def help_command(message: Message):
    text = (
        "👋 Я твой цифровой собеседник.\n\n"
        "Что бы воспользоваться функцией gpt помощника 🕵‍♀️ следуй инструкциям бота .\n\n"
        "Этот бот сделан на базе нейронной сети YandexGPT.\n"
        "Это мой первый опыт знакомства с gpt, "
        "поэтому не переживай если возникла какая-то ошибка. Просто сообщи мне об этом)\n"
        "И я постараюсь её решить."
    )
    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=ReplyKeyboardRemove()
    )


def filter_hello(message):
    word = "привет"
    return word in message.text.lower()


@bot.message_handler(content_types=['text'], func=filter_hello)
def say_hello(message: Message):
    user_name = message.from_user.first_name
    bot.send_message(
        chat_id=message.chat.id,
        text=f"{user_name}, приветики 👋!"
    )


def filter_bye(message):
    word = "пока"
    return word in message.text.lower()


@bot.message_handler(content_types=["text"], func=filter_bye)
def say_bye(message: Message):
    bot.send_message(
        chat_id=message.chat.id,
        text="Пока, заходи ещё!"
    )


@bot.message_handler(func=lambda message: True, content_types=['audio', 'photo', 'voice', 'video', 'document',
                                                               'text', 'location', 'contact', 'sticker'])
def send_echo(message: Message):
    text = (
        f"Вы отправили ({message.text}).\n"
        f"Но к сожалению я вас не понял😔, для общения со мной используйте встроенные кнопки.🤗"
    )
    bot.send_message(
        chat_id=message.chat.id,
        text=text
    )


logging.info("Бот запущен")
bot.infinity_polling(timeout=60, long_polling_timeout=5)
