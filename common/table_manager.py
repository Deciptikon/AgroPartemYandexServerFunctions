import os
import boto3
from boto3.dynamodb.conditions import Key
from common.constants import NAME_TABLES

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

def get_user(table, user_name: str):
    if user_name == '':
        return None
    
    items = get_items(
        table = table, 
        key = NAME_TABLES.USER_TABLE, 
        val = user_name)
    
    if len(items) == 1:
        return items[0]
    else:
        return None