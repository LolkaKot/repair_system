import app.config as config
from app.core.database import Database
from app.core.mysql_database import MySQLDatabase

def create_database():
    """Создает экземпляр базы данных в зависимости от конфигурации"""
    if hasattr(config, 'DATABASE_TYPE') and config.DATABASE_TYPE == "mysql":
        print("✅ Используется MySQL база данных")
        return MySQLDatabase()
    else:
        print("⚠️ Используется SQLite база данных")
        return Database()