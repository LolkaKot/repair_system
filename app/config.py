"""
Настройки приложения
"""

# Настройки базы данных
DATABASE_TYPE = "mysql"
DATABASE_PATH = "repair_system.db"

# Настройки MySQL
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "root123"
MYSQL_DATABASE = "repair_system"

# Настройки приложения
APP_TITLE = "Система учета заявок на ремонт оборудования"
APP_WIDTH = 1200
APP_HEIGHT = 800
APP_MIN_WIDTH = 800
APP_MIN_HEIGHT = 600

# Настройки темы
THEME_MODE = "light"

# Настройки порта
DEFAULT_PORT = 8550

# Настройки уведомлений
ENABLE_NOTIFICATIONS = True

# Тестовые пользователи
TEST_USERS = {
    "admin": {"username": "admin", "password": "admin123", "role": "admin"},
    "manager": {"username": "manager", "password": "manager123", "role": "manager"},
    "master1": {"username": "master1", "password": "master123", "role": "master"},
    "client1": {"username": "client1", "password": "client123", "role": "client"}
}