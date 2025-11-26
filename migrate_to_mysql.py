#!/usr/bin/env python3
"""
Скрипт миграции данных из SQLite в MySQL
"""

import sqlite3
import mysql.connector
from datetime import datetime
import sys
import os

def get_mysql_config():
    """Получает настройки MySQL из config.py или запрашивает у пользователя"""
    try:
        # Пробуем импортировать из config.py
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
        import app.config as config
        
        # Проверяем есть ли настройки MySQL
        if hasattr(config, 'MYSQL_HOST'):
            return {
                'host': config.MYSQL_HOST,
                'port': config.MYSQL_PORT,
                'user': config.MYSQL_USER,
                'password': config.MYSQL_PASSWORD,
                'database': config.MYSQL_DATABASE
            }
    except:
        pass
    
    # Если настроек нет - запрашиваем у пользователя
    print("🔧 Настройки MySQL не найдены в config.py")
    print("📝 Введите данные для подключения к MySQL:")
    
    return {
        'host': input("Хост [localhost]: ") or "localhost",
        'port': int(input("Порт [3306]: ") or "3306"),
        'user': input("Пользователь [root]: ") or "root",
        'password': input("Пароль: "),
        'database': input("База данных [repair_system]: ") or "repair_system"
    }

def migrate_data():
    """Переносит данные из SQLite в MySQL"""
    
    print("=" * 50)
    print("МИГРАЦИЯ ДАННЫХ ИЗ SQLITE В MYSQL")
    print("=" * 50)
    
    # Получаем настройки MySQL
    mysql_config = get_mysql_config()
    
    # Проверяем существование SQLite базы
    if not os.path.exists('repair_system.db'):
        print("❌ Файл repair_system.db не найден!")
        return False
    
    # Подключение к SQLite
    try:
        sqlite_conn = sqlite3.connect('repair_system.db')
        sqlite_cursor = sqlite_conn.cursor()
        print("✅ Подключение к SQLite успешно")
    except Exception as e:
        print(f"❌ Ошибка подключения к SQLite: {e}")
        return False
    
    # Подключение к MySQL
    try:
        mysql_conn = mysql.connector.connect(**mysql_config)
        mysql_cursor = mysql_conn.cursor()
        print("✅ Подключение к MySQL успешно")
    except Exception as e:
        print(f"❌ Ошибка подключения к MySQL: {e}")
        sqlite_conn.close()
        return False
    
    try:
        # 1. Миграция пользователей
        print("\n📋 Миграция пользователей...")
        sqlite_cursor.execute("SELECT id, username, password, full_name, role, email, phone FROM users")
        users = sqlite_cursor.fetchall()
        
        for user in users:
            mysql_cursor.execute(
                "INSERT IGNORE INTO users (id, username, password, full_name, role, email, phone) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                user
            )
        print(f"✅ Перенесено пользователей: {len(users)}")
        
        # 2. Миграция заявок
        print("\n📋 Миграция заявок...")
        sqlite_cursor.execute("SELECT id, ticket_number, title, description, status, created_date, client_id, assigned_master_id FROM tickets")
        tickets = sqlite_cursor.fetchall()
        
        for ticket in tickets:
            # Конвертируем дату если нужно
            created_date = ticket[5]
            if isinstance(created_date, str) and 'T' in created_date:
                created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
            
            mysql_cursor.execute(
                "INSERT IGNORE INTO tickets (id, ticket_number, title, description, status, created_date, client_id, assigned_master_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (*ticket[:5], created_date, *ticket[6:])
            )
        print(f"✅ Перенесено заявок: {len(tickets)}")
        
        # 3. Миграция комментариев
        print("\n📋 Миграция комментариев...")
        sqlite_cursor.execute("SELECT id, ticket_id, user_id, user_name, comment_text, created_date FROM comments")
        comments = sqlite_cursor.fetchall()
        
        for comment in comments:
            # Конвертируем дату если нужно
            created_date = comment[5]
            if isinstance(created_date, str) and 'T' in created_date:
                created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
            
            mysql_cursor.execute(
                "INSERT IGNORE INTO comments (id, ticket_id, user_id, user_name, comment_text, created_date) VALUES (%s, %s, %s, %s, %s, %s)",
                (*comment[:5], created_date)
            )
        print(f"✅ Перенесено комментариев: {len(comments)}")
        
        mysql_conn.commit()
        
        print("\n" + "=" * 50)
        print("🎉 МИГРАЦИЯ УСПЕШНО ЗАВЕРШЕНА!")
        print(f"📊 Статистика:")
        print(f"   👥 Пользователи: {len(users)}")
        print(f"   📝 Заявки: {len(tickets)}")
        print(f"   💬 Комментарии: {len(comments)}")
        print("=" * 50)
        
        # Сохраняем настройки в config.py
        save_config_to_file(mysql_config)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при миграции: {e}")
        mysql_conn.rollback()
        return False
    
    finally:
        sqlite_conn.close()
        mysql_conn.close()

def save_config_to_file(mysql_config):
    """Сохраняет настройки MySQL в config.py"""
    config_path = os.path.join('app', 'config.py')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем есть ли уже настройки MySQL
        if 'MYSQL_HOST' not in content:
            # Находим где добавить настройки (после DATABASE_PATH)
            if 'DATABASE_PATH = ' in content:
                insert_pos = content.find('DATABASE_PATH = ') + len('DATABASE_PATH = "repair_system.db"')
                new_content = content[:insert_pos] + f'''

# Настройки MySQL
MYSQL_HOST = "{mysql_config['host']}"
MYSQL_PORT = {mysql_config['port']}
MYSQL_USER = "{mysql_config['user']}"
MYSQL_PASSWORD = "{mysql_config['password']}"
MYSQL_DATABASE = "{mysql_config['database']}"''' + content[insert_pos:]
                
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✅ Настройки MySQL сохранены в {config_path}")
        
    except Exception as e:
        print(f"⚠️ Не удалось сохранить настройки в config.py: {e}")

if __name__ == "__main__":
    success = migrate_data()
    
    if success:
        print("\n🎯 Дальнейшие действия:")
        print("1. Убедитесь, что в app/config.py установлено: DATABASE_TYPE = 'mysql'")
        print("2. Запустите приложение: python run.py")
        print("3. Проверьте работу всех функций")
    else:
        print("\n❌ Миграция не удалась. Проверьте настройки и попробуйте снова.")
        sys.exit(1)