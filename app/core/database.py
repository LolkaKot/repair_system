import sqlite3
from datetime import datetime
from typing import List, Optional
import app.config as config

class Database:
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        
        # Пользователи
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                email TEXT,
                phone TEXT
            )
        ''')
        
        # Заявки - базовая таблица
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_number TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_date TEXT NOT NULL,
                client_id INTEGER NOT NULL,
                assigned_master_id INTEGER,
                FOREIGN KEY (client_id) REFERENCES users (id)
            )
        ''')

        # Таблица комментариев
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                user_name TEXT NOT NULL,
                comment_text TEXT NOT NULL,
                created_date TEXT NOT NULL,
                FOREIGN KEY (ticket_id) REFERENCES tickets (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Таблица уведомлений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                notification_type TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_date TEXT NOT NULL,
                related_ticket_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (related_ticket_id) REFERENCES tickets (id)
            )
        ''')
        
        # Проверяем и добавляем поле assigned_master_id если его нет
        try:
            cursor.execute("SELECT assigned_master_id FROM tickets LIMIT 1")
        except sqlite3.OperationalError:
            # Поле не существует, добавляем его
            print("Adding assigned_master_id column to tickets table...")
            cursor.execute('''
                ALTER TABLE tickets 
                ADD COLUMN assigned_master_id INTEGER
                REFERENCES users(id)
            ''')
        
        # Тестовые данные
        self._create_test_data(cursor)
        
        conn.commit()
        conn.close()
    
    def _create_test_data(self, cursor):
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
                "INSERT INTO users (username, password, full_name, role, email, phone) VALUES (?, ?, ?, ?, ?, ?)",
                users
            )
        
        cursor.execute("SELECT COUNT(*) FROM tickets")
        if cursor.fetchone()[0] == 0:
            tickets = [
                ('T001', 'Ремонт принтера', 'Не печатает черным цветом', 'pending', datetime.now().isoformat(), 5, None),
                ('T002', 'Неисправность станка', 'Станок издает странные звуки', 'in_progress', datetime.now().isoformat(), 5, 3),
                ('T003', 'Настройка компьютера', 'Медленно работает', 'completed', datetime.now().isoformat(), 5, 3),
                ('T004', 'Замена картриджа', 'Требуется замена картриджа', 'pending', datetime.now().isoformat(), 5, None)
            ]
            cursor.executemany(
                "INSERT INTO tickets (ticket_number, title, description, status, created_date, client_id, assigned_master_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                tickets
            )
    
    def get_all_tickets(self) -> List[dict]:
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        
        # Проверяем существование поля assigned_master_id
        try:
            cursor.execute("PRAGMA table_info(tickets)")
            columns = [column[1] for column in cursor.fetchall()]
            has_assigned_master = 'assigned_master_id' in columns
        except:
            has_assigned_master = False
        
        if has_assigned_master:
            cursor.execute('''
                SELECT t.*, u.full_name as client_name, m.full_name as master_name
                FROM tickets t
                LEFT JOIN users u ON t.client_id = u.id
                LEFT JOIN users m ON t.assigned_master_id = m.id
                ORDER BY t.created_date DESC
            ''')
        else:
            # Если поля нет, используем упрощенный запрос
            cursor.execute('''
                SELECT t.*, u.full_name as client_name, NULL as master_name
                FROM tickets t
                LEFT JOIN users u ON t.client_id = u.id
                ORDER BY t.created_date DESC
            ''')
        
        tickets = cursor.fetchall()
        conn.close()
        
        return [{
            'id': t[0],
            'ticket_number': t[1],
            'title': t[2],
            'description': t[3],
            'status': t[4],
            'created_date': t[5],
            'client_id': t[6],
            'assigned_master_id': t[7] if has_assigned_master else None,
            'client_name': t[8],
            'master_name': t[9] if has_assigned_master else None
        } for t in tickets]
    
    def get_tickets_by_master(self, master_id: int) -> List[dict]:
        """Получает заявки назначенные мастеру"""
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        
        # Проверяем существование поля assigned_master_id
        try:
            cursor.execute("PRAGMA table_info(tickets)")
            columns = [column[1] for column in cursor.fetchall()]
            has_assigned_master = 'assigned_master_id' in columns
        except:
            has_assigned_master = False
        
        if has_assigned_master:
            cursor.execute('''
                SELECT t.*, u.full_name as client_name, m.full_name as master_name
                FROM tickets t
                LEFT JOIN users u ON t.client_id = u.id
                LEFT JOIN users m ON t.assigned_master_id = m.id
                WHERE t.assigned_master_id = ?
                ORDER BY t.created_date DESC
            ''', (master_id,))
        else:
            # Если поля нет, возвращаем пустой список
            cursor.execute('SELECT 1')  # Простой запрос чтобы не было ошибки
            tickets = []
            conn.close()
            return []
        
        tickets = cursor.fetchall()
        conn.close()
        
        return [{
            'id': t[0],
            'ticket_number': t[1],
            'title': t[2],
            'description': t[3],
            'status': t[4],
            'created_date': t[5],
            'client_id': t[6],
            'assigned_master_id': t[7],
            'client_name': t[8],
            'master_name': t[9]
        } for t in tickets]
    
    def get_pending_tickets(self) -> List[dict]:
        """Получает заявки со статусом pending и без назначенного мастера"""
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        
        # Проверяем существование поля assigned_master_id
        try:
            cursor.execute("PRAGMA table_info(tickets)")
            columns = [column[1] for column in cursor.fetchall()]
            has_assigned_master = 'assigned_master_id' in columns
        except:
            has_assigned_master = False
        
        if has_assigned_master:
            cursor.execute('''
                SELECT t.*, u.full_name as client_name, m.full_name as master_name
                FROM tickets t
                LEFT JOIN users u ON t.client_id = u.id
                LEFT JOIN users m ON t.assigned_master_id = m.id
                WHERE t.status = 'pending' AND t.assigned_master_id IS NULL
                ORDER BY t.created_date DESC
            ''')
        else:
            # Если поля нет, возвращаем все pending заявки
            cursor.execute('''
                SELECT t.*, u.full_name as client_name, NULL as master_name
                FROM tickets t
                LEFT JOIN users u ON t.client_id = u.id
                WHERE t.status = 'pending'
                ORDER BY t.created_date DESC
            ''')
        
        tickets = cursor.fetchall()
        conn.close()
        
        return [{
            'id': t[0],
            'ticket_number': t[1],
            'title': t[2],
            'description': t[3],
            'status': t[4],
            'created_date': t[5],
            'client_id': t[6],
            'assigned_master_id': t[7] if has_assigned_master else None,
            'client_name': t[8],
            'master_name': t[9] if has_assigned_master else None
        } for t in tickets]
    
    def assign_ticket_to_master(self, ticket_id: int, master_id: int, user_role: str = None) -> bool:
        """Назначает заявку мастеру и меняет статус на in_progress с проверкой прав"""
        # Проверка прав доступа - только администраторы и менеджеры могут назначать мастеров
        if user_role and user_role not in ['admin', 'manager']:
            return False
            
        try:
            conn = sqlite3.connect(config.DATABASE_PATH)
            cursor = conn.cursor()
            
            # Проверяем существование поля assigned_master_id
            try:
                cursor.execute("PRAGMA table_info(tickets)")
                columns = [column[1] for column in cursor.fetchall()]
                has_assigned_master = 'assigned_master_id' in columns
            except:
                has_assigned_master = False
            
            if has_assigned_master:
                cursor.execute('''
                    UPDATE tickets 
                    SET assigned_master_id = ?, status = 'in_progress' 
                    WHERE id = ? AND status = 'pending'
                ''', (master_id, ticket_id))
            else:
                # Если поля нет, просто меняем статус
                cursor.execute('''
                    UPDATE tickets 
                    SET status = 'in_progress' 
                    WHERE id = ? AND status = 'pending'
                ''', (ticket_id,))
            
            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            
            return affected_rows > 0
            
        except Exception as e:
            print(f"Error assigning ticket to master: {e}")
            return False

    def get_user_by_credentials(self, username: str, password: str) -> Optional[dict]:
        """Проверяет учетные данные пользователя"""
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, full_name, role, email, phone FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'full_name': user[2],
                'role': user[3],
                'email': user[4],
                'phone': user[5]
            }
        return None
    
    def create_user(self, username: str, password: str, full_name: str, email: str, phone: str) -> bool:
        """Создает нового пользователя (клиента)"""
        try:
            conn = sqlite3.connect(config.DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, full_name, role, email, phone) VALUES (?, ?, ?, 'client', ?, ?)",
                (username, password, full_name, email, phone)
            )
            
            # Получаем ID нового пользователя
            user_id = cursor.lastrowid
            
            # Создаем тестовую заявку для нового пользователя
            ticket_number = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"
            cursor.execute(
                "INSERT INTO tickets (ticket_number, title, description, status, created_date, client_id) VALUES (?, ?, ?, ?, ?, ?)",
                (ticket_number, 'Первая заявка', 'Это ваша первая тестовая заявка', 'pending', datetime.now().isoformat(), user_id)
            )
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def get_tickets_by_client(self, client_id: int) -> List[dict]:
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        
        # Проверяем существование поля assigned_master_id
        try:
            cursor.execute("PRAGMA table_info(tickets)")
            columns = [column[1] for column in cursor.fetchall()]
            has_assigned_master = 'assigned_master_id' in columns
        except:
            has_assigned_master = False
        
        if has_assigned_master:
            cursor.execute('''
                SELECT t.*, u.full_name as client_name, m.full_name as master_name
                FROM tickets t
                LEFT JOIN users u ON t.client_id = u.id
                LEFT JOIN users m ON t.assigned_master_id = m.id
                WHERE t.client_id = ?
                ORDER BY t.created_date DESC
            ''', (client_id,))
        else:
            cursor.execute('''
                SELECT t.*, u.full_name as client_name, NULL as master_name
                FROM tickets t
                LEFT JOIN users u ON t.client_id = u.id
                WHERE t.client_id = ?
                ORDER BY t.created_date DESC
            ''', (client_id,))
        
        tickets = cursor.fetchall()
        conn.close()
        
        return [{
            'id': t[0],
            'ticket_number': t[1],
            'title': t[2],
            'description': t[3],
            'status': t[4],
            'created_date': t[5],
            'client_id': t[6],
            'assigned_master_id': t[7] if has_assigned_master else None,
            'client_name': t[8],
            'master_name': t[9] if has_assigned_master else None
        } for t in tickets]
    
    def get_masters(self) -> List[dict]:
        """Получает список мастеров"""
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, role FROM users WHERE role = 'master'")
        masters = cursor.fetchall()
        conn.close()
        
        return [{
            'id': m[0],
            'username': m[1],
            'full_name': m[2],
            'role': m[3]
        } for m in masters]
    
    def update_ticket_status(self, ticket_id: int, status: str) -> bool:
        """Обновляет статус заявки"""
        try:
            conn = sqlite3.connect(config.DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE tickets SET status = ? WHERE id = ?",
                (status, ticket_id)
            )
            
            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            
            # Возвращаем True только если действительно обновили запись
            return affected_rows > 0
            
        except Exception as e:
            print(f"Error updating ticket status: {e}")
            return False
    
    def delete_ticket(self, ticket_id: int, user_id: int, user_role: str) -> bool:
        """Удаляет заявку с проверкой прав и каскадным удалением"""
        try:
            conn = sqlite3.connect(config.DATABASE_PATH)
            cursor = conn.cursor()
            
            # Проверяем права на удаление
            if user_role == 'admin':
                # Админ может удалить любую заявку - сначала удаляем связанные данные
                cursor.execute("DELETE FROM notifications WHERE related_ticket_id = ?", (ticket_id,))
                cursor.execute("DELETE FROM comments WHERE ticket_id = ?", (ticket_id,))
                cursor.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
                
            elif user_role == 'client':
                # Клиент может удалить только свои заявки - проверяем владельца
                cursor.execute("SELECT client_id FROM tickets WHERE id = ?", (ticket_id,))
                result = cursor.fetchone()
                
                if result and result[0] == user_id:
                    # Удаляем связанные данные и заявку
                    cursor.execute("DELETE FROM notifications WHERE related_ticket_id = ?", (ticket_id,))
                    cursor.execute("DELETE FROM comments WHERE ticket_id = ?", (ticket_id,))
                    cursor.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
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
            conn = sqlite3.connect(config.DATABASE_PATH)
            cursor = conn.cursor()
            
            # Генерируем уникальный номер заявки с случайным компонентом
            import random
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            random_suffix = ''.join(random.choices('0123456789', k=4))
            ticket_number = f"T{timestamp}{random_suffix}"
            
            # Проверяем уникальность (на всякий случай)
            cursor.execute("SELECT id FROM tickets WHERE ticket_number = ?", (ticket_number,))
            if cursor.fetchone():
                # Если номер уже существует, генерируем новый
                random_suffix = ''.join(random.choices('0123456789', k=6))
                ticket_number = f"T{timestamp}{random_suffix}"
            
            cursor.execute('''
                INSERT INTO tickets (ticket_number, title, description, created_date, client_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (ticket_number, title, description, datetime.now().isoformat(), client_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating ticket: {e}")
            return False

    def update_ticket_status_with_notification(self, ticket_id: int, new_status: str, notification_service) -> bool:
        """Обновляет статус заявки с отправкой уведомления"""
        # Получаем текущий статус
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT status FROM tickets WHERE id = ?', (ticket_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False
        
        old_status = result[0]
        
        # Обновляем статус
        cursor.execute(
            "UPDATE tickets SET status = ? WHERE id = ?",
            (new_status, ticket_id)
        )
        
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        if affected_rows > 0 and old_status != new_status:
            # Отправляем уведомление об изменении статуса
            notification_service.notify_ticket_status_change(ticket_id, old_status, new_status)
        
        return affected_rows > 0

    def assign_ticket_to_master_with_notification(self, ticket_id: int, master_id: int, notification_service, user_role: str = None) -> bool:
        """Назначает заявку мастеру с отправкой уведомлений"""
        # Проверка прав доступа
        if user_role and user_role not in ['admin', 'manager']:
            return False
            
        try:
            conn = sqlite3.connect(config.DATABASE_PATH)
            cursor = conn.cursor()
            
            # Проверяем существование поля assigned_master_id
            try:
                cursor.execute("PRAGMA table_info(tickets)")
                columns = [column[1] for column in cursor.fetchall()]
                has_assigned_master = 'assigned_master_id' in columns
            except:
                has_assigned_master = False
            
            if has_assigned_master:
                cursor.execute('''
                    UPDATE tickets 
                    SET assigned_master_id = ?, status = 'in_progress' 
                    WHERE id = ? AND status = 'pending'
                ''', (master_id, ticket_id))
            else:
                cursor.execute('''
                    UPDATE tickets 
                    SET status = 'in_progress' 
                    WHERE id = ? AND status = 'pending'
                ''', (ticket_id,))
            
            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            
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
            conn = sqlite3.connect(config.DATABASE_PATH)
            cursor = conn.cursor()
            
            ticket_number = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            cursor.execute('''
                INSERT INTO tickets (ticket_number, title, description, created_date, client_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (ticket_number, title, description, datetime.now().isoformat(), client_id))
            
            ticket_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            if ticket_id:
                # Отправляем уведомление администраторам
                notification_service.notify_ticket_created(ticket_id)
            
            return True
        except Exception as e:
            print(f"Error creating ticket: {e}")
            return False

    # НОВЫЕ МЕТОДЫ ДЛЯ РЕДАКТИРОВАНИЯ ЗАЯВОК
    def update_ticket(self, ticket_id: int, title: str, description: str, user_id: int, user_role: str) -> bool:
        """Обновляет заявку с проверкой прав"""
        try:
            conn = sqlite3.connect(config.DATABASE_PATH)
            cursor = conn.cursor()
            
            # Проверяем права на редактирование
            if user_role == 'admin':
                # Админ может редактировать любую заявку
                cursor.execute('''
                    UPDATE tickets 
                    SET title = ?, description = ? 
                    WHERE id = ?
                ''', (title, description, ticket_id))
            
            elif user_role == 'client':
                # Клиент может редактировать только свои заявки в статусе pending
                cursor.execute('''
                    UPDATE tickets 
                    SET title = ?, description = ? 
                    WHERE id = ? AND client_id = ? AND status = 'pending'
                ''', (title, description, ticket_id, user_id))
            
            elif user_role == 'master':
                # Мастер может редактировать только назначенные ему заявки
                cursor.execute('''
                    UPDATE tickets 
                    SET title = ?, description = ? 
                    WHERE id = ? AND assigned_master_id = ?
                ''', (title, description, ticket_id, user_id))
            else:
                conn.close()
                return False
            
            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            
            return affected_rows > 0
            
        except Exception as e:
            print(f"Error updating ticket: {e}")
            return False

    def add_comment(self, ticket_id: int, user_id: int, user_name: str, comment_text: str) -> bool:
        """Добавляет комментарий к заявке"""
        try:
            conn = sqlite3.connect(config.DATABASE_PATH)
            cursor = conn.cursor()
            
            # Проверяем существование заявки
            cursor.execute("SELECT id FROM tickets WHERE id = ?", (ticket_id,))
            if not cursor.fetchone():
                conn.close()
                return False
            
            cursor.execute('''
                INSERT INTO comments (ticket_id, user_id, user_name, comment_text, created_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (ticket_id, user_id, user_name, comment_text, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding comment: {e}")
            return False

    def get_comments_by_ticket(self, ticket_id: int) -> List[dict]:
        """Получает все комментарии для заявки"""
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, u.role as user_role
            FROM comments c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.ticket_id = ?
            ORDER BY c.created_date ASC
        ''', (ticket_id,))
        
        comments = cursor.fetchall()
        conn.close()
        
        return [{
            'id': c[0],
            'ticket_id': c[1],
            'user_id': c[2],
            'user_name': c[3],
            'comment_text': c[4],
            'created_date': c[5],
            'user_role': c[6]
        } for c in comments]

    def get_ticket_by_id(self, ticket_id: int) -> Optional[dict]:
        """Получает заявку по ID"""
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute("PRAGMA table_info(tickets)")
            columns = [column[1] for column in cursor.fetchall()]
            has_assigned_master = 'assigned_master_id' in columns
        except:
            has_assigned_master = False
        
        if has_assigned_master:
            cursor.execute('''
                SELECT t.*, u.full_name as client_name, m.full_name as master_name
                FROM tickets t
                LEFT JOIN users u ON t.client_id = u.id
                LEFT JOIN users m ON t.assigned_master_id = m.id
                WHERE t.id = ?
            ''', (ticket_id,))
        else:
            cursor.execute('''
                SELECT t.*, u.full_name as client_name, NULL as master_name
                FROM tickets t
                LEFT JOIN users u ON t.client_id = u.id
                WHERE t.id = ?
            ''', (ticket_id,))
        
        ticket = cursor.fetchone()
        conn.close()
        
        if ticket:
            return {
                'id': ticket[0],
                'ticket_number': ticket[1],
                'title': ticket[2],
                'description': ticket[3],
                'status': ticket[4],
                'created_date': ticket[5],
                'client_id': ticket[6],
                'assigned_master_id': ticket[7] if has_assigned_master else None,
                'client_name': ticket[8],
                'master_name': ticket[9] if has_assigned_master else None
            }
        return None

    # МЕТОДЫ ДЛЯ УВЕДОМЛЕНИЙ
    def create_notification(self, user_id: int, title: str, message: str, 
                          notification_type: str, related_ticket_id: Optional[int] = None) -> bool:
        """Создает новое уведомление"""
        try:
            conn = sqlite3.connect(config.DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO notifications (user_id, title, message, notification_type, 
                                         created_date, related_ticket_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, title, message, notification_type, 
                  datetime.now().isoformat(), related_ticket_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating notification: {e}")
            return False

    def get_user_notifications(self, user_id: int, unread_only: bool = False) -> List[dict]:
        """Получает уведомления пользователя"""
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        
        query = '''
            SELECT n.*, t.ticket_number 
            FROM notifications n
            LEFT JOIN tickets t ON n.related_ticket_id = t.id
            WHERE n.user_id = ?
        '''
        
        if unread_only:
            query += ' AND n.is_read = FALSE'
        
        query += ' ORDER BY n.created_date DESC'
        
        cursor.execute(query, (user_id,))
        notifications = cursor.fetchall()
        conn.close()
        
        return [{
            'id': n[0],
            'user_id': n[1],
            'title': n[2],
            'message': n[3],
            'notification_type': n[4],
            'is_read': bool(n[5]),
            'created_date': n[6],
            'related_ticket_id': n[7],
            'ticket_number': n[8]
        } for n in notifications]

    def mark_notification_as_read(self, notification_id: int) -> bool:
        """Помечает уведомление как прочитанное"""
        try:
            conn = sqlite3.connect(config.DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE notifications SET is_read = TRUE WHERE id = ?
            ''', (notification_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error marking notification as read: {e}")
            return False

    def mark_all_notifications_as_read(self, user_id: int) -> bool:
        """Помечает все уведомления пользователя как прочитанные"""
        try:
            conn = sqlite3.connect(config.DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE notifications SET is_read = TRUE WHERE user_id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error marking all notifications as read: {e}")
            return False

    def get_unread_notifications_count(self, user_id: int) -> int:
        """Получает количество непрочитанных уведомлений"""
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM notifications 
            WHERE user_id = ? AND is_read = FALSE
        ''', (user_id,))
        
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_connection(self):
        """Возвращает соединение с базой данных (для совместимости)"""
        return sqlite3.connect(config.DATABASE_PATH)