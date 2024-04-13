import requests
from config import IAM_TOKEN, FOLDER_ID, RUS, URL_GPT


def text_to_speech(text: str):

    # Аутентификация через IAM-токен
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
    }
    data = {
        'text': text,  # текст, который нужно преобразовать в голосовое сообщение
        'lang': RUS,
        'voice': 'filipp',  # голос Филлипа
        'folderId': FOLDER_ID,
    }
    # Выполняем запрос
    response = requests.post(
        url=URL_GPT,
        headers=headers,
        data=data)

    if response.status_code == 200:
        return True, response.content  # Возвращаем голосовое сообщение
    else:
        return False, "При запросе в SpeechKit возникла ошибка"


