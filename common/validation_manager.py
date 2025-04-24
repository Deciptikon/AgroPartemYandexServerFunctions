# Валидация имени пользователя
def is_valid_user_name(query_string):
    if 'user_name' in query_string and len(query_string['user_name']) > 0:
        return True
    else:
        return False

# Валидация пароля
def is_valid_user_password(query_string):
    if 'user_password' in query_string and len(query_string['user_password']) > 0:
        return True
    else:
        return False

# Валидация серийного номера
def is_valid_serial_key(query_string):
    if 'serial_key' in query_string and len(query_string['serial_key']) > 0:
        return True
    else:
        return False

# Валидация подписи
def is_valid_sign(query_string: str, secret_key: str = None):
    if 'sign' in query_string and len(query_string['sign']) > 0:
        if secret_key:
            # нужно отбросить sign,
            # создать локальную подпись с secret_key, 
            # сравнить обе подписи
            return False
        else:
            return True
    else:
        return False

# Валидация временной метки
def is_valid_timestamp(query_string):
    if 'timestamp' in query_string and len(query_string['timestamp']) > 0:
        return True
    else:
        return False