from common.constants import (
    NAME_TABLES,
    DATA_FIELDS,
)
from common.validation_manager import (
    is_valid_serial_key,
    is_valid_sign,
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
    get_track,
    append_in_string_data,
    delete_from_string_data,
)
from common.datetime_manager import (
    create_timestamp,
    datetime_diff, # по хорошему, нужно проверить срок действия secret_key
)
from common.crypto_manager import (
    generate_signature,
)

def handler(event, context):
    print("-----------------------------")
    
    # Получаем параметры запроса
    p = event.get('queryStringParameters', {})
    print(p)


    ########## Проверяем валидность всех параметров ##########
    if (
        not is_valid_serial_key(p)
        or not is_valid_sign(p)
        or not is_valid_timestamp(p)
    ):
        return return_ERROR()
    
    # Генерируем timestamp
    timestamp = create_timestamp()
    
    # Получаем таблицу устройства
    device_table = get_table(NAME_TABLES.DEVICE_TABLE)
    print("Читаем данные")
    
    device = get_device(table=device_table, serial_key=p[DATA_FIELDS.SERIAL_KEY])
    print(device)

    if not device:
        return return_ERROR()

    # получаем секретный ключ этого устройства и проверяем подпись
    local_secret_key = device.get(DATA_FIELDS.SECRET_KEY)
    if not is_valid_sign(p, secret_key = local_secret_key):
        return return_ERROR()
    
    list_tracks = device.get(DATA_FIELDS.LIST_TRACKS)
    track_key = f"{timestamp}_{p[DATA_FIELDS.SERIAL_KEY]}"

    # Получаем таблицу треков
    track_table = get_table(NAME_TABLES.TRACK_TABLE)

    point = {
            DATA_FIELDS.TRACK_LAT: p.get(DATA_FIELDS.TRACK_LAT),
            DATA_FIELDS.TRACK_LON: p.get(DATA_FIELDS.TRACK_LON)
    }

    if not list_tracks:
        # Если треков нет, инициализируем
        list_tracks = {}
    else:
        list_tracks = eval(list_tracks)

    near_track = None
    min_time = 3600
    # ищем ближайший трек
    for key in list_tracks.keys():
        t = datetime_diff(
                start_date_str=str(list_tracks[key][DATA_FIELDS.TIMESTAMP]),
                end_date_str=timestamp
            )
        print("time = ", t)
        if t < min_time:
            # Здесь же можно добавить и ограничение 
            # на максимальное отклонение от начальной точки...
            near_track = key
            min_time = t
    
    # Если ближайший трек обнаружен
    if near_track:
        track_data = get_track(table=track_table, track_key=near_track)
        if not track_data:
            return return_ERROR()
        
        track = eval(track_data.get(DATA_FIELDS.GPS_DATA))# ПОТЕНЦИАЛЬНАЯ УЯЗВИМОСТЬ
        
        # добавляем новую точку
        track[str(p.get(DATA_FIELDS.TRACK_TIME))] = point

        # Дописываем информацию в таблицу трека
        if not update_item(
            table=track_table, 
            key_dict={DATA_FIELDS.TRACK_KEY: str(near_track)},
            field_name=DATA_FIELDS.GPS_DATA,
            new_value=str(track)
        ):
            return return_ERROR()
        
        # увеличиваем длину трека на 1
        lent = int(list_tracks[near_track][DATA_FIELDS.LENGTH_TRACK])
        list_tracks[near_track] = {
            DATA_FIELDS.TIMESTAMP: str(timestamp),
            DATA_FIELDS.TRACK_LAT: p.get(DATA_FIELDS.TRACK_LAT),
            DATA_FIELDS.TRACK_LON: p.get(DATA_FIELDS.TRACK_LON),
            DATA_FIELDS.LENGTH_TRACK: str(lent + 1)
        }
        # Обновляем информацию о самом треке
        if not update_item(
            table=device_table, 
            key_dict={DATA_FIELDS.SERIAL_KEY: str(p[DATA_FIELDS.SERIAL_KEY])},
            field_name=DATA_FIELDS.LIST_TRACKS,
            new_value=str(track)
        ):
            return return_ERROR()
        
        return return_SUCCESS()
    
    # Если ближайшего нет, создаём новый
    list_tracks[track_key] = {
        DATA_FIELDS.TIMESTAMP: str(timestamp),
        DATA_FIELDS.TRACK_LAT: p.get(DATA_FIELDS.TRACK_LAT),
        DATA_FIELDS.TRACK_LON: p.get(DATA_FIELDS.TRACK_LON),
        DATA_FIELDS.LENGTH_TRACK: str(1)
    }

    # Добавляем трек в список
    if not update_item(
        table=device_table, 
        key_dict={DATA_FIELDS.SERIAL_KEY: str(p[DATA_FIELDS.SERIAL_KEY])},
        field_name=DATA_FIELDS.LIST_TRACKS,
        new_value=str(list_tracks)
    ):
        return return_ERROR()
    
    track = {
        p.get(DATA_FIELDS.TRACK_TIME): point,
    }

    item = {
        DATA_FIELDS.TRACK_KEY: str(track_key),
        DATA_FIELDS.SERIAL_KEY: str(p[DATA_FIELDS.SERIAL_KEY]),
        DATA_FIELDS.GPS_DATA: str(track)
    }

    # Добавляем трек в таблицу
    if not set_item(table=track_table, item=item):
        return return_ERROR()
    
    return return_SUCCESS()




