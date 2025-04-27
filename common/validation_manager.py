from constants import DATA_FIELDS

# Валидация имени пользователя
def is_valid_user_name(query_string):
    if (
        DATA_FIELDS.USER_NAME in query_string 
        and len(query_string[DATA_FIELDS.USER_NAME]) > 0
    ):
        return True
    else:
        return False

# Валидация пароля
def is_valid_user_password(query_string):
    if (
        DATA_FIELDS.USER_PASSWORD in query_string 
        and len(query_string[DATA_FIELDS.USER_PASSWORD]) > 0
    ):
        return True
    else:
        return False

# Валидация серийного номера
def is_valid_serial_key(query_string):
    if (
        DATA_FIELDS.SERIAL_KEY in query_string 
        and len(query_string[DATA_FIELDS.SERIAL_KEY]) > 0
    ):
        return True
    else:
        return False

# Валидация подписи
def is_valid_sign(query_string: str, secret_key: str = None):
    if (
        DATA_FIELDS.SIGN in query_string 
        and len(query_string[DATA_FIELDS.SIGN]) > 0
    ):
        if secret_key:
            # нужно отбросить sign,
            # создать локальную подпись с secret_key, 
            # сравнить обе подписи
            
            sign = '0'
            local_sign = '0'
            if local_sign == sign:
                return True
            else:
                return False
        else:
            return True
    else:
        return False

# Валидация метки времени
def is_valid_timestamp(query_string):
    if (
        DATA_FIELDS.TIMESTAMP in query_string 
        and len(query_string[DATA_FIELDS.TIMESTAMP]) > 0
    ):
        return True
    else:
        return False