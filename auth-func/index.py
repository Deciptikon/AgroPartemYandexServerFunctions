from common.constants import (
    NAME_TABLES,
    HTTP_SUCCESS,
    HTTP_ERROR
)
from common.validation_manager import (
    is_valid_user_name,
    is_valid_user_password,
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
from common.crypto_manager import (
    generate_secret_key,
)

def handler(event, context):
    print("-----------------------------")
    
    # Получаем параметры запроса
    p = event.get('queryStringParameters', {})
    print(p)
    
    # Проверяем валидность всех параметров
    a = is_valid_user_name(p)
    print(a)
    #b = is_valid_sign(p)
    #print(b)
    #c = is_valid_timestamp(p)
    #print(c)

    # Если все параметры валидны
    if a:
        print(p['user_name'])
        
        # Получаем таблицу
        user_table = get_table(NAME_TABLES.USER_TABLE)

        print("Читаем данные")
        user_data = get_user(table=user_table, user_name=p['user_name'] )

# Если пользователь найден
        if user_data:
            print("запись есть, проверяем пароль")
            
            save_pass = user_data['user_password']
            if save_pass == p['user_password']:
                # пароли совпадают, передаём информацию пользователю
                print("пароли совпадают")
                # генерируем векретный ключ
                secret_key = generate_secret_key(64)

                timestamp = create_timestamp()

                # формируем ответ
                item = {
                    'user_name': str(user_data['user_name']),
                    'user_password': str(user_data['user_password']),
                    'timestamp': str(timestamp),
                    'user_nikname': str(user_data['user_nikname']),
                    'secret_key': str(secret_key)
                }
                print(item)

                # записываем токен и время его создания в текущего пользователя
                try:
                    response = user_table.put_item(Item = item)
            
                    # Если запись прошла успешно, возвращаем успешный ответ с новым токеном
                    return answer_to_web(200, 'Авторизация успешна', data = item)
        
                except Exception as e:
                # Возвращаем ошибку, если запись в БД не удалась
                    return answer_to_web(500, 'Ошибка авторизации', data = str(e))

            else:
                # пароли не совпадают, отправляем ошибку
                print("пароли не совпадают")
                return answer_to_web(401, 'Ошибка авторизации')

# если записей нет, регестрируем нового пользователя
        else:
            print("регестрируем нового пользователя")

            # Генерируем timestamp
            timestamp = create_timestamp()

            new_item = {
                'user_name': p['user_name'],
                'user_password': p['user_password'],
                'timestamp': timestamp,
                'user_nikname': 'User_' + timestamp
            }

            try:
                response = user_table.put_item(Item = new_item)
            
                # Возвращаем успешный ответ
                return answer_to_web(200, 'Регистрация успешна', data = new_item)
        
            except Exception as e:
                # Возвращаем ошибку, если запись в БД не удалась
                return answer_to_web(500, 'Ошибка регистрации', data = str(e))

            
                
    else:
        # Возвращаем ошибку, если параметр 'name' отсутствует или пуст
        return answer_to_web(400, 'Параметры отсутствуют или пусты')
    