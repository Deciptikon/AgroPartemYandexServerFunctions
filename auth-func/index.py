import os
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
import json 

import hashlib
import secrets
import string

# Валидация имени пользователя
def is_valid_user_name(query_string):
    if 'user_name' in query_string and len(query_string['user_name']) > 0:
        return True
    else:
        return False

# Валидация пароля
def is_valid_user_password(query_string):
    if 'user_pass' in query_string and len(query_string['user_pass']) > 0:
        return True
    else:
        return False

# Валидация подписи
def is_valid_sig(query_string):
    if 'sig' in query_string and len(query_string['sig']) > 0:
        return True
    else:
        return False

# Валидация временной метки
def is_valid_time(query_string):
    if 'time' in query_string and len(query_string['time']) > 0:
        return True
    else:
        return False

# Генератор секретного ключа
def generate_secret_key(length: int = 64) -> str:
    """
    Генерирует криптографически безопасный секретный ключ из букв и цифр.
    
    :param length: Длина ключа (по умолчанию 64 символа)
    :return: Случайная строка из букв и цифр
    """
    if length < 8:
        raise ValueError("Длина ключа должна быть не менее 8 символов")
    
    alphabet = string.ascii_letters + string.digits  # Буквы (A-Z, a-z) + цифры (0-9)
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# подпись к строке
def generate_signature(unsigned_url: str, secret_key: str) -> str:
    """
    Генерирует SHA-256 подпись URL в hex-формате
    
    :param unsigned_url: URL без подписи
    :param secret_key: Секретный ключ из API_CONFIG.SECRET_KEY
    :return: Подпись в hex
    """
    text = unsigned_url + secret_key
    # Создаем SHA-256 хеш
    sha256_hash = hashlib.sha256(text.encode('utf-8'))
    # Получаем hex-представление
    return sha256_hash.hexdigest()

# генерируем timestamp
def create_timestamp():
    curtime = datetime.now()
    timestamp = curtime.strftime('%Y%m%d%H%M%S')
    return timestamp

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

# Получение таблицы
def get_table(table_name):
    # Подключаемся к DynamoDB
    ydb_docapi_client = boto3.resource(
        'dynamodb', 
        endpoint_url=os.getenv('ENDPOINT_URL'),
        region_name=os.getenv('REGION_NAME'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    return ydb_docapi_client.Table(table_name)

def handler(event, context):
    print("-----------------------------")
    
    # Получаем параметры запроса
    p = event.get('queryStringParameters', {})
    print(p)
    
    # Проверяем валидность всех параметров
    a = is_valid_user_name(p)
    print(a)
    #b = is_valid_sig(p)
    #print(b)
    #c = is_valid_time(p)
    #print(c)

    # Если все параметры валидны
    if a:
        print(p['user_name'])
        
        # Получаем таблицу
        table = get_table('user-table')


        print("Читаем данные")
        res = table.query(
            KeyConditionExpression=Key('user_name').eq(p['user_name'])
        )
        items = res.get('Items', [])  # Список всех записей с этим serial
        print(items)

        if len(items) == 0:
            # если записей нет, регестрируем нового пользователя
            print("регестрируем нового пользователя")

            # Генерируем timestamp
            timestamp = create_timestamp()

            new_item = {
                'user_name': p['user_name'],
                'user_pass': p['user_pass'],
                'timestamp': timestamp,
                'user_nikname': 'User_' + timestamp
            }

            try:
                response = table.put_item(Item = new_item)
            
                # Возвращаем успешный ответ
                return answer_to_web(200, 'Регистрация успешна', data = new_item)
        
            except Exception as e:
                # Возвращаем ошибку, если запись в БД не удалась
                return answer_to_web(500, 'Ошибка регистрации', data = str(e))

        else:
            # если запись есть, проверяем пароль
            print("запись есть, проверяем пароль")
            
            save_pass = items[0]['user_pass']
            if save_pass == p['user_pass']:
                # пароли совпадают, передаём информацию пользователю
                print("пароли совпадают")
                # генерируем векретный ключ
                token = generate_secret_key(64)

                timestamp = create_timestamp()

                # формируем ответ
                item = {
                    'user_name': str(items[0]['user_name']),
                    'user_pass': str(items[0]['user_pass']),
                    'timestamp': str(timestamp),
                    'user_nikname': str(items[0]['user_nikname']),
                    'token': str(token)
                }
                print(item)

                # записываем токен и время его создания в текущего пользователя
                try:
                    response = table.put_item(Item = item)
            
                    # Если запись прошла успешно, возвращаем успешный ответ с новым токеном
                    return answer_to_web(200, 'Авторизация успешна', data = item)
        
                except Exception as e:
                # Возвращаем ошибку, если запись в БД не удалась
                    return answer_to_web(500, 'Ошибка авторизации', data = str(e))

            else:
                # пароли не совпадают, отправляем ошибку
                print("пароли не совпадают")
                return answer_to_web(401, 'Ошибка авторизации')
                
    else:
        # Возвращаем ошибку, если параметр 'name' отсутствует или пуст
        return answer_to_web(400, 'Параметры отсутствуют или пусты')
    