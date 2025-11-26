import mysql.connector
from datetime import datetime
from typing import List, Optional
import app.config as config

class MySQLNotificationManager:
    def __init__(self, database):
        self.database = database
        self._init_notifications_table()
    
    def _init_notifications_table(self):
        """Инициализирует таблицу уведомлений"""
        # Таблица уже создается в MySQLDatabase.init_db()
        pass
    
    def create_notification(self, user_id: int, title: str, message: str, 
                          notification_type: str, related_ticket_id: Optional[int] = None) -> bool:
        """Создает новое уведомление"""
        try:
            conn = self.database.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO notifications (user_id, title, message, notification_type, 
                                         created_date, related_ticket_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (user_id, title, message, notification_type, 
                  datetime.now(), related_ticket_id))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating notification: {e}")
            return False
    
    def get_user_notifications(self, user_id: int, unread_only: bool = False) -> List[dict]:
        """Получает уведомления пользователя"""
        conn = self.database.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = '''
            SELECT n.*, t.ticket_number 
            FROM notifications n
            LEFT JOIN tickets t ON n.related_ticket_id = t.id
            WHERE n.user_id = %s
        '''
        
        if unread_only:
            query += ' AND n.is_read = FALSE'
        
        query += ' ORDER BY n.created_date DESC'
        
        cursor.execute(query, (user_id,))
        notifications = cursor.fetchall()
        
        for notification in notifications:
            if notification['created_date']:
                notification['created_date'] = notification['created_date'].isoformat()
        
        return notifications
    
    def mark_as_read(self, notification_id: int) -> bool:
        """Помечает уведомление как прочитанное"""
        try:
            conn = self.database.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE notifications SET is_read = TRUE WHERE id = %s
            ''', (notification_id,))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error marking notification as read: {e}")
            return False
    
    def mark_all_as_read(self, user_id: int) -> bool:
        """Помечает все уведомления пользователя как прочитанные"""
        try:
            conn = self.database.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE notifications SET is_read = TRUE WHERE user_id = %s
            ''', (user_id,))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error marking all notifications as read: {e}")
            return False
    
    def get_unread_count(self, user_id: int) -> int:
        """Получает количество непрочитанных уведомлений"""
        conn = self.database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM notifications 
            WHERE user_id = %s AND is_read = FALSE
        ''', (user_id,))
        
        count = cursor.fetchone()[0]
        return count