import flet as ft
from app.ui.themes.colors import AppColors

def create_nav_bar(title: str, user_name: str, buttons: list):
    """Создает навигационную панель"""
    return ft.Row([
        ft.Text(
            f"{title} | {user_name}",
            size=16,
            weight=ft.FontWeight.BOLD
        ),
        ft.Row(buttons)
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

def create_notification_button(unread_count: int, on_click, show_count: bool = True):
    """Создает кнопку уведомлений"""
    if show_count and unread_count > 0:
        return ft.ElevatedButton(
            text=f"Уведомления ({unread_count})",
            icon="NOTIFICATIONS",
            on_click=on_click,
            style=ft.ButtonStyle(
                color=AppColors.WHITE,
                bgcolor=AppColors.PRIMARY
            )
        )
    else:
        return ft.IconButton(
            icon="NOTIFICATIONS",
            tooltip="Уведомления",
            on_click=on_click
        )

def create_logout_button(on_click):
    """Создает кнопку выхода"""
    return ft.ElevatedButton(
        "Выйти", 
        on_click=on_click,
        style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=AppColors.ERROR)
    )

def create_stats_button(on_click):
    """Создает кнопку статистики"""
    return ft.ElevatedButton(
        "📊 Статистика",
        on_click=on_click,
        style=ft.ButtonStyle(
            color=AppColors.WHITE,
            bgcolor=AppColors.PRIMARY
        )
    )

def create_create_ticket_button(on_click):
    """Создает кнопку создания заявки"""
    return ft.ElevatedButton(
        "Создать заявку",
        on_click=on_click,
        style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=AppColors.PRIMARY)
    )