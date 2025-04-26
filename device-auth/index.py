from torch import P
from common.constants import (
    NAME_TABLES,
    DATA_FIELDS,
)
from common.validation_manager import (
    is_valid_serial_key,
    is_valid_sign,
    is_valid_user_name,
    is_valid_user_password,
    is_valid_timestamp,
)
from common.http_manager import (
    answer_to_web,
    return_SUCCESS,
    return_ERROR,
    build_sorted_query_string,
)
from common.table_manager import (
    get_table,
    set_item,
    update_item,
    delete_item,
    get_user,
    get_device,
    append_in_string_data,
    delete_from_string_data,
)
from common.datetime_manager import (
    create_timestamp,
    datetime_diff, # по хорошему, нужно проверить срок действия secret_key
)
from common.crypto_manager import (
    generate_secret_key,
    generate_signature,
)




def handler(event, context):
    print("-----------------------------")
    
    # Получаем параметры запроса
    p = event.get('queryStringParameters', {})
    print(p)
    
    query_string = build_sorted_query_string(params=p, exclude_key=DATA_FIELDS.SIGN)
    print(query_string)
    
    ########## Проверяем валидность всех параметров ##########
    if (
        not is_valid_serial_key(p)
        or not is_valid_sign(p)
        or not is_valid_timestamp(p)
    ):
        return return_ERROR()
    
# Если все параметры валидны

    # Генерируем timestamp
    timestamp = create_timestamp()
    
    # Получаем таблицу ожидания
    waiting_table = get_table(NAME_TABLES.WAITING_TABLE)
    print("Читаем данные")# [{'serial': '00000-12345-67890', 'timestamp': '20250411153130', ...}]
    
    device = get_device(table=waiting_table, serial_key=p[DATA_FIELDS.SERIAL_KEY])
    print(device)

# Если устройство в списке ожидания првоеряем наличие ключей
    if device:
    # Если для устройства готов ключ привязки
        bind_key = device.get(DATA_FIELDS.BIND_KEY)
        if bind_key:
            data = {
                DATA_FIELDS.SERIAL_KEY: str(p[DATA_FIELDS.SERIAL_KEY]),
                DATA_FIELDS.TIMESTAMP: str(timestamp),
                DATA_FIELDS.BIND_KEY: str(bind_key),
            }
            return answer_to_web(202, 'Start binding', data=data)
    
    # Если для устройства готов секретный ключ
        secret_key = device.get(DATA_FIELDS.SECRET_KEY)
        user_name = device.get(DATA_FIELDS.USER_NAME)
        if secret_key and user_name:
            user_table = get_table(NAME_TABLES.USER_TABLE)
            user_data = get_user(table=user_table, user_name=user_name)
            if not user_data:
                return return_ERROR()

            device_table = get_table(NAME_TABLES.DEVICE_TABLE)

            new_device_item = {
                DATA_FIELDS.SERIAL_KEY: str(p[DATA_FIELDS.SERIAL_KEY]),
                DATA_FIELDS.SECRET_KEY: str(secret_key),
                DATA_FIELDS.TIMESTAMP: str(timestamp),
                DATA_FIELDS.USER_NAME: str(user_name),
            }

            # Добавляем новое устройство в список устройств пользователя
            list_devices = append_in_string_data(
                strind_struct=user_data[DATA_FIELDS.LIST_DEVICES],
                key=p[DATA_FIELDS.SERIAL_KEY],
                val={
                    'name': 'Устройство_' + str(timestamp),
                }
            )

            # Записываем устройство в БД привязанных устройств
            if not set_item(table=device_table, item=new_device_item):
                return return_ERROR()
            
            # Записываем устройство в список устройств пользователя
            if not update_item(
                table=user_table, 
                key_dict={DATA_FIELDS.USER_NAME: str(user_data[DATA_FIELDS.USER_NAME])},
                field_name=DATA_FIELDS.LIST_DEVICES,
                new_value=str(list_devices)
            ):
                return return_ERROR()
            
            # Удаляем из списка ожидания
            if not delete_item(
                waiting_table, 
                DATA_FIELDS.SERIAL_KEY, 
                p[DATA_FIELDS.SERIAL_KEY]
            ):
                return return_ERROR()
            
            data = {
                DATA_FIELDS.SERIAL_KEY: str(p[DATA_FIELDS.SERIAL_KEY]),
                DATA_FIELDS.TIMESTAMP: str(timestamp),
                DATA_FIELDS.SECRET_KEY: str(secret_key),
            }
            return answer_to_web(201, 'Finish binding', data=data)
        
    # Если устройство в списке ожидания,
    # но не участвует в процессе привязки,
    # то просто обновляем его время активности
        if update_item(
                table=waiting_table, 
                key_dict={DATA_FIELDS.SERIAL_KEY: str(p[DATA_FIELDS.SERIAL_KEY])},
                field_name=DATA_FIELDS.TIMESTAMP,
                new_value=str(timestamp)
        ):
            return answer_to_web(300, 'Waiting, device not binding', data=device)
        else:
            return return_ERROR()

# Если устройства нет в списке ожидания
# проверяем находится ли оно в списке привязанных устройств
    device_table = get_table(NAME_TABLES.DEVICE_TABLE)
    device = get_device(table=device_table, serial_key=p[DATA_FIELDS.SERIAL_KEY])
    print(device)

# Если устройство уже в списке привязанных
    if device:
        # Проверяем корректность его secret_key #########################################################
        local_secret_key = device.get(DATA_FIELDS.SECRET_KEY)
        if not local_secret_key:
            return return_ERROR()
        
        # Генерируем подпись к присланным данным от пользователя
        local_sign = generate_signature(
            unsigned_url=build_sorted_query_string(
                params=p, 
                exclude_key=DATA_FIELDS.SIGN
                ),
            secret_key=local_secret_key
        )
        print('Local Sign: ', local_sign)

        # Если подписи совпадают, значит устройство привязано
        if local_sign != p[DATA_FIELDS.SIGN]:
            return return_ERROR()
        
        return return_SUCCESS()

# Если устройства нет, ни в списке ожидания, ни в списке привязанных устройств
# то помещаем его в список ожидающих привязки
    device = {
        DATA_FIELDS.SERIAL_KEY: str(p[DATA_FIELDS.SERIAL_KEY]),
        DATA_FIELDS.TIMESTAMP: str(timestamp)
    }
    
    # Записываем устройство в таблицу ожидания
    if set_item(table=waiting_table, item=device):
        return answer_to_web(300, 'Waiting, device not binding', data=device)
    else:
        return return_ERROR()
    

    