import json 
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

