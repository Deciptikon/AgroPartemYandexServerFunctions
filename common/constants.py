from dataclasses import dataclass


# Класс для сообщений
@dataclass(frozen=True)
class HttpCodes:
    CODE: int = 0
    MESSAGE: str = 'null'

HTTP_SUCCESS = HttpCodes(CODE=int(200), MESSAGE="Success.")
HTTP_ERROR = HttpCodes(CODE=int(400), MESSAGE="Error.")


# Названия всех полей 
@dataclass(frozen=True)
class DataFields:
    USER_NAME: str = 'user_name'
    USER_PASSWORD: str = 'user_password'
    USER_NIKNAME: str = 'user_nikname'
    SECRET_KEY: str = 'secret_key'
    SERIAL_KEY: str = 'serial_key'
    BIND_KEY: str = 'bind_key'
    TIMESTAMP: str = 'timestamp'
    SIGN: str = 'sign'
    DELETE_DEVICE: str = 'delete_device'
    BIND_DEVICE: str = 'bind_device'
    CHECK_BIND_KEY: str = 'check_bind_key'
    GET_LIST_DEVICES: str = 'get_list_devices'
    GET_LIST_TRACKS: str = 'get_list_tracks'
    LIST_DEVICES: str = 'list_devices'
    LIST_TRACKS: str = 'list_tracks'
    TRACK_KEY: str = 'track_key'
    TRACK_LAT: str = 'track_lat'
    TRACK_LON: str = 'track_lon'
    TRACK_TIME: str = 'track_time'
    GPS_DATA: str = 'gps_data'
    LENGTH_TRACK: str = 'length_track'

DATA_FIELDS = DataFields()


# Формат даты
DATE_FORMAT = '%Y%m%d%H%M%S'


# названия таблиц
@dataclass(frozen=True)
class NameTables:
    USER_TABLE: str = 'user-table'
    WAITING_TABLE: str = 'waiting-table'
    DEVICE_TABLE: str = 'device-table'
    TRACK_TABLE: str = 'track-table'

NAME_TABLES = NameTables()


