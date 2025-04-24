import os
import boto3
from datetime import datetime
import json 

from common.utils import (
    is_valid_user_name,
    is_valid_user_password,
    is_valid_serial_key,
    is_valid_sign,
    is_valid_timestamp,
    answer_to_web,
    return_SUCCESS,
    return_ERROR,
    get_table,
    get_items,
    create_timestamp,
    datetime_diff,
)

def handler(event, context):
    print("-----------------------------")
    
    # Получаем параметры запроса
    p = event.get('queryStringParameters', {})
    print(p)
    
########## Проверяем валидность всех параметров ##########
    if (
        not is_valid_user_name(p)
        or not is_valid_timestamp(p)
        or not is_valid_serial_key(p)
    ):
        return answer_to_web(400, 'Ошибка.')

    # получаем доступ к данным пользователя
    table = get_table('user-table')
    print("Читаем данные")

    # Список всех записей с этим user_name
    items = get_items(key='user_name', val=p['user_name'])  
    print(items)

    if len(items) == 0:
        # если записей нет, Ошибка.
        print("Пользователь не обнаружен")
        return answer_to_web(400, 'Ошибка.')
    
    # Если пользователь найден
    user_data = items[0]
    local_secret_key = user_data.secret_key
    
    if not is_valid_sign(p, secret_key = local_secret_key):
        return answer_to_web(400, 'Ошибка.')
    
##########       Если все данные валидны       ##########
    
    # Если пользователь инициирует процедуру привязки
    if p.get('bind_device'):
        # проверяем, существует ли ожидающее устройство с serial_key
        # генерируем ключ привязки и записываем в ожидающее устройство
        pass

    # Если пользователь запрашивает проверку ключа привязки
    if p.get('check_bind_key'):
        # проверяем, существует ли ожидающее устройство с serial_key
        # проверяем, валиден ли bind_key
        # генерируем секретный ключ и записываем в ожидающее устройство
        pass

    # Если пользователь запрашивает список своих устройств
    if p.get('get_list_devices'):
        pass
    
    # Если пользователь запрашивает удаление устройства serial_key
    if p.get('delete_device'):
        # проверяем, существует ли привязанное устройство с serial_key
        pass

    # Если все параметры валидны
    return answer_to_web(200, 'Успешно.')
    
