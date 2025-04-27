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
    delete_item,
    get_table,
    get_items,
    get_user,
    get_device,
    update_item,
)
from common.datetime_manager import (
    create_timestamp,
    datetime_diff,
)
from common.crypto_manager import (
    generate_secret_key,
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
        or not is_valid_sign(p)
    ):
        return return_ERROR()

    # получаем доступ к данным пользователя
    user_table = get_table(NAME_TABLES.USER_TABLE)
    print("Читаем данные")

    # Если пользователь найден
    user_data = get_user(table=user_table, user_name=p[DATA_FIELDS.USER_NAME] )
    if not user_data:
        return return_ERROR()
    
    local_secret_key = user_data.get(DATA_FIELDS.SECRET_KEY)
    
    if not is_valid_sign(p, secret_key = local_secret_key):
        return return_ERROR()
    
##########       Если все данные валидны       ##########
    
    # Если пользователь инициирует процедуру привязки
    if p.get(DATA_FIELDS.BIND_DEVICE):
        # Получаем таблицу ожидания
        waiting_table = get_table(NAME_TABLES.WAITING_TABLE)

        # проверяем, существует ли ожидающее устройство с serial_key
        device = get_device(table=waiting_table, serial_key=p[DATA_FIELDS.SERIAL_KEY])
        print(device)
        if not device:
            return return_ERROR()
        
        # генерируем ключ привязки и записываем в ожидающее устройство
        bind_key = generate_secret_key(6)

        if update_item(
                table=waiting_table, 
                key_dict={DATA_FIELDS.SERIAL_KEY: str(p[DATA_FIELDS.SERIAL_KEY])},
                field_name=DATA_FIELDS.BIND_KEY,
                new_value=str(bind_key)
        ):
            return return_SUCCESS()
        else:
            return return_ERROR()

    # Если пользователь запрашивает проверку ключа привязки
    if p.get(DATA_FIELDS.CHECK_BIND_KEY):
        # Получаем таблицу ожидания
        waiting_table = get_table(NAME_TABLES.WAITING_TABLE)

        # проверяем, существует ли ожидающее устройство с serial_key
        device = get_device(table=waiting_table, serial_key=p[DATA_FIELDS.SERIAL_KEY])
        print(device)
        if not device:
            return return_ERROR()
        
        # проверяем, валиден ли bind_key
        bind_key = p.get(DATA_FIELDS.BIND_KEY)
        if not bind_key:
            return return_ERROR()
        
        local_bind_key = device.get(DATA_FIELDS.BIND_KEY)
        if not local_bind_key:
            return return_ERROR()
        
        if bind_key != local_bind_key:
            return return_ERROR()
        
        # Стираем ключ привязки
        if not update_item(
                table=waiting_table, 
                key_dict={DATA_FIELDS.SERIAL_KEY: str(p[DATA_FIELDS.SERIAL_KEY])},
                field_name=DATA_FIELDS.BIND_KEY,
                new_value=None
        ):
            return return_ERROR()
        
        # генерируем секретный ключ и записываем в ожидающее устройство
        # ключ 
        secret_key = generate_secret_key(length=64)
        if not update_item(
                table=waiting_table, 
                key_dict={DATA_FIELDS.SERIAL_KEY: str(p[DATA_FIELDS.SERIAL_KEY])},
                field_name=DATA_FIELDS.SECRET_KEY,
                new_value=str(secret_key)
        ):
            return return_ERROR()
        # и имя пользователя
        if not update_item(
                table=waiting_table, 
                key_dict={DATA_FIELDS.SERIAL_KEY: str(p[DATA_FIELDS.SERIAL_KEY])},
                field_name=DATA_FIELDS.USER_NAME,
                new_value=str(p[DATA_FIELDS.USER_NAME])
        ):
            return return_ERROR()
        
        return return_SUCCESS()

    # Если пользователь запрашивает список своих устройств
    if p.get(DATA_FIELDS.GET_LIST_DEVICES):
        # получаем список устройств пользователя
        ld = user_data.get(DATA_FIELDS.LIST_DEVICES)
        if not ld:
            return return_SUCCESS(data=str({}))
        list_devices = eval(ld)
        
        data = {
            DATA_FIELDS.USER_NAME: str(user_data.get(DATA_FIELDS.USER_NAME)),
            DATA_FIELDS.LIST_DEVICES: list_devices
        }
        return answer_to_web(HTTP_SUCCESS.CODE, HTTP_SUCCESS.MESSAGE, data = data)
    
    # Если пользователь запрашивает удаление устройства serial_key
    if p.get(DATA_FIELDS.DELETE_DEVICE):
        # проверяем, существует ли привязанное устройство с serial_key
        ld = user_data.get(DATA_FIELDS.LIST_DEVICES)
        if not ld:
            return return_ERROR()
        
        list_devices = eval(ld)
        if not list_devices.get(p[DATA_FIELDS.SERIAL_KEY]):
            return return_ERROR()
        
        device_table = get_table(NAME_TABLES.DEVICE_TABLE)
        device = get_device(table=device_table, serial_key=p[DATA_FIELDS.SERIAL_KEY])
        if not device:
            return return_ERROR()
        
        if p[DATA_FIELDS.USER_NAME] != device.get(DATA_FIELDS.USER_NAME):
            return return_ERROR()
        
        # Если устройство существует, удаляем его
        if not delete_item(
            table=device_table,
            key=DATA_FIELDS.SERIAL_KEY,
            val=p[DATA_FIELDS.SERIAL_KEY]
        ):
            return return_ERROR()
        
        del list_devices[p[DATA_FIELDS.SERIAL_KEY]]
        if update_item(
            table=user_table,
            key_dict={DATA_FIELDS.USER_NAME: p[DATA_FIELDS.USER_NAME]},
            field_name=DATA_FIELDS.LIST_DEVICES,
            new_value=str(list_devices)
        ):
            return return_ERROR()

        # Здесь можно было бы добавить проверку, удалились ли данные..
        return return_SUCCESS()

    # Если все параметры валидны, но ничего не запрашивается
    return return_SUCCESS()
    
