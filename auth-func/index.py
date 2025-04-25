from common.constants import (
    NAME_TABLES,
    DATA_FIELDS,
)
from common.validation_manager import (
    is_valid_user_name,
    is_valid_user_password,
    is_valid_timestamp,
)
from common.http_manager import (
    return_SUCCESS,
    return_ERROR,
)
from common.table_manager import (
    get_table,
    get_user,
)
from common.datetime_manager import (
    create_timestamp,
    datetime_diff, # по хорошему, нужно проверить срок действия secret_key
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
        or not is_valid_user_password(p)
    ):
        return return_ERROR()

    # Получаем таблицу
    user_table = get_table(NAME_TABLES.USER_TABLE)

    # Если пользователь найден
    user_data = get_user(table=user_table, user_name=p[DATA_FIELDS.USER_NAME] )
    if not user_data:
# Если пользователь не существует, 
# регистрируем нового пользователя
        timestamp = create_timestamp()
        new_item = {
            DATA_FIELDS.USER_PASSWORD: str(p[DATA_FIELDS.USER_PASSWORD]),
            DATA_FIELDS.USER_NIKNAME: str('User_' + timestamp),
            DATA_FIELDS.TIMESTAMP: str(timestamp),
            DATA_FIELDS.USER_NAME: str(p[DATA_FIELDS.USER_NAME]),
        }
        try:
            response = user_table.put_item(Item = new_item)
            return return_SUCCESS(data=new_item)
    
        except Exception as e:
            # Возвращаем ошибку, если запись в БД не удалась
            return return_ERROR()
    
# Если пользователь существует
# проверяем пароль
    save_pass = user_data[DATA_FIELDS.USER_PASSWORD]
    if save_pass != p[DATA_FIELDS.USER_PASSWORD]:
        return return_ERROR()
    
    # Если пароль верный, генерируем секретный ключ
    secret_key = generate_secret_key(64)

    timestamp = create_timestamp()

    # формируем ответ
    item = {
        DATA_FIELDS.USER_PASSWORD: str(user_data[DATA_FIELDS.USER_PASSWORD]),
        DATA_FIELDS.USER_NIKNAME: str(user_data[DATA_FIELDS.USER_NIKNAME]),
        DATA_FIELDS.LIST_DEVICES: str(user_data[DATA_FIELDS.LIST_DEVICES]),
        DATA_FIELDS.USER_NAME: str(user_data[DATA_FIELDS.USER_NAME]),
        DATA_FIELDS.TIMESTAMP: str(timestamp),
        DATA_FIELDS.SECRET_KEY: str(secret_key),
    }
    print(item)

    # записываем токен и время его создания в текущего пользователя
    try:
        response = user_table.put_item(Item = item)
        # Если запись прошла успешно, возвращаем успешный ответ с новым токеном
        data = {
            DATA_FIELDS.USER_NAME: str(user_data[DATA_FIELDS.USER_NAME]),
            DATA_FIELDS.TIMESTAMP: str(timestamp),
            DATA_FIELDS.SECRET_KEY: str(secret_key),
        }
        return return_SUCCESS(data=data)
    except Exception as e:
        # Возвращаем ошибку, если запись в БД не удалась
        return return_ERROR()
    