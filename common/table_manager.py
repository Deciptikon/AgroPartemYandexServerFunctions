import os
import boto3
from boto3.dynamodb.conditions import Key
from common.http_manager import return_ERROR
from constants import DATA_FIELDS, NAME_TABLES

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

def set_item(table, item: dict):
    """
    Добавляем новый элемент в таблицу (или перезаписывает существующий)
    
    :param table: Объект таблицы DynamoDB
    :param item: Словарь с ключами элемента (например, {'device_id': '123', 'name': 'I am'})
    """
    try:
        response = table.put_item(Item=item)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False
    except Exception as e:
        return None

def update_item(table, key_dict, field_name: str, new_value):
    """
    Обновляет одно поле в существующем элементе
    
    :param table: Объект таблицы DynamoDB
    :param key_dict: Словарь с ключами элемента (например, {'device_id': '123'})
    :param field_name: Название поля для обновления
    :param new_value: Новое значение
    """
    try:
        response = table.update_item(
            Key=key_dict,
            UpdateExpression=f'SET #field = :val',
            ExpressionAttributeNames={
                '#field': field_name  # Защита от зарезервированных слов
            },
            ExpressionAttributeValues={
                ':val': new_value
            },
            ReturnValues='UPDATED_NEW'  # Возвращает обновленные поля
        )
        print(f"Обновлено поле '{field_name}': {response.get('Attributes', {})}")
        return True
    except Exception as e:
        print(f"Ошибка при обновлении: {e}")
        return False

def delete_item(table, key: str, val: str):
    """
    Удаляет элемент из таблицы по ключу
    
    :param table: Объект таблицы DynamoDB
    :param key: Название ключа партиции и сортировки
    :param val: Значение удаляемого ключа партиции и сортировки
    :return: Результат операции удаления
    """
    try:
        response = table.delete_item(
            Key={key: val},
            ReturnValues='ALL_OLD'  # Возвращает удаленный элемент
        )
        return response
    except Exception as e:
        print(f"Error deleting item: {e}")
        return None

def get_user(table, user_name: str):
    if user_name == '':
        return None
    
    items = get_items(
        table = table, 
        key = DATA_FIELDS.USER_NAME, 
        val = user_name)
    
    if len(items) == 1:
        return items[0]
    else:
        return None

def get_device(table, serial_key: str):
    if serial_key == '':
        return None
    
    items = get_items(
        table = table, 
        key = DATA_FIELDS.SERIAL_KEY, 
        val = serial_key)
    
    if len(items) == 1:
        return items[0]
    else:
        return None
    
def get_track(table, track_key: str):
    if track_key == '':
        return None
    
    items = get_items(
        table = table, 
        key = DATA_FIELDS.TRACK_KEY, 
        val = track_key)
    
    if len(items) == 1:
        return items[0]
    else:
        return None

# Добавление записи в строковую структуру
def append_in_string_data(string_struct: str, key: str, val: any):
    if len(key) == 0:
        return string_struct
    
    if not string_struct or len(string_struct) == 0:
        struct = {}
        struct[key] = val
        return str(struct)
    
    struct = eval(string_struct)
    struct[key] = val
    return str(struct)

# Удаление записи из строковой структуры
def delete_from_string_data(strind_struct: str, key: str):
    if len(key) == 0:
        return strind_struct

    struct = eval(strind_struct)
    if key not in struct.keys():
        return strind_struct
    
    del struct[key]
    return str(struct)
