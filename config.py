from dotenv import load_dotenv
from os import getenv

load_dotenv()

TOKEN = getenv("token")  # Токен бота

FOLDER_ID = getenv("folder_id")  # Folder_id для gpt

IAM_TOKEN = getenv("iam_token")  # Iam токен для gpt

LOGS_PATH = "logs.log"  # Путь к файлу логов

DB_TABLE = "speech_kit.db"  # Название базы данных

MAX_USER_TTS_SYMBOLS = 1000  # Максимальное количество символов на человека

MAX_TTS_SYMBOLS = 200  # Максимальный размер ответа

ADMINS = [1645457137, 786540182]  # Список user_id админов

RUS = 'ru-RU'  # Язык текста для ГС

URL_GPT = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'  # Ссылка на яндекс gpt

MAX_USERS = 5  # Число пользователй которые могут воспользоваться ботом


