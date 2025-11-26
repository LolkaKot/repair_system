import flet as ft
from datetime import datetime
from app.ui.themes.colors import AppColors

def create_ticket_card(ticket: dict, current_user: dict, on_edit=None, on_delete=None, on_comments=None):
    """Создает карточку заявки для клиента"""
    status_colors = {
        'pending': AppColors.PENDING,
        'in_progress': AppColors.IN_PROGRESS,
        'completed': AppColors.COMPLETED,
        'cancelled': AppColors.CANCELLED
    }
    
    status_color = status_colors.get(ticket['status'], AppColors.GREY)
    
    # Создаем кнопки управления
    action_buttons = []
    
    # Кнопка редактирования (только для клиентов и только pending заявки)
    if (current_user['role'] == 'client' and 
        ticket['client_id'] == current_user['id'] and 
        ticket['status'] == 'pending' and
        on_edit):
        action_buttons.append(
            ft.ElevatedButton(
                "РЕДАКТИРОВАТЬ",
                style=ft.ButtonStyle(
                    color=AppColors.WHITE,
                    bgcolor=AppColors.PRIMARY_LIGHT
                ),
                on_click=lambda e, t=ticket: on_edit(t)
            )
        )
    
    # Кнопка комментариев (только для администраторов и мастеров)
    if on_comments and current_user['role'] in ['admin', 'master']:
        action_buttons.append(
            ft.ElevatedButton(
                "Комментарии",
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=AppColors.INFO
                ),
                on_click=lambda e, t=ticket: on_comments(t)
            )
        )
    
    # Кнопка удаления
    if on_delete:
        action_buttons.append(
            ft.ElevatedButton(
                "УДАЛИТЬ",
                style=ft.ButtonStyle(
                    color=AppColors.WHITE,
                    bgcolor=AppColors.ERROR
                ),
                on_click=lambda e, t=ticket: on_delete(t)
            )
        )
    
    card_content = [
        ft.Row([
            ft.Text(f"#{ticket['ticket_number']}", weight=ft.FontWeight.BOLD, size=16),
            ft.Container(
                content=ft.Text(
                    ticket['status'].replace('_', ' ').upper(), 
                    color=ft.Colors.WHITE, 
                    size=10,
                    weight=ft.FontWeight.BOLD
                ),
                bgcolor=status_color,
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                border_radius=ft.border_radius.all(6)
            )
        ]),
        ft.Text(ticket['title'], weight=ft.FontWeight.BOLD, size=14),
        ft.Text(ticket['description'], size=12),
        ft.Text(f"Клиент: {ticket['client_name']}", size=12),
        ft.Text(f"Создана: {_format_date(ticket['created_date'])}", size=10),
    ]
    
    if action_buttons:
        card_content.append(
            ft.Row(action_buttons, alignment=ft.MainAxisAlignment.END)
        )
    
    return ft.Card(
        content=ft.Container(
            content=ft.Column(card_content),
            padding=ft.padding.all(16),
            border_radius=ft.border_radius.all(8)
        ),
        elevation=2
    )

def create_admin_ticket_card(ticket: dict, on_assign=None, on_status_change=None, on_edit=None, on_comments=None, on_delete=None):
    """Создает карточку заявки для администратора"""
    status_colors = {
        'pending': AppColors.PENDING,
        'in_progress': AppColors.IN_PROGRESS, 
        'completed': AppColors.COMPLETED,
        'cancelled': AppColors.CANCELLED
    }
    
    status_color = status_colors.get(ticket['status'], AppColors.GREY)
    
    # Создаем базовую карточку
    card_content = [
        ft.Row([
            ft.Text(f"#{ticket['ticket_number']}", weight=ft.FontWeight.BOLD, size=16),
            ft.Container(
                content=ft.Text(
                    _get_status_text(ticket['status']), 
                    color=ft.Colors.WHITE, 
                    size=10,
                    weight=ft.FontWeight.BOLD
                ),
                bgcolor=status_color,
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                border_radius=ft.border_radius.all(6)
            )
        ]),
        ft.Text(ticket['title'], weight=ft.FontWeight.BOLD, size=14),
        ft.Text(ticket['description'], size=12),
        ft.Text(f"Клиент: {ticket['client_name']}", size=12),
        ft.Text(f"Мастер: {ticket.get('master_name', 'Не назначен')}", size=12),
        ft.Text(f"Создана: {_format_date(ticket['created_date'])}", size=10),
    ]
    
    # Создаем кнопки управления для администратора
    action_rows = []
    
    # Первый ряд: назначение мастера и изменение статуса
    first_row_buttons = []
    
    # Кнопка назначения/смены мастера
    if on_assign:
        master_button_text = "Назначить мастера" if not ticket.get('assigned_master_id') else "Сменить мастера"
        master_button_color = AppColors.PRIMARY if not ticket.get('assigned_master_id') else AppColors.PRIMARY_LIGHT
        
        first_row_buttons.append(
            ft.ElevatedButton(
                master_button_text,
                style=ft.ButtonStyle(
                    color=AppColors.WHITE,
                    bgcolor=master_button_color
                ),
                on_click=lambda e, t=ticket: on_assign(t)
            )
        )
    
    # Выпадающий список для изменения статуса
    if on_status_change:
        status_dropdown = ft.Dropdown(
            label="Изменить статус",
            width=180,
            options=[
                ft.dropdown.Option("pending", "Ожидание"),
                ft.dropdown.Option("in_progress", "В работе"),
                ft.dropdown.Option("completed", "Завершена"),
                ft.dropdown.Option("cancelled", "Отменена")
            ],
            value=ticket['status'],
            on_change=lambda e, t=ticket: on_status_change(t, e.control.value),
            tooltip="Для статусов 'В работе' и 'Завершена' должен быть назначен мастер" if not ticket.get('assigned_master_id') else None
        )
        first_row_buttons.append(status_dropdown)
    
    if first_row_buttons:
        action_rows.append(ft.Row(first_row_buttons, spacing=10))
    
    # Второй ряд: дополнительные действия
    second_row_buttons = []
    
    if on_edit:
        second_row_buttons.append(
            ft.ElevatedButton(
                "Редактировать",
                style=ft.ButtonStyle(
                    color=AppColors.WHITE,
                    bgcolor=AppColors.PRIMARY_LIGHT
                ),
                on_click=lambda e, t=ticket: on_edit(t)
            )
        )
    
    if on_comments:
        second_row_buttons.append(
            ft.ElevatedButton(
                "Комментарии",
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=AppColors.INFO
                ),
                on_click=lambda e, t=ticket: on_comments(t)
            )
        )
    
    if on_delete:
        second_row_buttons.append(
            ft.ElevatedButton(
                "Удалить",
                style=ft.ButtonStyle(
                    color=AppColors.WHITE,
                    bgcolor=AppColors.ERROR
                ),
                on_click=lambda e, t=ticket: on_delete(t)
            )
        )
    
    if second_row_buttons:
        action_rows.append(ft.Row(second_row_buttons, alignment=ft.MainAxisAlignment.END))
    
    # Добавляем все кнопки в карточку
    card_content.extend(action_rows)
    
    return ft.Card(
        content=ft.Container(
            content=ft.Column(card_content),
            padding=ft.padding.all(16),
            border_radius=ft.border_radius.all(8)
        ),
        elevation=2
    )

def create_master_ticket_card(ticket: dict, on_take=None, on_status_change=None, on_edit=None, on_comments=None, show_client_phone=True):
    """Создает карточку заявки для мастера"""
    status_colors = {
        'pending': AppColors.PENDING,
        'in_progress': AppColors.IN_PROGRESS,
        'waiting_parts': AppColors.WAITING_PARTS,
        'completed': AppColors.COMPLETED,
        'cancelled': AppColors.CANCELLED
    }
    
    status_color = status_colors.get(ticket['status'], AppColors.GREY)
    
    card_content = [
        ft.Row([
            ft.Text(f"#{ticket['ticket_number']}", weight=ft.FontWeight.BOLD, size=16),
            ft.Container(
                content=ft.Text(
                    ticket['status'].replace('_', ' ').upper(), 
                    color=ft.Colors.WHITE, 
                    size=10,
                    weight=ft.FontWeight.BOLD
                ),
                bgcolor=status_color,
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                border_radius=ft.border_radius.all(6)
            )
        ]),
        ft.Text(ticket['title'], weight=ft.FontWeight.BOLD, size=14),
        ft.Text(ticket['description'], size=12),
        ft.Text(f"Клиент: {ticket['client_name']}", size=12),
        ft.Text(f"Создана: {_format_date(ticket['created_date'])}", size=10),
    ]
    
    # Добавляем кнопки управления статусом
    status_controls = []
    
    # Кнопка комментариев (для всех статусов)
    if on_comments:
        status_controls.append(
            ft.ElevatedButton(
                "Комментарии",
                on_click=lambda e, t=ticket: on_comments(t),
                style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=AppColors.INFO)
            )
        )
    
    # Кнопка редактирования
    if on_edit and ticket['status'] in ['in_progress', 'waiting_parts']:
        status_controls.append(
            ft.ElevatedButton(
                "Редактировать",
                on_click=lambda e, t=ticket: on_edit(t),
                style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=AppColors.PRIMARY_LIGHT)
            )
        )
    
    if ticket['status'] == 'in_progress':
        if on_status_change:
            status_controls.extend([
                ft.ElevatedButton(
                    "Ожидает запчасти",
                    on_click=lambda e, t=ticket: on_status_change(t['id'], 'waiting_parts'),
                    style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=AppColors.WARNING)
                ),
                ft.ElevatedButton(
                    "Завершить",
                    on_click=lambda e, t=ticket: on_status_change(t['id'], 'completed'),
                    style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=AppColors.SUCCESS)
                )
            ])
    elif ticket['status'] == 'waiting_parts':
        if on_status_change:
            status_controls.extend([
                ft.ElevatedButton(
                    "В работу",
                    on_click=lambda e, t=ticket: on_status_change(t['id'], 'in_progress'),
                    style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=AppColors.IN_PROGRESS)
                ),
                ft.ElevatedButton(
                    "Завершить",
                    on_click=lambda e, t=ticket: on_status_change(t['id'], 'completed'),
                    style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=AppColors.SUCCESS)
                )
            ])
    elif ticket['status'] == 'pending' and on_take:
        status_controls.append(
            ft.ElevatedButton(
                "Взять в работу",
                on_click=lambda e, t=ticket: on_take(t['id']),
                style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=AppColors.PRIMARY)
            )
        )
    
    if status_controls:
        card_content.append(
            ft.Row(status_controls, spacing=5, wrap=True, alignment=ft.MainAxisAlignment.START)
        )
    
    return ft.Card(
        content=ft.Container(
            content=ft.Column(card_content),
            padding=ft.padding.all(16),
            border_radius=ft.border_radius.all(8)
        ),
        elevation=2
    )

def _get_status_text(status: str) -> str:
    """Возвращает читаемый текст статуса"""
    status_texts = {
        'pending': 'ОЖИДАЕТ',
        'in_progress': 'В РАБОТЕ',
        'completed': 'ЗАВЕРШЕНА',
        'cancelled': 'ОТМЕНЕНА'
    }
    return status_texts.get(status, status.upper())

def _format_date(date_string: str) -> str:
    """Форматирует дату в читаемый вид"""
    try:
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime("%d.%m.%Y %H:%M")
    except:
        return date_string[:16].replace('T', ' ')