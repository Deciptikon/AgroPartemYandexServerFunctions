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
    get_track,
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

# Если пользователь запрашивает список треков
    if p.get(DATA_FIELDS.GET_LIST_TRACKS):
        if not p.get(DATA_FIELDS.SERIAL_KEY):
            return_ERROR()
        
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
        
        # Если устройство существует, и принадлежит пользователю
        # получаем его список треков
        list_tracks = device.get(DATA_FIELDS.LIST_TRACKS)
        if not list_tracks:
            return return_ERROR()
        
        data = {
            DATA_FIELDS.USER_NAME: p[DATA_FIELDS.USER_NAME],
            DATA_FIELDS.SERIAL_KEY: p[DATA_FIELDS.SERIAL_KEY],
            DATA_FIELDS.LIST_TRACKS: str(list_tracks)
        }
        return return_SUCCESS(data=data)
    
    # Если пользователь запрашивает получение данных трека
    if p.get(DATA_FIELDS.GET_TRACK_DATA):
        track_key = p.get(DATA_FIELDS.TRACK_KEY)
        if not track_key or len(track_key) != 32:
            return return_ERROR()
        
        track_table = get_table(NAME_TABLES.TRACK_TABLE)
        track = get_track(table=track_table, track_key=track_key)
        if not track:
            return return_ERROR()
        
        return return_SUCCESS(data=track)

    return return_SUCCESS()