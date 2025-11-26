from typing import List, Optional
import app.config as config

class NotificationService:
    def __init__(self, db, notification_manager):
        self.db = db
        self.notification_manager = notification_manager
    
    def notify_ticket_status_change(self, ticket_id: int, old_status: str, new_status: str):
        """Уведомляет клиента об изменении статуса заявки"""
        # Получаем информацию о заявке
        ticket = self.db.get_ticket_by_id(ticket_id)
        
        if not ticket:
            return False
        
        client_id = ticket['client_id']
        ticket_number = ticket['ticket_number']
        title = ticket['title']
        
        status_names = {
            'pending': 'ожидает',
            'in_progress': 'в работе',
            'waiting_parts': 'ожидает запчасти',
            'completed': 'завершена',
            'cancelled': 'отменена'
        }
        
        old_status_name = status_names.get(old_status, old_status)
        new_status_name = status_names.get(new_status, new_status)
        
        title_msg = f"Статус заявки изменен"
        message = f"Статус вашей заявки #{ticket_number} '{title}' изменен с '{old_status_name}' на '{new_status_name}'"
        
        return self.notification_manager.create_notification(
            user_id=client_id,
            title=title_msg,
            message=message,
            notification_type='status_change',
            related_ticket_id=ticket_id
        )
    
    # Остальные методы остаются без изменений...
    def notify_master_assigned(self, ticket_id: int, master_id: int):
        """Уведомляет мастера о назначении заявки"""
        ticket = self.db.get_ticket_by_id(ticket_id)
        
        if not ticket:
            return False
        
        ticket_number = ticket['ticket_number']
        title = ticket['title']
        client_name = ticket['client_name']
        
        title_msg = "Новая заявка назначена"
        message = f"Вам назначена заявка #{ticket_number} '{title}' от клиента {client_name}"
        
        return self.notification_manager.create_notification(
            user_id=master_id,
            title=title_msg,
            message=message,
            notification_type='assignment',
            related_ticket_id=ticket_id
        )
    
    def notify_client_about_master(self, ticket_id: int, master_id: int):
        """Уведомляет клиента о назначении мастера"""
        ticket = self.db.get_ticket_by_id(ticket_id)
        
        if not ticket:
            return False
        
        ticket_number = ticket['ticket_number']
        title = ticket['title']
        client_id = ticket['client_id']
        master_name = ticket['master_name']
        
        title_msg = "Мастер назначен"
        message = f"На вашу заявку #{ticket_number} '{title}' назначен мастер {master_name}"
        
        return self.notification_manager.create_notification(
            user_id=client_id,
            title=title_msg,
            message=message,
            notification_type='master_assigned',
            related_ticket_id=ticket_id
        )
    
    def notify_ticket_created(self, ticket_id: int):
        """Уведомляет администраторов о новой заявке"""
        ticket = self.db.get_ticket_by_id(ticket_id)
        
        if not ticket:
            return False
        
        ticket_number = ticket['ticket_number']
        title = ticket['title']
        client_name = ticket['client_name']
        
        # Получаем всех администраторов
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE role = 'admin'")
        admins = cursor.fetchall()
        
        if not admins:
            return False
        
        title_msg = "Новая заявка"
        message = f"Создана новая заявка #{ticket_number} '{title}' от клиента {client_name}"
        
        success_count = 0
        for admin in admins:
            admin_id = admin[0]
            if self.notification_manager.create_notification(
                user_id=admin_id,
                title=title_msg,
                message=message,
                notification_type='new_ticket',
                related_ticket_id=ticket_id
            ):
                success_count += 1
        
        return success_count > 0