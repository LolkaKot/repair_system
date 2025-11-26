# app/ui/views/dashboard/master.py

import flet as ft
import sqlite3
import threading
import time
from app.core.database import Database
from app.core.auth import AuthManager
from app.ui.components.navigation import create_nav_bar, create_notification_button, create_logout_button
from app.ui.components.ticket_cards import create_master_ticket_card
from app.ui.views.shared.notifications import NotificationsView
from app.ui.themes.colors import AppColors

class MasterDashboardView:
    def __init__(self, auth_manager, db: Database, on_logout, on_edit_ticket=None, on_show_comments=None, notification_service=None):
        self.auth_manager = auth_manager
        self.db = db
        self.on_logout = on_logout
        self.on_edit_ticket = on_edit_ticket
        self.on_show_comments = on_show_comments
        self.notification_service = notification_service
        self.page = None
        self.notification_button = None
        
        self.my_tickets_column = ft.Column(scroll=ft.ScrollMode.AUTO)
        self.available_tickets_column = ft.Column(scroll=ft.ScrollMode.AUTO)
        
        # Сразу загружаем данные
        self._my_tickets_data = self._get_my_tickets_data()
        self._available_tickets_data = self._get_available_tickets_data()
    
    def _get_my_tickets_data(self):
        """Получаем данные о назначенных заявках"""
        return self.db.get_tickets_by_master(self.auth_manager.current_user['id'])
    
    def _get_available_tickets_data(self):
        """Получаем данные о доступных заявках"""
        return self.db.get_pending_tickets()
    
    def _show_comments(self, ticket: dict):
        """Показывает комментарии к заявке"""
        if hasattr(self, 'on_show_comments') and self.on_show_comments:
            self.on_show_comments(ticket['id'])
        else:
            print(f"Would show comments for ticket {ticket['id']}")

    def _load_my_tickets(self):
        """Загружает назначенные заявки"""
        self.my_tickets_column.controls.clear()
        
        tickets = self._my_tickets_data
        
        if not tickets:
            self.my_tickets_column.controls.append(
                ft.Text("У вас нет назначенных заявок", size=16, color="grey")
            )
        else:
            for ticket in tickets:
                card = create_master_ticket_card(
                    ticket,
                    on_take=None,  # Для назначенных заявок кнопка "Взять" не нужна
                    on_status_change=self._update_status,
                    on_edit=self._edit_ticket,
                    on_comments=self._show_comments
                )
                self.my_tickets_column.controls.append(card)
        
        if self.page:
            self.my_tickets_column.update()
    
    def _load_available_tickets(self):
        """Загружает доступные заявки"""
        self.available_tickets_column.controls.clear()
        
        tickets = self._available_tickets_data
        
        if not tickets:
            self.available_tickets_column.controls.append(
                ft.Text("Нет доступных заявок", size=16, color="grey")
            )
        else:
            for ticket in tickets:
                card = create_master_ticket_card(
                    ticket,
                    on_take=self._take_ticket,
                    on_status_change=None,  # Для доступных заявок изменение статуса недоступно
                    on_edit=None,
                    on_comments=self._show_comments
                )
                self.available_tickets_column.controls.append(card)
        
        if self.page:
            self.available_tickets_column.update()
    
    def _update_notification_button(self, unread_count=None):
        """Обновляет кнопку уведомлений с актуальным счетчиком"""
        if unread_count is None:
            if hasattr(self, 'notification_service') and self.notification_service:
                unread_count = self.notification_service.notification_manager.get_unread_count(
                    self.auth_manager.current_user['id']
                )
            else:
                unread_count = 0
        
        print(f"Обновление кнопки уведомлений (admin/master): {unread_count} непрочитанных")
        
        # Сохраняем старую кнопку для замены
        old_button = self.notification_button
        
        # Создаем новую кнопку
        if unread_count > 0:
            self.notification_button = create_notification_button(unread_count, self._show_notifications, show_count=True)
        else:
            self.notification_button = create_notification_button(unread_count, self._show_notifications, show_count=False)
        
        # Если страница существует, заменяем кнопку в интерфейсе
        if self.page and hasattr(self, '_current_nav_bar'):
            self._replace_button_in_nav_bar(old_button, self.notification_button)
        
        if self.page:
            self.page.update()

    def _replace_button_in_nav_bar(self, old_button, new_button):
        """Заменяет кнопку в навигационной панели"""
        def find_and_replace(control):
            if hasattr(control, 'controls'):
                for i, child in enumerate(control.controls):
                    if child == old_button:
                        # Нашли старую кнопку - заменяем на новую
                        control.controls[i] = new_button
                        print("Кнопка уведомлений заменена в навигационной панели!")
                        return True
                    elif find_and_replace(child):
                        return True
            return False
        
        if hasattr(self, '_current_nav_bar'):
            find_and_replace(self._current_nav_bar)
        
    def _show_notifications(self, e):
        """Показывает уведомления во всплывающем окне"""
        print("Кнопка уведомлений нажата!")
        
        if hasattr(self, 'notification_service') and self.notification_service and self.page:
            print("Создаем всплывающее окно...")
            
            notifications_view = NotificationsView(
                self.notification_service.notification_manager, 
                self.auth_manager.current_user['id'],
                on_ticket_click=self._highlight_ticket,
                on_notifications_update=self._update_notification_button
            )
            
            def close_popup(e=None):
                print("Закрытие всплывающего окна")
                # Убираем overlay со страницы
                if hasattr(self, '_notifications_overlay'):
                    self.page.overlay.remove(self._notifications_overlay)
                    self.page.update()
            
            # Создаем содержимое окна уведомлений
            content = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Уведомления", size=20, weight=ft.FontWeight.BOLD, expand=True),
                        ft.IconButton("CLOSE", on_click=close_popup),
                    ]),
                    ft.Divider(),
                    notifications_view.build_popup_content(self.page, close_popup)
                ]),
                width=600,
                height=500,
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(2, ft.Colors.BLUE_900),
                border_radius=10,
                padding=15,
            )
            
            # Создаем overlay контейнер
            overlay_content = ft.Container(
                content=ft.Stack([
                    # Полупрозрачный фон
                    ft.Container(
                        bgcolor=ft.Colors.BLACK54,
                        expand=True,
                    ),
                    # Окно уведомлений по центру
                    ft.Container(
                        content=content,
                        alignment=ft.alignment.center,
                        expand=True,
                    )
                ]),
                expand=True,
            )
            
            # Добавляем обработчик клика вне окна
            def on_overlay_click(e):
                # Закрываем только если клик был на полупрозрачном фоне
                if e.control == overlay_content:
                    close_popup()
            
            overlay_content.on_click = on_overlay_click
            
            # Создаем Stack для наложения
            self._notifications_overlay = ft.Stack(
                [
                    overlay_content
                ],
                expand=True,
            )
            
            # Добавляем overlay на страницу
            self.page.overlay.append(self._notifications_overlay)
            self.page.update()
            print("Всплывающее окно открыто!")
        else:
            print("Условия не выполнены:")
            print(f"notification_service: {hasattr(self, 'notification_service')}")
            print(f"page: {self.page}")
    
    def _highlight_ticket(self, ticket_id: int):
        """Подсвечивает заявку в списке"""
        # Закрываем диалоговое окно
        self.page.dialog.open = False
        
        # Показываем сообщение
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Переход к заявке #{ticket_id}"),
            bgcolor=AppColors.INFO
        )
        self.page.snack_bar.open = True
        self.page.update()
        
        print(f"Переход к заявке {ticket_id}")
    
    def _edit_ticket(self, ticket: dict):
        """Редактирует заявку (для мастера)"""
        if hasattr(self, 'on_edit_ticket') and self.on_edit_ticket:
            self.on_edit_ticket(ticket['id'])
        else:
            print(f"Would edit ticket {ticket['id']}")
    
    def _get_client_phone(self, client_id: int) -> str:
        """Получает телефон клиента"""
        try:
            conn = sqlite3.connect('repair_system.db')
            cursor = conn.cursor()
            cursor.execute("SELECT phone FROM users WHERE id = ?", (client_id,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else "Не указан"
        except:
            return "Не указан"
    
    def _take_ticket(self, ticket_id: int):
        """Берет заявку в работу"""
        print(f"Взятие заявки в работу: {ticket_id}")
        
        if hasattr(self, 'notification_service') and self.notification_service:
            print("Notification service доступен")
            success = self.db.assign_ticket_to_master_with_notification(
                ticket_id, self.auth_manager.current_user['id'], self.notification_service
            )
        else:
            print("Notification service НЕ доступен")
            success = self.db.assign_ticket_to_master(ticket_id, self.auth_manager.current_user['id'])
        
        if success:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Заявка взята в работу!"),
                bgcolor=AppColors.SUCCESS
            )
            self.page.snack_bar.open = True
            # Обновляем данные
            self._my_tickets_data = self._get_my_tickets_data()
            self._available_tickets_data = self._get_available_tickets_data()
            self._load_my_tickets()
            self._load_available_tickets()
            self.page.update()
        else:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Ошибка при взятии заявки в работу"),
                bgcolor=AppColors.ERROR
            )
            self.page.snack_bar.open = True
            self.page.update()

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
    
    def _update_status(self, ticket_id: int, status: str):
        """Обновляет статус заявки"""
        print(f"Обновление статуса заявки {ticket_id} на {status}")
        
        if hasattr(self, 'notification_service') and self.notification_service:
            print("Notification service доступен")
            success = self.db.update_ticket_status_with_notification(
                ticket_id, status, self.notification_service
            )
        else:
            print("Notification service НЕ доступен")
            success = self.db.update_ticket_status(ticket_id, status)
        
        if success:
            status_texts = {
                'in_progress': 'в работу',
                'waiting_parts': 'ожидание запчастей', 
                'completed': 'завершена'
            }
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Статус заявки изменен на '{status_texts[status]}'"),
                bgcolor=AppColors.SUCCESS
            )
            self.page.snack_bar.open = True
            # Обновляем данные
            self._my_tickets_data = self._get_my_tickets_data()
            self._load_my_tickets()
            self.page.update()
        else:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Ошибка при изменении статуса"),
                bgcolor=AppColors.ERROR
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _on_refresh(self, e):
        """Обработчик обновления"""
        self._my_tickets_data = self._get_my_tickets_data()
        self._available_tickets_data = self._get_available_tickets_data()
        self._load_my_tickets()
        self._load_available_tickets()
    
    def build(self, page: ft.Page):
        self.page = page
        
        # Инициализируем кнопку уведомлений
        self._update_notification_button()
        
        # Создаем кнопки для навигационной панели (без кнопки "Обновить")
        nav_buttons = [
            self.notification_button,
            create_logout_button(lambda _: self.on_logout())
        ]
        
        # Навигационная панель
        nav_bar = create_nav_bar(
            "Панель мастера",
            self.auth_manager.current_user['full_name'],
            nav_buttons
        )
        
        # Сохраняем ссылку на навигационную панель для будущих обновлений
        self._current_nav_bar = nav_bar
        
        # Создаем вкладки
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Мои заявки",
                    content=ft.Container(
                        content=self.my_tickets_column,
                        padding=20
                    )
                ),
                ft.Tab(
                    text="Доступные заявки",
                    content=ft.Container(
                        content=self.available_tickets_column,
                        padding=20
                    )
                )
        ]
        )
        
        main_content = ft.Column([
            nav_bar,
            ft.Divider(),
            tabs
        ])
        
        # Загружаем заявки после создания интерфейса
        def delayed_load():
            time.sleep(0.1)
            self._load_my_tickets()
            self._load_available_tickets()
        
        threading.Thread(target=delayed_load, daemon=True).start()
        
        return main_content