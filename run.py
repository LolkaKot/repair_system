"""
Точка входа для запуска системы учета заявок на ремонт
"""

import flet as ft
from app.main import main

if __name__ == "__main__":
    print("Запуск системы учета заявок на ремонт оборудования...")
    print("=" * 50)
    print("Доступные тестовые пользователи:")
    print("  Администратор: admin / admin123")
    print("  Менеджер: manager / manager123")
    print("  Мастер: master1 / master123")
    print("  Клиент: client1 / client123")
    print("=" * 50)
    
    try:
        # Запуск приложения
        ft.app(
            target=main,
            view=ft.AppView.FLET_APP,
            port=8550
        )
    except Exception as e:
        print(f"Ошибка при запуске: {e}")
        input("Нажмите Enter для выхода...")
