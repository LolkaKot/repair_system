"""
Модели данных для системы учета заявок
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    """Модель пользователя"""
    id: int
    username: str
    password: str
    full_name: str
    role: str
    email: Optional[str] = None
    phone: Optional[str] = None

@dataclass
class Ticket:
    """Модель заявки"""
    id: int
    ticket_number: str
    title: str
    description: str
    status: str
    created_date: datetime
    client_id: int
    assigned_master_id: Optional[int] = None
    client_name: Optional[str] = None
    master_name: Optional[str] = None

@dataclass
class Comment:
    """Модель комментария"""
    id: int
    ticket_id: int
    user_id: int
    user_name: str
    comment_text: str
    created_date: datetime
    user_role: Optional[str] = None

@dataclass
class Notification:
    """Модель уведомления"""
    id: int
    user_id: int
    title: str
    message: str
    notification_type: str
    is_read: bool
    created_date: datetime
    related_ticket_id: Optional[int] = None
    ticket_number: Optional[str] = None