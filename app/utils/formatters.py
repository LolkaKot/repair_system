from datetime import datetime
from typing import Optional

def format_date(date_string: str, format_type: str = "short") -> str:
    """
    Форматирует дату в читаемый вид
    
    Args:
        date_string: Строка с датой в ISO формате
        format_type: Тип формата ("short", "long", "datetime")
        
    Returns:
        str: Отформатированная дата
    """
    if not date_string:
        return "Не указана"
    
    try:
        # Парсим дату из ISO формата
        if 'Z' in date_string:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        else:
            dt = datetime.fromisoformat(date_string)
        
        formats = {
            "short": "%d.%m.%Y",           # 15.12.2023
            "long": "%d %B %Y",            # 15 декабря 2023
            "datetime": "%d.%m.%Y %H:%M",  # 15.12.2023 14:30
            "time": "%H:%M",               # 14:30
            "full": "%d.%m.%Y %H:%M:%S"   # 15.12.2023 14:30:25
        }
        
        format_str = formats.get(format_type, "%d.%m.%Y %H:%M")
        return dt.strftime(format_str)
        
    except (ValueError, TypeError):
        # Если не удалось распарсить, возвращаем как есть (обрезаем время если есть)
        return date_string[:16].replace('T', ' ') if 'T' in date_string else date_string

def format_phone(phone: str) -> str:
    """
    Форматирует номер телефона в читаемый вид
    
    Args:
        phone: Номер телефона в любом формате
        
    Returns:
        str: Отформатированный номер телефона
    """
    if not phone:
        return "Не указан"
    
    # Убираем все нецифровые символы
    cleaned = ''.join(filter(str.isdigit, phone))
    
    if len(cleaned) == 10:
        # Формат: +7 (XXX) XXX-XX-XX
        return f"+7 ({cleaned[0:3]}) {cleaned[3:6]}-{cleaned[6:8]}-{cleaned[8:10]}"
    elif len(cleaned) == 11:
        # Формат: +7 (XXX) XXX-XX-XX (убираем первую 7 или 8)
        return f"+7 ({cleaned[1:4]}) {cleaned[4:7]}-{cleaned[7:9]}-{cleaned[9:11]}"
    else:
        # Если формат не распознан, возвращаем как есть
        return phone

def format_status(status: str) -> str:
    """
    Форматирует статус заявки в читаемый вид
    
    Args:
        status: Статус заявки
        
    Returns:
        str: Отформатированный статус
    """
    status_map = {
        'pending': 'Ожидает',
        'in_progress': 'В работе',
        'waiting_parts': 'Ожидает запчасти',
        'completed': 'Завершена',
        'cancelled': 'Отменена'
    }
    
    return status_map.get(status, status)

def format_role(role: str) -> str:
    """
    Форматирует роль пользователя в читаемый вид
    
    Args:
        role: Роль пользователя
        
    Returns:
        str: Отформатированная роль
    """
    role_map = {
        'admin': 'Администратор',
        'manager': 'Менеджер',
        'master': 'Мастер',
        'client': 'Клиент'
    }
    
    return role_map.get(role, role)

def format_ticket_number(ticket_number: str) -> str:
    """
    Форматирует номер заявки для отображения
    
    Args:
        ticket_number: Номер заявки
        
    Returns:
        str: Отформатированный номер заявки
    """
    if not ticket_number:
        return "Без номера"
    
    return f"#{ticket_number}"

def format_duration(seconds: int) -> str:
    """
    Форматирует продолжительность в читаемый вид
    
    Args:
        seconds: Продолжительность в секундах
        
    Returns:
        str: Отформатированная продолжительность
    """
    if not seconds:
        return "0 сек"
    
    if seconds < 60:
        return f"{seconds} сек"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} мин"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours} ч {minutes} мин"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days} д {hours} ч"

def format_file_size(size_bytes: int) -> str:
    """
    Форматирует размер файла в читаемый вид
    
    Args:
        size_bytes: Размер файла в байтах
        
    Returns:
        str: Отформатированный размер файла
    """
    if not size_bytes:
        return "0 Б"
    
    units = ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']
    unit_index = 0
    
    size = float(size_bytes)
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.1f} {units[unit_index]}"

def format_currency(amount: float, currency: str = "₽") -> str:
    """
    Форматирует денежную сумму в читаемый вид
    
    Args:
        amount: Сумма
        currency: Валюта
        
    Returns:
        str: Отформатированная сумма
    """
    if amount is None:
        return "Не указана"
    
    return f"{amount:,.2f} {currency}".replace(',', ' ').replace('.', ',')

def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Форматирует процентное значение
    
    Args:
        value: Значение в долях (0.15 = 15%)
        decimals: Количество знаков после запятой
        
    Returns:
        str: Отформатированный процент
    """
    if value is None:
        return "Не указано"
    
    percentage = value * 100
    return f"{percentage:.{decimals}f}%"