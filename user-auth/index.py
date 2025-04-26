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
    set_item,
    update_item,
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
        new_user = {
            DATA_FIELDS.USER_PASSWORD: str(p[DATA_FIELDS.USER_PASSWORD]),
            DATA_FIELDS.USER_NIKNAME: str('User_' + timestamp),
            DATA_FIELDS.TIMESTAMP: str(timestamp),
            DATA_FIELDS.USER_NAME: str(p[DATA_FIELDS.USER_NAME]),
        }

        if not set_item(
            table=user_table,
            item=new_user
        ):
            return return_ERROR()
        
        return return_SUCCESS(data=new_user)
    
# Если пользователь существует
# проверяем пароль
    save_pass = user_data[DATA_FIELDS.USER_PASSWORD]
    if save_pass != p[DATA_FIELDS.USER_PASSWORD]:
        return return_ERROR()
    
    # Если пароль верный, генерируем секретный ключ
    secret_key = generate_secret_key(64)
    timestamp = create_timestamp()

    if not update_item(
        table=user_table,
        key_dict={DATA_FIELDS.USER_NAME: str(user_data[DATA_FIELDS.USER_NAME]),},
        field_name=DATA_FIELDS.SECRET_KEY,
        new_value=str(secret_key)
    ):
        return return_ERROR()
    
    if not update_item(
        table=user_table,
        key_dict={DATA_FIELDS.USER_NAME: str(user_data[DATA_FIELDS.USER_NAME]),},
        field_name=DATA_FIELDS.TIMESTAMP,
        new_value=str(timestamp)
    ):
        return return_ERROR()

    data = {
            DATA_FIELDS.USER_NAME: str(user_data[DATA_FIELDS.USER_NAME]),
            DATA_FIELDS.TIMESTAMP: str(timestamp),
            DATA_FIELDS.SECRET_KEY: str(secret_key),
        }
    return return_SUCCESS(data=data)
    