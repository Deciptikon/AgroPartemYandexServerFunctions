from common.table_manager import (
    append_in_string_data,
    delete_from_string_data,
)

list_devices = {
            '12345-67890-RTYBV': {
                'name': "TestName"
                },
            '2G3J6-228GT-QNI85': {
                'name': "Опрыскиватель"
                },
            '00000-ABCDE-1A2B0': {
                'name': "Новый 777"
                }
            }

str_list = str(list_devices)
ttt = append_in_string_data(
    strind_struct=str_list,
    key='99999-ABCDE-99999',
    val={'name': "99999999999"}
)
ppp = delete_from_string_data(
    strind_struct=ttt,
    key=''
)
print(ttt)