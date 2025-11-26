import re
from typing import Tuple  # Убираем bool отсюда

def validate_email(email: str) -> Tuple[bool, str]:
    """
    Валидация email адреса
    
    Args:
        email: Email для проверки
        
    Returns:
        Tuple[bool, str]: (валиден ли email, сообщение об ошибке)
    """
    if not email:
        return False, "Email не может быть пустым"
    
    # Проверка длины
    if len(email) > 254:  # RFC 5321 ограничение
        return False, "Email слишком длинный"
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Неверный формат email"
    
    # Дополнительная проверка длины имени пользователя
    local_part = email.split('@')[0]
    if len(local_part) > 64:  # RFC 5321 ограничение
        return False, "Имя пользователя в email слишком длинное"
    
    return True, ""

def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Валидация номера телефона
    
    Args:
        phone: Номер телефона для проверки
        
    Returns:
        Tuple[bool, str]: (валиден ли телефон, сообщение об ошибке)
    """
    if not phone:
        return False, "Телефон не может быть пустым"
    
    # Убираем все нецифровые символы
    cleaned_phone = re.sub(r'\D', '', phone)
    
    # Проверяем длину (российские номера обычно 10-11 цифр)
    if len(cleaned_phone) not in [10, 11]:
        return False, "Неверная длина номера телефона"
    
    # Проверяем, что номер начинается с 7 или 8 (для России)
    if not cleaned_phone.startswith(('7', '8')):
        return False, "Номер должен начинаться с 7 или 8"
    
    return True, ""

def validate_password(password: str) -> Tuple[bool, str]:
    """
    Валидация пароля
    
    Args:
        password: Пароль для проверки
        
    Returns:
        Tuple[bool, str]: (валиден ли пароль, сообщение об ошибке)
    """
    if not password:
        return False, "Пароль не может быть пустым"
    
    if len(password) < 6:
        return False, "Пароль должен содержать минимум 6 символов"
    
    if len(password) > 50:
        return False, "Пароль не должен превышать 50 символов"
    
    # ИСПРАВЛЕНИЕ: проверяем наличие хотя бы одной буквы (любого регистра) и одной цифры
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    if not has_letter:
        return False, "Пароль должен содержать хотя бы одну букву"
    
    if not has_digit:
        return False, "Пароль должен содержать хотя бы одну цифру"
    
    return True, ""

def validate_username(username: str) -> Tuple[bool, str]:
    """
    Валидация имени пользователя
    
    Args:
        username: Имя пользователя для проверки
        
    Returns:
        Tuple[bool, str]: (валидно ли имя, сообщение об ошибке)
    """
    if not username:
        return False, "Имя пользователя не может быть пустым"
    
    if len(username) < 3:
        return False, "Имя пользователя должно содержать минимум 3 символа"
    
    if len(username) > 30:
        return False, "Имя пользователя не должно превышать 30 символов"
    
    # Проверяем допустимые символы (только буквы, цифры и подчеркивание)
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Имя пользователя может содержать только буквы, цифры и подчеркивание"
    
    return True, ""

def validate_full_name(full_name: str) -> Tuple[bool, str]:
    """
    Валидация полного имени
    
    Args:
        full_name: Полное имя для проверки
        
    Returns:
        Tuple[bool, str]: (валидно ли имя, сообщение об ошибке)
    """
    if not full_name:
        return False, "Полное имя не может быть пустым"
    
    if len(full_name) < 2:
        return False, "Полное имя должно содержать минимум 2 символа"
    
    if len(full_name) > 100:
        return False, "Полное имя не должно превышать 100 символов"
    
    # Проверяем, что имя содержит только буквы, пробелы и дефисы
    if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s\-]+$', full_name):
        return False, "Полное имя может содержать только буквы, пробелы и дефисы"
    
    return True, ""

def validate_ticket_title(title: str) -> Tuple[bool, str]:
    """
    Валидация заголовка заявки
    
    Args:
        title: Заголовок заявки для проверки
        
    Returns:
        Tuple[bool, str]: (валиден ли заголовок, сообщение об ошибке)
    """
    if not title:
        return False, "Заголовок заявки не может быть пустым"
    
    if len(title) < 5:
        return False, "Заголовок заявки должен содержать минимум 5 символов"
    
    if len(title) > 200:
        return False, "Заголовок заявки не должен превышать 200 символов"
    
    return True, ""

def validate_ticket_description(description: str) -> Tuple[bool, str]:
    """
    Валидация описания заявки
    
    Args:
        description: Описание заявки для проверки
        
    Returns:
        Tuple[bool, str]: (валидно ли описание, сообщение об ошибке)
    """
    if not description:
        return False, "Описание заявки не может быть пустым"
    
    if len(description) < 10:
        return False, "Описание заявки должно содержать минимум 10 символов"
    
    if len(description) > 2000:
        return False, "Описание заявки не должно превышать 2000 символов"
    
    return True, ""