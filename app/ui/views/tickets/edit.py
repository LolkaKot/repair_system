import flet as ft
import threading
import time
from app.core.database import Database
from app.ui.components.forms import create_form_field, create_button
from app.ui.components.base import BaseComponent
from app.ui.themes.colors import AppColors

class TicketEditView(BaseComponent):
    def __init__(self, db: Database, current_user: dict, ticket_id: int, on_back, on_ticket_updated):
        super().__init__()
        self.db = db
        self.current_user = current_user
        self.ticket_id = ticket_id
        self.on_back = on_back
        self.on_ticket_updated = on_ticket_updated
        
        # Загружаем данные заявки
        self.ticket = self.db.get_ticket_by_id(ticket_id)
        
        # Поля формы
        self.title_field = create_form_field(
            "Название заявки*",
            width=400,
            value=self.ticket['title'] if self.ticket else "",
            helper_text="Краткое описание проблемы"
        )
        self.description_field = create_form_field(
            "Подробное описание проблемы*",
            width=400,
            multiline=True,
            min_lines=3,
            max_lines=5,
            value=self.ticket['description'] if self.ticket else ""
        )
        
        self.error_text = ft.Text("", color=AppColors.ERROR)
        self.success_text = ft.Text("", color=AppColors.SUCCESS)
        
        # Информация о заявке (только для чтения)
        self.ticket_info = self._create_ticket_info()
    
    def _create_ticket_info(self):
        """Создает блок с информацией о заявке (только для чтения)"""
        if not self.ticket:
            return ft.Text("Заявка не найдена", color=AppColors.ERROR)
        
        status_colors = {
            'pending': AppColors.PENDING,
            'in_progress': AppColors.IN_PROGRESS,
            'waiting_parts': AppColors.WAITING_PARTS,
            'completed': AppColors.COMPLETED,
            'cancelled': AppColors.CANCELLED
        }
        
        status_color = status_colors.get(self.ticket['status'], AppColors.GREY)
        
        return ft.Column([
            ft.Row([
                ft.Text("Информация о заявке:", weight=ft.FontWeight.BOLD, size=14),
            ]),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(f"№: {self.ticket['ticket_number']}", weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Text(
                                self.ticket['status'].replace('_', ' ').upper(),
                                color=ft.Colors.WHITE,
                                size=10,
                                weight=ft.FontWeight.BOLD
                            ),
                            bgcolor=status_color,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            border_radius=6
                        )
                    ]),
                    ft.Text(f"Статус: {self.ticket['status']}"),
                    ft.Text(f"Создана: {self._format_date(self.ticket['created_date'])}"),
                    ft.Text(f"Клиент: {self.ticket['client_name']}"),
                    ft.Text(f"Мастер: {self.ticket.get('master_name', 'Не назначен')}"),
                ], spacing=5),
                bgcolor=AppColors.GREY_LIGHT,
                padding=10,
                border_radius=8
            )
        ])
    
    def _format_date(self, date_string: str) -> str:
        """Форматирует дату в читаемый вид"""
        try:
            from datetime import datetime
            # Парсим дату из ISO формата
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            # Форматируем в удобный вид: "дд.мм.гггг чч:мм"
            return dt.strftime("%d.%m.%Y %H:%M")
        except:
            # Если не удалось распарсить, возвращаем как есть
            return date_string[:16].replace('T', ' ')
    
    def _update_ticket(self, e):
        """Обновляет заявку"""
        if not self.ticket:
            self.error_text.value = "Заявка не найдена"
            self.error_text.update()
            return
        
        # Валидация
        if not all([self.title_field.value, self.description_field.value]):
            self.error_text.value = "Заполните все обязательные поля"
            self.error_text.update()
            return
        
        # Проверяем, изменились ли данные
        if (self.title_field.value == self.ticket['title'] and 
            self.description_field.value == self.ticket['description']):
            self.error_text.value = "Данные не изменились"
            self.error_text.update()
            return
        
        # Обновляем заявку
        success = self.db.update_ticket(
            self.ticket_id,
            self.title_field.value,
            self.description_field.value,
            self.current_user['id'],
            self.current_user['role']
        )
        
        if success:
            self.success_text.value = "Заявка успешно обновлена!"
            self.success_text.update()
            
            # Уведомляем об успешном обновлении
            self.on_ticket_updated()
            
            # Возвращаемся назад через 1 секунду
            def delayed_back():
                time.sleep(1)
                self.on_back()
            threading.Thread(target=delayed_back, daemon=True).start()
        else:
            self.error_text.value = "Ошибка при обновлении заявки. Проверьте права доступа."
            self.error_text.update()
    
    def build(self):
        if not self.ticket:
            return ft.Column([
                ft.TextButton("← Назад", on_click=lambda _: self.on_back()),
                ft.Text("Заявка не найдена", size=20, color=AppColors.ERROR)
            ])
        
        # Проверяем права на редактирование
        can_edit = False
        if self.current_user['role'] == 'admin':
            can_edit = True
        elif self.current_user['role'] == 'client' and self.ticket['client_id'] == self.current_user['id'] and self.ticket['status'] == 'pending':
            can_edit = True
        elif self.current_user['role'] == 'master' and self.ticket.get('assigned_master_id') == self.current_user['id']:
            can_edit = True
        
        if not can_edit:
            return ft.Column([
                ft.TextButton("← Назад", on_click=lambda _: self.on_back()),
                ft.Text("Редактирование заявки", size=20, weight=ft.FontWeight.BOLD),
                self.ticket_info,
                ft.Container(height=20),
                ft.Text("У вас нет прав для редактирования этой заявки", 
                       color=AppColors.ERROR, size=16),
                ft.Text("Возможные причины:", size=14, weight=ft.FontWeight.BOLD),
                ft.Text("• Заявка уже находится в работе", size=12),
                ft.Text("• Заявка назначена другому мастеру", size=12),
                ft.Text("• Заявка завершена или отменена", size=12),
            ])
        
        return ft.Column([
            ft.Row([
                ft.TextButton(
                    "← Назад",
                    on_click=lambda _: self.on_back()
                ),
                ft.Text("Редактирование заявки", size=20, weight=ft.FontWeight.BOLD),
            ]),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        self.ticket_info,
                        ft.Divider(),
                        ft.Text("Редактирование информации", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text("Поля со * обязательны для заполения", size=12, color=AppColors.GREY),
                        
                        self.title_field,
                        self.description_field,
                        
                        ft.Container(height=10),
                        
                        ft.Row([
                            create_button(
                                "Сохранить изменения",
                                self._update_ticket,
                                color=AppColors.PRIMARY,
                                width=200
                            ),
                            ft.TextButton(
                                "Отмена",
                                on_click=lambda _: self.on_back(),
                                style=ft.ButtonStyle(padding=ft.padding.symmetric(horizontal=20, vertical=12))
                            )
                        ]),
                        self.error_text,
                        self.success_text,
                    ]),
                    padding=20
                )
            )
        ])