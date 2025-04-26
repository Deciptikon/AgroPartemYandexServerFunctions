import json 
from urllib.parse import quote

from constants import (
    HTTP_SUCCESS,
    HTTP_ERROR
)

# Ответ от сервера
def answer_to_web(code: int, message: str, data = ''):
    return {
            'statusCode': code,
            'body': json.dumps({
                'code': code,
                'message': message,
                'data': data
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

# Успешный ответ сервера
def return_SUCCESS(data = ''):
    return answer_to_web(HTTP_SUCCESS.CODE, HTTP_SUCCESS.MESSAGE, data)

# Ошибка сервера
def return_ERROR(data = ''):
    return answer_to_web(HTTP_ERROR.CODE, HTTP_ERROR.MESSAGE, data)

# Парсинг query-строки из url
def build_sorted_query_string(params, exclude_key='sign'):
    """
    Собирает query-строку для подписи, исключая указанный ключ
    :param params: dict - параметры запроса
    :param exclude_key: str - ключ, который нужно исключить (обычно 'sign' или 'signature')
    :return: str - строка вида "key1=value1&key2=value2"
    """
    sorted_keys = sorted(params.keys())  # Сортируем ключи по алфавиту
    query_parts = []
    
    for key in sorted_keys:
        if key == exclude_key:
            continue  # Пропускаем ключ подписи
        
        value = params[key]
        # Экранируем и добавляем пару ключ=значение
        query_parts.append(f"{quote(key)}={quote(str(value))}")
    
    return "&".join(query_parts)  # Объединяем через &

