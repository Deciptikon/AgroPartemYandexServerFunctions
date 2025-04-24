from common.constants import (
    HTTP_SUCCESS,
    HTTP_ERROR
)
from common.validation_manager import (
    is_valid_user_name,
    is_valid_serial_key,
    is_valid_sign,
    is_valid_timestamp,
)
from common.http_manager import (
    answer_to_web,
    return_SUCCESS,
    return_ERROR,
)
from common.table_manager import (
    get_table,
    get_items,
)
from common.datetime_manager import (
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
        return return_ERROR()

    # получаем доступ к данным пользователя
    table = get_table('user-table')
    print("Читаем данные")

    # Список всех записей с этим user_name
    items = get_items(table=table, key='user_name', val=p['user_name'])  
    print(items)

    if len(items) == 0:
        # если записей нет, Ошибка.
        print("Пользователь не обнаружен")
        return return_ERROR()
    
    # Если пользователь найден
    user_data = items[0]
    local_secret_key = user_data.secret_key
    
    if not is_valid_sign(p, secret_key = local_secret_key):
        return return_ERROR()
    
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
        # получаем список устройств пользователя
        list_devices = {
            '12345-67890-RTYBV': {
                'name': "TestName"
                },
            '2G3J6-228GT-QNI85': {
                'name': "Опрыскиватель"
                },
            '00000-ABCDE-1A2B0': {
                'name': "Новый 777"
                }
            }
        data = {
            'user_name': 'VolodyaFarmer',
            'list_devices': list_devices
        }
        return answer_to_web(HTTP_SUCCESS['code'], HTTP_SUCCESS['message'], data = data)
    
    # Если пользователь запрашивает удаление устройства serial_key
    if p.get('delete_device'):
        # проверяем, существует ли привязанное устройство с serial_key
        pass

    # Если все параметры валидны, но ничего не запрашивается
    return return_SUCCESS()
    
