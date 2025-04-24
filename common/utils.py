import os
import boto3
from boto3.dynamodb.conditions import Key
import json 
from datetime import datetime
from dateutil.relativedelta import relativedelta  # pip install python-dateutil
import hashlib
import secrets
import string

HTTP_SUCCESS = 200
HTTP_ERROR = 400

def datetime_diff(start_date_str, end_date_str, unit='seconds'):
    """
    Вычисляет разницу между двумя датами в заданных единицах.
    
    Параметры:
        start_date_str (str): Начальная дата в формате '%Y%m%d%H%M%S'.
        end_date_str (str): Конечная дата в формате '%Y%m%d%H%M%S'.
        unit (str): Единица измерения ('seconds', 'minutes', 'hours', 'days', 'months', 'years').
    
    Возвращает:
        int/float: Разница в указанных единицах.
    """
    # Парсим строки в datetime объекты
    date_format = '%Y%m%d%H%M%S'
    start_date = datetime.strptime(start_date_str, date_format)
    end_date = datetime.strptime(end_date_str, date_format)
    
    # Вычисляем разницу
    delta = end_date - start_date  # Для дней, секунд
    rd = relativedelta(end_date, start_date)  # Для месяцев, лет
    
    # Возвращаем результат в нужных единицах
    if unit == 'seconds':
        return delta.total_seconds()
    elif unit == 'minutes':
        return delta.total_seconds() / 60
    elif unit == 'hours':
        return delta.total_seconds() / 3600
    elif unit == 'days':
        return delta.days
    elif unit == 'months':
        return rd.months + (rd.years * 12)
    elif unit == 'years':
        return rd.years + (rd.months / 12)
    else:
        raise ValueError("Неподдерживаемая единица измерения. Используйте: 'seconds', 'minutes', 'hours', 'days', 'months', 'years'")

# Валидация имени пользователя
def is_valid_user_name(query_string):
    if 'user_name' in query_string and len(query_string['user_name']) > 0:
        return True
    else:
        return False

# Валидация пароля
def is_valid_user_password(query_string):
    if 'user_password' in query_string and len(query_string['user_password']) > 0:
        return True
    else:
        return False

# Валидация серийного номера
def is_valid_serial_key(query_string):
    if 'serial_key' in query_string and len(query_string['serial_key']) > 0:
        return True
    else:
        return False

# Валидация подписи
def is_valid_sign(query_string: str, secret_key: str = None):
    if 'sign' in query_string and len(query_string['sign']) > 0:
        if secret_key:
            # нужно отбросить sign,
            # создать локальную подпись с secret_key, 
            # сравнить обе подписи
            return False
        else:
            return True
    else:
        return False

# Валидация временной метки
def is_valid_timestamp(query_string):
    if 'timestamp' in query_string and len(query_string['timestamp']) > 0:
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

# Успешный ответ сервера
def return_SUCCESS(data = ''):
    return answer_to_web(HTTP_SUCCESS, "Success.", data)

# Ошибка сервера
def return_ERROR(data = ''):
    return answer_to_web(HTTP_ERROR, "Error.", data)

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

def get_items(table, key: str, val: str):
    res = table.query(
        KeyConditionExpression=Key(key).eq(val)
    )
    return res.get('Items', [])  # Список всех записей с значением val по ключу key