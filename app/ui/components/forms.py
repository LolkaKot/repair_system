import flet as ft
from app.ui.themes.colors import AppColors

def create_form_field(label: str, width: int = 400, password: bool = False, multiline: bool = False, **kwargs):
    """Создает стандартное поле формы"""
    return ft.TextField(
        label=label,
        width=width,
        password=password,
        can_reveal_password=password,
        multiline=multiline,
        **kwargs
    )

def create_search_field(on_change=None, width: int = 400):
    """Создает поле поиска"""
    return ft.TextField(
        label="Поиск заявок...",
        on_change=on_change,
        width=width
    )

def create_status_filter(on_change=None, width: int = 200):
    """Создает фильтр по статусу"""
    return ft.Dropdown(
        label="Фильтр по статусу",
        width=width,
        options=[
            ft.dropdown.Option("all", "Все заявки"),
            ft.dropdown.Option("pending", "Ожидают"),
            ft.dropdown.Option("in_progress", "В работе"),
            ft.dropdown.Option("completed", "Завершены"),
            ft.dropdown.Option("cancelled", "Отменены"),
        ],
        value="all",
        on_change=on_change
    )

def create_date_filter(on_change=None, width: int = 200, label: str = "Сортировка по дате"):
    """Создает фильтр по дате"""
    return ft.Dropdown(
        label=label,
        width=width,
        options=[
            ft.dropdown.Option("newest", "Сначала новые"),
            ft.dropdown.Option("oldest", "Сначала старые")
        ],
        value="newest",
        on_change=on_change
    )

def create_button(text: str, on_click, color: str = AppColors.PRIMARY, width: int = None):
    """Создает стандартную кнопку"""
    return ft.ElevatedButton(
        text=text,
        on_click=on_click,
        style=ft.ButtonStyle(
            color=AppColors.WHITE,
            bgcolor=color
        ),
        width=width
    )

def create_icon_button(icon: str, on_click, tooltip: str = None, color: str = AppColors.PRIMARY):
    """Создает кнопку с иконкой"""
    return ft.IconButton(
        icon=icon,
        tooltip=tooltip,
        on_click=on_click,
        icon_color=color
    )