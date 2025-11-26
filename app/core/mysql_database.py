import mysql.connector
from datetime import datetime
from typing import List, Optional
import app.config as config

class MySQLDatabase:
    def __init__(self):
        self.connection = None
        self.init_db()
    
    def get_connection(self):
        """Создает соединение с MySQL"""
        if self.connection is None or not self.connection.is_connected():
            self.connection = mysql.connector.connect(
                host=config.MYSQL_HOST,
                user=config.MYSQL_USER,
                password=config.MYSQL_PASSWORD,
                database=config.MYSQL_DATABASE,
                port=config.MYSQL_PORT
            )
        return self.connection
    
    def init_db(self):
        """Инициализирует базу данных и создает таблицы"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Создаем таблицы
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                role VARCHAR(20) NOT NULL,
                email VARCHAR(100),
                phone VARCHAR(20)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ticket_number VARCHAR(50) UNIQUE NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                created_date DATETIME NOT NULL,
                client_id INT NOT NULL,
                assigned_master_id INT,
                FOREIGN KEY (client_id) REFERENCES users (id),
                FOREIGN KEY (assigned_master_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ticket_id INT NOT NULL,
                user_id INT NOT NULL,
                user_name VARCHAR(100) NOT NULL,
                comment_text TEXT NOT NULL,
                created_date DATETIME NOT NULL,
                FOREIGN KEY (ticket_id) REFERENCES tickets (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                notification_type VARCHAR(50) NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_date DATETIME NOT NULL,
                related_ticket_id INT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (related_ticket_id) REFERENCES tickets (id)
            )
        ''')
        
        # Тестовые данные
        self._create_test_data(cursor)
        
        conn.commit()
    
    def _create_test_data(self, cursor):
        """Создает тестовые данные"""
        # Проверяем есть ли пользователи
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            users = [
                ('admin', 'admin123', 'Администратор Системы', 'admin', 'admin@company.com', '+79990000000'),
                ('manager', 'manager123', 'Менеджер Иванов', 'manager', 'manager@company.com', '+79990000001'),
                ('master1', 'master123', 'Мастер Петров', 'master', 'master@company.com', '+79990000002'),
                ('master2', 'master123', 'Мастер Сидоров', 'master', 'master2@company.com', '+79990000004'),
                ('client1', 'client123', 'Клиент Сидоров', 'client', 'client@company.com', '+79990000003')
            ]
            cursor.executemany(
                "INSERT INTO users (username, password, full_name, role, email, phone) VALUES (%s, %s, %s, %s, %s, %s)",
                users
            )
        
        cursor.execute("SELECT COUNT(*) FROM tickets")
        if cursor.fetchone()[0] == 0:
            tickets = [
                ('T001', 'Ремонт принтера', 'Не печатает черным цветом', 'pending', datetime.now(), 5, None),
                ('T002', 'Неисправность станка', 'Станок издает странные звуки', 'in_progress', datetime.now(), 5, 3),
                ('T003', 'Настройка компьютера', 'Медленно работает', 'completed', datetime.now(), 5, 3),
                ('T004', 'Замена картриджа', 'Требуется замена картриджа', 'pending', datetime.now(), 5, None)
            ]
            cursor.executemany(
                "INSERT INTO tickets (ticket_number, title, description, status, created_date, client_id, assigned_master_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                tickets
            )
    
    def get_all_tickets(self) -> List[dict]:
        """Получает все заявки"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT t.*, u.full_name as client_name, m.full_name as master_name
            FROM tickets t
            LEFT JOIN users u ON t.client_id = u.id
            LEFT JOIN users m ON t.assigned_master_id = m.id
            ORDER BY t.created_date DESC
        ''')
        
        tickets = cursor.fetchall()
        
        # Конвертируем datetime в строку для совместимости
        for ticket in tickets:
            if ticket['created_date']:
                ticket['created_date'] = ticket['created_date'].isoformat()
        
        return tickets
    
    def get_tickets_by_master(self, master_id: int) -> List[dict]:
        """Получает заявки назначенные мастеру"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT t.*, u.full_name as client_name, m.full_name as master_name
            FROM tickets t
            LEFT JOIN users u ON t.client_id = u.id
            LEFT JOIN users m ON t.assigned_master_id = m.id
            WHERE t.assigned_master_id = %s
            ORDER BY t.created_date DESC
        ''', (master_id,))
        
        tickets = cursor.fetchall()
        
        for ticket in tickets:
            if ticket['created_date']:
                ticket['created_date'] = ticket['created_date'].isoformat()
        
        return tickets
    
    def get_pending_tickets(self) -> List[dict]:
        """Получает заявки со статусом pending и без назначенного мастера"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT t.*, u.full_name as client_name, m.full_name as master_name
            FROM tickets t
            LEFT JOIN users u ON t.client_id = u.id
            LEFT JOIN users m ON t.assigned_master_id = m.id
            WHERE t.status = 'pending' AND t.assigned_master_id IS NULL
            ORDER BY t.created_date DESC
        ''')
        
        tickets = cursor.fetchall()
        
        for ticket in tickets:
            if ticket['created_date']:
                ticket['created_date'] = ticket['created_date'].isoformat()
        
        return tickets
    
    def assign_ticket_to_master(self, ticket_id: int, master_id: int) -> bool:
        """Назначает заявку мастеру и меняет статус на in_progress"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE tickets 
                SET assigned_master_id = %s, status = 'in_progress' 
                WHERE id = %s AND status = 'pending'
            ''', (master_id, ticket_id))
            
            affected_rows = cursor.rowcount
            conn.commit()
            
            print(f"🔧 DEBUG: Назначение заявки {ticket_id} мастеру {master_id}")
            print(f"🔧 DEBUG: Затронуто строк: {affected_rows}")
            
            return affected_rows > 0
            
        except Exception as e:
            print(f"❌ Error assigning ticket to master: {e}")
            return False

    def get_user_by_credentials(self, username: str, password: str) -> Optional[dict]:
        """Проверяет учетные данные пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            "SELECT id, username, full_name, role, email, phone FROM users WHERE username = %s AND password = %s",
            (username, password)
        )
        user = cursor.fetchone()
        
        return user
    
    def create_user(self, username: str, password: str, full_name: str, email: str, phone: str) -> bool:
        """Создает нового пользователя (клиента)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO users (username, password, full_name, role, email, phone) VALUES (%s, %s, %s, 'client', %s, %s)",
                (username, password, full_name, email, phone)
            )
            
            user_id = cursor.lastrowid
            
            # Создаем тестовую заявку для нового пользователя
            ticket_number = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"
            cursor.execute(
                "INSERT INTO tickets (ticket_number, title, description, status, created_date, client_id) VALUES (%s, %s, %s, %s, %s, %s)",
                (ticket_number, 'Первая заявка', 'Это ваша первая тестовая заявка', 'pending', datetime.now(), user_id)
            )
            
            conn.commit()
            return True
        except mysql.connector.IntegrityError:
            return False
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def get_tickets_by_client(self, client_id: int) -> List[dict]:
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT t.*, u.full_name as client_name, m.full_name as master_name
            FROM tickets t
            LEFT JOIN users u ON t.client_id = u.id
            LEFT JOIN users m ON t.assigned_master_id = m.id
            WHERE t.client_id = %s
            ORDER BY t.created_date DESC
        ''', (client_id,))
        
        tickets = cursor.fetchall()
        
        for ticket in tickets:
            if ticket['created_date']:
                ticket['created_date'] = ticket['created_date'].isoformat()
        
        return tickets
    
    def get_masters(self) -> List[dict]:
        """Получает список мастеров"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, username, full_name FROM users WHERE role = 'master'")
        masters = cursor.fetchall()
        
        return masters
    
    def update_ticket_status(self, ticket_id: int, status: str) -> bool:
        """Обновляет статус заявки с проверкой назначения мастера"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Сначала проверим есть ли назначенный мастер
            cursor.execute('''
                SELECT assigned_master_id FROM tickets WHERE id = %s
            ''', (ticket_id,))
            result = cursor.fetchone()
            
            if not result:
                print("❌ Заявка не найдена")
                return False
                
            assigned_master_id = result[0]
            
            # Проверяем: если пытаемся поставить in_progress или completed без мастера
            if status in ['in_progress', 'completed'] and not assigned_master_id:
                print("❌ Нельзя изменить статус без назначенного мастера")
                return False
            
            # Если проверка пройдена - обновляем статус
            cursor.execute(
                "UPDATE tickets SET status = %s WHERE id = %s",
                (status, ticket_id)
            )
            
            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            
            return affected_rows > 0
            
        except Exception as e:
            print(f"Error updating ticket status: {e}")
            return False
    
    def delete_ticket(self, ticket_id: int, user_id: int, user_role: str) -> bool:
        """Удаляет заявку с проверкой прав и каскадным удалением"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Проверяем права на удаление
            if user_role == 'admin':
                # Админ может удалить любую заявку - сначала удаляем связанные данные
                cursor.execute("DELETE FROM notifications WHERE related_ticket_id = %s", (ticket_id,))
                cursor.execute("DELETE FROM comments WHERE ticket_id = %s", (ticket_id,))
                cursor.execute("DELETE FROM tickets WHERE id = %s", (ticket_id,))
                
            elif user_role == 'client':
                # Клиент может удалить только свои заявки - проверяем владельца
                cursor.execute("SELECT client_id FROM tickets WHERE id = %s", (ticket_id,))
                result = cursor.fetchone()
                
                if result and result[0] == user_id:
                    # Удаляем связанные данные и заявку
                    cursor.execute("DELETE FROM notifications WHERE related_ticket_id = %s", (ticket_id,))
                    cursor.execute("DELETE FROM comments WHERE ticket_id = %s", (ticket_id,))
                    cursor.execute("DELETE FROM tickets WHERE id = %s", (ticket_id,))
                else:
                    conn.close()
                    return False
            else:
                conn.close()
                return False
            
            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            
            return affected_rows > 0
            
        except Exception as e:
            print(f"Error deleting ticket: {e}")
            return False
    
    def create_ticket(self, title: str, description: str, client_id: int) -> bool:
        """Создает новую заявку"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            ticket_number = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            cursor.execute('''
                INSERT INTO tickets (ticket_number, title, description, created_date, client_id)
                VALUES (%s, %s, %s, %s, %s)
            ''', (ticket_number, title, description, datetime.now(), client_id))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating ticket: {e}")
            return False

    def update_ticket_status_with_notification(self, ticket_id: int, new_status: str, notification_service) -> bool:
        """Обновляет статус заявки с отправкой уведомления и проверкой мастера"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Получаем текущий статус и назначенного мастера
            cursor.execute('SELECT status, assigned_master_id FROM tickets WHERE id = %s', (ticket_id,))
            result = cursor.fetchone()
            
            if not result:
                return False
            
            old_status, assigned_master_id = result
            
            # Проверяем назначение мастера для определенных статусов
            if new_status in ['in_progress', 'completed'] and not assigned_master_id:
                print("❌ Нельзя установить статус 'в работе' или 'выполнено' без назначенного мастера")
                return False
            
            # Обновляем статус
            cursor.execute(
                "UPDATE tickets SET status = %s WHERE id = %s",
                (new_status, ticket_id)
            )
            
            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            
            if affected_rows > 0 and old_status != new_status:
                # Отправляем уведомление об изменении статуса
                notification_service.notify_ticket_status_change(ticket_id, old_status, new_status)
            
            return affected_rows > 0
            
        except Exception as e:
            print(f"Error updating ticket status: {e}")
            return False

    def assign_ticket_to_master_with_notification(self, ticket_id: int, master_id: int, notification_service) -> bool:
        """Назначает заявку мастеру с отправкой уведомлений"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE tickets 
                SET assigned_master_id = %s, status = 'in_progress' 
                WHERE id = %s AND status = 'pending'
            ''', (master_id, ticket_id))
            
            affected_rows = cursor.rowcount
            conn.commit()
            
            if affected_rows > 0:
                # Отправляем уведомления
                notification_service.notify_master_assigned(ticket_id, master_id)
                notification_service.notify_client_about_master(ticket_id, master_id)
            
            return affected_rows > 0
            
        except Exception as e:
            print(f"Error assigning ticket to master: {e}")
            return False

    def create_ticket_with_notification(self, title: str, description: str, client_id: int, notification_service) -> bool:
        """Создает новую заявку с отправкой уведомлений"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            ticket_number = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            cursor.execute('''
                INSERT INTO tickets (ticket_number, title, description, created_date, client_id)
                VALUES (%s, %s, %s, %s, %s)
            ''', (ticket_number, title, description, datetime.now(), client_id))
            
            ticket_id = cursor.lastrowid
            
            conn.commit()
            
            if ticket_id:
                # Отправляем уведомление администраторам
                notification_service.notify_ticket_created(ticket_id)
            
            return True
        except Exception as e:
            print(f"Error creating ticket: {e}")
            return False

    def update_ticket(self, ticket_id: int, title: str, description: str, user_id: int, user_role: str) -> bool:
        """Обновляет заявку с проверкой прав"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Проверяем права на редактирование
            if user_role == 'admin':
                # Админ может редактировать любую заявку
                cursor.execute('''
                    UPDATE tickets 
                    SET title = %s, description = %s 
                    WHERE id = %s
                ''', (title, description, ticket_id))
            
            elif user_role == 'client':
                # Клиент может редактировать только свои заявки в статусе pending
                cursor.execute('''
                    UPDATE tickets 
                    SET title = %s, description = %s 
                    WHERE id = %s AND client_id = %s AND status = 'pending'
                ''', (title, description, ticket_id, user_id))
            
            elif user_role == 'master':
                # Мастер может редактировать только назначенные ему заявки
                cursor.execute('''
                    UPDATE tickets 
                    SET title = %s, description = %s 
                    WHERE id = %s AND assigned_master_id = %s
                ''', (title, description, ticket_id, user_id))
            else:
                return False
            
            affected_rows = cursor.rowcount
            conn.commit()
            
            return affected_rows > 0
            
        except Exception as e:
            print(f"Error updating ticket: {e}")
            return False

    def add_comment(self, ticket_id: int, user_id: int, user_name: str, comment_text: str) -> bool:
        """Добавляет комментарий к заявке"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO comments (ticket_id, user_id, user_name, comment_text, created_date)
                VALUES (%s, %s, %s, %s, %s)
            ''', (ticket_id, user_id, user_name, comment_text, datetime.now()))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding comment: {e}")
            return False

    def get_comments_by_ticket(self, ticket_id: int) -> List[dict]:
        """Получает все комментарии для заявки"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT c.*, u.role as user_role
            FROM comments c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.ticket_id = %s
            ORDER BY c.created_date ASC
        ''', (ticket_id,))
        
        comments = cursor.fetchall()
        
        for comment in comments:
            if comment['created_date']:
                comment['created_date'] = comment['created_date'].isoformat()
        
        return comments

    def get_ticket_by_id(self, ticket_id: int) -> Optional[dict]:
        """Получает заявку по ID"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT t.*, u.full_name as client_name, m.full_name as master_name
            FROM tickets t
            LEFT JOIN users u ON t.client_id = u.id
            LEFT JOIN users m ON t.assigned_master_id = m.id
            WHERE t.id = %s
        ''', (ticket_id,))
        
        ticket = cursor.fetchone()
        
        if ticket and ticket['created_date']:
            ticket['created_date'] = ticket['created_date'].isoformat()
        
        return ticket

    def __del__(self):
        """Закрывает соединение при удалении объекта"""
        if self.connection and self.connection.is_connected():
            self.connection.close()