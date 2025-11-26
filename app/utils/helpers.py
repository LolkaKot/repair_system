import random
import string
from datetime import datetime, timedelta
from typing import List, Optional

def generate_ticket_number(prefix: str = "T") -> str:
    """
    Генерирует уникальный номер заявки
    
    Args:
        prefix: Префикс для номера
        
    Returns:
        str: Уникальный номер заявки
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{timestamp}{random_suffix}"

def calculate_working_days(start_date: datetime, end_date: datetime) -> int:
    """
    Рассчитывает количество рабочих дней между двумя датами
    
    Args:
        start_date: Начальная дата
        end_date: Конечная дата
        
    Returns:
        int: Количество рабочих дней
    """
    if start_date > end_date:
        return 0
    
    working_days = 0
    current_date = start_date
    
    while current_date <= end_date:
        # Пропускаем выходные (суббота=5, воскресенье=6)
        if current_date.weekday() < 5:
            working_days += 1
        current_date += timedelta(days=1)
    
    return working_days

def get_status_color(status: str) -> str:
    """
    Возвращает цвет для статуса заявки
    
    Args:
        status: Статус заявки
        
    Returns:
        str: HEX код цвета
    """
    status_colors = {
        'pending': '#FF9800',      # Оранжевый
        'in_progress': '#2196F3',  # Синий
        'waiting_parts': '#FFC107', # Желтый
        'completed': '#4CAF50',    # Зеленый
        'cancelled': '#F44336'     # Красный
    }
    
    return status_colors.get(status, '#9E9E9E')  # Серый по умолчанию

def get_role_display_name(role: str) -> str:
    """
    Возвращает отображаемое название роли
    
    Args:
        role: Роль пользователя
        
    Returns:
        str: Отображаемое название роли
    """
    role_names = {
        'admin': 'Администратор',
        'manager': 'Менеджер',
        'master': 'Мастер',
        'client': 'Клиент'
    }
    
    return role_names.get(role, role)

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Обрезает текст до указанной длины
    
    Args:
        text: Исходный текст
        max_length: Максимальная длина
        suffix: Суффикс для обрезанного текста
        
    Returns:
        str: Обрезанный текст
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def safe_int_convert(value, default: int = 0) -> int:
    """
    Безопасное преобразование в целое число
    
    Args:
        value: Значение для преобразования
        default: Значение по умолчанию при ошибке
        
    Returns:
        int: Преобразованное значение
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float_convert(value, default: float = 0.0) -> float:
    """
    Безопасное преобразование в число с плавающей точкой
    
    Args:
        value: Значение для преобразования
        default: Значение по умолчанию при ошибке
        
    Returns:
        float: Преобразованное значение
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def is_valid_email(email: str) -> bool:
    """
    Проверяет валидность email адреса
    
    Args:
        email: Email для проверки
        
    Returns:
        bool: Валиден ли email
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def generate_random_password(length: int = 8) -> str:
    """
    Генерирует случайный пароль
    
    Args:
        length: Длина пароля
        
    Returns:
        str: Случайный пароль
    """
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(characters) for _ in range(length))

def get_days_until_date(target_date: datetime) -> int:
    """
    Рассчитывает количество дней до указанной даты
    
    Args:
        target_date: Целевая дата
        
    Returns:
        int: Количество дней до даты
    """
    today = datetime.now().date()
    target = target_date.date()
    return (target - today).days

def format_days_delta(days: int) -> str:
    """
    Форматирует разницу в днях в читаемый вид
    
    Args:
        days: Разница в днях
        
    Returns:
        str: Отформатированная разница
    """
    if days == 0:
        return "сегодня"
    elif days == 1:
        return "завтра"
    elif days == -1:
        return "вчера"
    elif days > 0:
        return f"через {days} дн."
    else:
        return f"{abs(days)} дн. назад"

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    Разбивает список на части указанного размера
    
    Args:
        lst: Исходный список
        chunk_size: Размер части
        
    Returns:
        List[List]: Список частей
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def get_first_letter_uppercase(text: str) -> str:
    """
    Возвращает первую букву текста в верхнем регистре
    
    Args:
        text: Исходный текст
        
    Returns:
        str: Первая буква в верхнем регистре
    """
    if not text:
        return ""
    return text[0].upper()

def is_working_hours() -> bool:
    """
    Проверяет, находятся ли текущие время в рабочих часах
    (предполагается 9:00-18:00 по будням)
    
    Returns:
        bool: True если рабочие часы
    """
    now = datetime.now()
    
    # Проверяем будний день (пн-пт)
    if now.weekday() >= 5:  # 5=суббота, 6=воскресенье
        return False
    
    # Проверяем время (9:00-18:00)
    if now.hour < 9 or now.hour >= 18:
        return False
    
    return True