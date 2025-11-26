import flet as ft
from app.core.database import Database
from app.ui.components.forms import create_form_field, create_button
from app.ui.components.base import BaseComponent
from app.ui.themes.colors import AppColors

class TicketCreateView(BaseComponent):
    def __init__(self, db: Database, current_user: dict, on_back, on_ticket_created, notification_service=None):
        super().__init__()
        self.db = db
        self.current_user = current_user
        self.on_back = on_back
        self.on_ticket_created = on_ticket_created
        self.notification_service = notification_service
        
        self.title_field = create_form_field(
            "Название заявки*", 
            width=400,
            helper_text="Краткое описание проблемы"
        )
        self.description_field = create_form_field(
            "Подробное описание проблемы*", 
            width=400,
            multiline=True,
            min_lines=3,
            max_lines=5
        )
        self.equipment_field = create_form_field(
            "Оборудование",
            width=400,
            helper_text="Модель и марка оборудования"
        )
        self.fault_type_field = create_form_field(
            "Тип неисправности",
            width=400,
            helper_text="Например: не включается, не печатает и т.д."
        )
        self.error_text = ft.Text("", color=AppColors.ERROR)
        self.success_text = ft.Text("", color=AppColors.SUCCESS)
    
    def _create_ticket(self, e):
        # Валидация
        if not all([
            self.title_field.value,
            self.description_field.value
        ]):
            self.error_text.value = "Заполните все обязательные поля (отмечены *)"
            self.error_text.update()
            return
        
        print("Создание заявки...")
        
        # Создание заявки через метод базы данных с уведомлениями
        if hasattr(self, 'notification_service') and self.notification_service:
            print("Notification service доступен")
            success = self.db.create_ticket_with_notification(
                title=self.title_field.value,
                description=self.description_field.value,
                client_id=self.current_user['id'],
                notification_service=self.notification_service
            )
        else:
            print("Notification service НЕ доступен")
            success = self.db.create_ticket(
                title=self.title_field.value,
                description=self.description_field.value,
                client_id=self.current_user['id']
            )
        
        if success:
            self.success_text.value = "Заявка успешно создана! Вы получите уведомление о смене статуса."
            self.success_text.update()
            
            # Очищаем форму
            self.title_field.value = ""
            self.description_field.value = ""
            self.equipment_field.value = ""
            self.fault_type_field.value = ""
            self.title_field.update()
            self.description_field.update()
            self.equipment_field.update()
            self.fault_type_field.update()
            
            # Уведомляем о создании заявки
            self.on_ticket_created()
        else:
            self.error_text.value = "Ошибка при создании заявки"
            self.error_text.update()
    
    def build(self):
        return ft.Column([
            ft.Row([
                ft.TextButton(
                    "← Назад",
                    on_click=lambda _: self.on_back()
                ),
                ft.Text("Создание новой заявки", size=20, weight=ft.FontWeight.BOLD),
            ]),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Заполните информацию о проблеме", size=16),
                        ft.Text("Поля со * обязательны для заполнения", size=12, color=AppColors.GREY),
                        
                        ft.Text("Основная информация", size=14, weight=ft.FontWeight.BOLD),
                        self.title_field,
                        self.description_field,
                        
                        ft.Text("Дополнительная информация", size=14, weight=ft.FontWeight.BOLD),
                        self.equipment_field,
                        self.fault_type_field,
                        
                        ft.Container(height=10),
                        
                        ft.Row([
                            create_button(
                                "Создать заявку",
                                self._create_ticket,
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
                        
                        ft.Container(height=10),
                        ft.Divider(),
                        
                        ft.Text("Что происходит после создания заявки?", size=12, weight=ft.FontWeight.BOLD),
                        ft.Column([
                            ft.Row([
                                ft.Icon("INFO", size=16, color=AppColors.INFO),
                                ft.Text("Администратор получит уведомление о новой заявке", size=12),
                            ]),
                            ft.Row([
                                ft.Icon("INFO", size=16, color=AppColors.INFO),
                                ft.Text("Вам будет назначен мастер для выполнения работ", size=12),
                            ]),
                            ft.Row([
                                ft.Icon("INFO", size=16, color=AppColors.INFO),
                                ft.Text("Вы будете получать уведомления об изменении статуса", size=12),
                            ]),
                        ], spacing=5)
                    ]),
                    padding=20
                )
            )
        ])