from common.constants import (
    NAME_TABLES,
    DATA_FIELDS,
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
    get_user,
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
    user_table = get_table(NAME_TABLES.USER_TABLE)
    print("Читаем данные")

    # Если пользователь найден
    user_data = get_user(table=user_table, user_name=p[DATA_FIELDS.USER_NAME] )
    if not user_data:
        return return_ERROR()
    
    local_secret_key = user_data.secret_key
    
    if not is_valid_sign(p, secret_key = local_secret_key):
        return return_ERROR()
    
##########       Если все данные валидны       ##########
    
    # Если пользователь инициирует процедуру привязки
    if p.get(DATA_FIELDS.BIND_DEVICE):
        # проверяем, существует ли ожидающее устройство с serial_key
        # генерируем ключ привязки и записываем в ожидающее устройство
        pass

    # Если пользователь запрашивает проверку ключа привязки
    if p.get(DATA_FIELDS.CHECK_BIND_KEY):
        # проверяем, существует ли ожидающее устройство с serial_key
        # проверяем, валиден ли bind_key
        # генерируем секретный ключ и записываем в ожидающее устройство
        pass

    # Если пользователь запрашивает список своих устройств
    if p.get(DATA_FIELDS.GET_LIST_DEVICES):
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
            DATA_FIELDS.USER_NAME: 'VolodyaFarmer',
            DATA_FIELDS.LIST_DEVICES: list_devices
        }
        return answer_to_web(HTTP_SUCCESS.CODE, HTTP_SUCCESS.MESSAGE, data = data)
    
    # Если пользователь запрашивает удаление устройства serial_key
    if p.get(DATA_FIELDS.DELETE_DEVICE):
        # проверяем, существует ли привязанное устройство с serial_key
        pass

    # Если все параметры валидны, но ничего не запрашивается
    return return_SUCCESS()
    
