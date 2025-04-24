import os
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
import json 

# Валидация серийного номера
def is_valid_serial(query_string):
    if 'serial' in query_string and len(query_string['serial']) > 0:
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
    a = is_valid_serial(p)
    print(a)
    b = is_valid_sig(p)
    print(b)
    c = is_valid_time(p)
    print(c)

    # Если все параметры валидны
    if a and b and c :
        print(p['serial'])
        
        # Получаем таблицу
        table = get_table('waiting-table')


        print("Читаем данные")# [{'serial': '00000-12345-67890', 'timestamp': '20250411153130'}]
        res = table.query(
            KeyConditionExpression=Key('serial').eq(p['serial'])
        )
        items = res.get('Items', [])  # Список всех записей с этим serial
        print(items)
        
        # Генерируем timestamp
        curtime = datetime.now()
        timestamp = curtime.strftime('%Y%m%d%H%M%S')
        
        # Записываем данные в таблицу
        try:
            response = table.put_item(
                Item={
                    'serial': p['serial'],
                    'timestamp': timestamp #p['timestamp']
                }
            )
            
            # Возвращаем успешный ответ
            return answer_to_web(200, 'Данные успешно записаны', data = {
                        'serial': p['serial'],
                        'timestamp': timestamp
                    })
        
        except Exception as e:
            # Возвращаем ошибку, если запись в БД не удалась
            return answer_to_web(500, 'Ошибка при записи данных в БД', data = str(e))
    
    else:
        # Возвращаем ошибку, если параметр 'name' отсутствует или пуст
        return answer_to_web(400, 'Параметры отсутствуют или пусты')
    