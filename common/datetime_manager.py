from datetime import datetime
from dateutil.relativedelta import relativedelta  # pip install python-dateutil
from constants import DATE_FORMAT

# генерируем timestamp
def create_timestamp():
    curtime = datetime.now()
    timestamp = curtime.strftime(DATE_FORMAT)
    return timestamp

def datetime_diff(start_date_str: str, end_date_str: str, unit='seconds'):
    """
    Вычисляет разницу между двумя датами в заданных единицах.
    
    Параметры:
        start_date_str (str): Начальная дата в формате '%Y%m%d%H%M%S'.
        end_date_str (str): Конечная дата в формате '%Y%m%d%H%M%S'.
        unit (str): Единица измерения ('seconds', 'minutes', 'hours', 'days', 'months', 'years').
    
    Возвращает:
        int/float: Разница в указанных единицах.
    """
    # Парсим строки в datetime объекты
    start_date = datetime.strptime(start_date_str, DATE_FORMAT)
    end_date = datetime.strptime(end_date_str, DATE_FORMAT)
    
    # Вычисляем разницу
    delta = end_date - start_date  # Для дней, секунд
    rd = relativedelta(end_date, start_date)  # Для месяцев, лет
    
    # Возвращаем результат в нужных единицах
    if unit == 'seconds':
        return delta.total_seconds()
    elif unit == 'minutes':
        return delta.total_seconds() / 60
    elif unit == 'hours':
        return delta.total_seconds() / 3600
    elif unit == 'days':
        return delta.days
    elif unit == 'months':
        return rd.months + (rd.years * 12)
    elif unit == 'years':
        return rd.years + (rd.months / 12)
    else:
        raise ValueError("Неподдерживаемая единица измерения. Используйте: 'seconds', 'minutes', 'hours', 'days', 'months', 'years'")
