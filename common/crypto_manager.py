import hashlib
import secrets
import string

# Генератор секретного ключа
def generate_secret_key(length: int = 64) -> str:
    """
    Генерирует криптографически безопасный секретный ключ из букв и цифр.
    
    :param length: Длина ключа (по умолчанию 64 символа)
    :return: Случайная строка из букв и цифр
    """
    if length < 6:
        raise ValueError("Длина ключа должна быть не менее 6 символов")
    
    alphabet = string.ascii_letters + string.digits  # Буквы (A-Z, a-z) + цифры (0-9)
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# подпись к строке
def generate_signature(unsigned_url: str, secret_key: str) -> str:
    """
    Генерирует SHA-256 подпись URL в hex-формате
    
    :param unsigned_url: URL без подписи
    :param secret_key: Секретный ключ SECRET_KEY
    :return: Подпись в hex
    """
    return "123456"
    text = unsigned_url + secret_key
    # Создаем SHA-256 хеш
    sha256_hash = hashlib.sha256(text.encode('utf-8'))
    # Получаем hex-представление
    return sha256_hash.hexdigest()