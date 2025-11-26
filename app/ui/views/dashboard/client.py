import flet as ft
from app.core.database import Database
from app.core.auth import AuthManager
from app.ui.components.navigation import create_nav_bar, create_notification_button, create_logout_button, create_create_ticket_button
from app.ui.components.forms import create_search_field
from app.ui.components.ticket_cards import create_ticket_card
from app.ui.views.shared.notifications import NotificationsView
from app.ui.themes.colors import AppColors

class ClientDashboardView:
    def __init__(self, auth_manager, db: Database, on_logout, on_create_ticket=None, on_edit_ticket=None,
                 notification_manager=None, notification_service=None):
        self.auth_manager = auth_manager
        self.db = db
        self.on_logout = on_logout
        self.on_create_ticket = on_create_ticket
        self.on_edit_ticket = on_edit_ticket
        self.notification_manager = notification_manager
        self.notification_service = notification_service
        self.page = None
        
        # Добавляем инициализацию кнопки уведомлений
        self.notification_button = None
        
        self.tickets_column = ft.Column(scroll=ft.ScrollMode.AUTO)
        self.search_field = create_search_field(on_change=self._on_search, width=400)
        
        # Сразу загружаем данные
        self._tickets_data = self._get_tickets_data()
    
    def _update_notification_button(self, unread_count=None):
        """Обновляет кнопку уведомлений с актуальным счетчиком"""
        if unread_count is None:
            if self.notification_manager:
                unread_count = self.notification_manager.get_unread_count(
                    self.auth_manager.current_user['id']
                )
            else:
                unread_count = 0
        
        print(f"Обновление кнопки уведомлений: {unread_count} непрочитанных")
        
        # Создаем новую кнопку
        if unread_count > 0:
            new_button = create_notification_button(unread_count, self._show_notifications, show_count=True)
        else:
            new_button = create_notification_button(unread_count, self._show_notifications, show_count=False)
        
        # Сохраняем новую кнопку
        old_button = self.notification_button
        self.notification_button = new_button
        
        # Находим и заменяем кнопку в интерфейсе
        if self.page and hasattr(self, '_current_content'):
            self._replace_button_in_interface(old_button, new_button)
        
        if self.page:
            self.page.update()

    def _replace_button_in_interface(self, old_button, new_button):
        """Заменяет кнопку в интерфейсе"""
        def find_and_replace(control):
            if hasattr(control, 'controls'):
                for i, child in enumerate(control.controls):
                    if child == old_button:
                        # Нашли старую кнопку - заменяем на новую
                        control.controls[i] = new_button
                        print("Кнопка заменена в интерфейсе!")
                        return True
                    elif find_and_replace(child):
                        return True
            return False
        
        if hasattr(self, '_current_content'):
            find_and_replace(self._current_content)
    
    def _get_tickets_data(self):
        """Получаем данные о заявках без обновления UI"""
        if self.auth_manager.is_client():
            return self.db.get_tickets_by_client(self.auth_manager.current_user['id'])
        else:
            return self.db.get_all_tickets()
    
    def _show_comments(self, ticket: dict):
        """Показывает комментарии к заявке"""
        # Для клиента комментарии показываются через отдельный view
        print(f"Would show comments for ticket {ticket['id']}")

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
        # Закрываем всплывающее окно уведомлений
        if hasattr(self, '_notifications_overlay'):
            self.page.overlay.remove(self._notifications_overlay)
        
        # Показываем сообщение
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Переход к заявке #{ticket_id}"),
            bgcolor=AppColors.INFO
        )
        self.page.snack_bar.open = True
        self.page.update()
        
        print(f"Переход к заявке {ticket_id}")
        
        # Здесь можно добавить логику для подсветки конкретной заявки
        # Например, прокрутка к заявке или выделение ее цветом
    
    def _edit_ticket(self, ticket: dict):
        """Переходит к редактированию заявки"""
        if hasattr(self, 'on_edit_ticket') and self.on_edit_ticket:
            self.on_edit_ticket(ticket['id'])
        else:
            print(f"Would edit ticket {ticket['id']}")
    
    def _delete_ticket(self, ticket: dict):
        """Удаляет заявку"""
        if not self.page:
            return
        
        success = self.db.delete_ticket(
            ticket['id'], 
            self.auth_manager.current_user['id'],
            self.auth_manager.current_user['role']
        )
        
        if success:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Заявка успешно удалена!"),
                bgcolor=AppColors.SUCCESS
            )
            self.page.snack_bar.open = True
            
            self._tickets_data = self._get_tickets_data()
            self._build_tickets_column(self.search_field.value)
            self.tickets_column.update()
        else:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Ошибка: Не удалось удалить заявку или нет прав"),
                bgcolor=AppColors.ERROR
            )
            self.page.snack_bar.open = True
        
        self.page.update()
    
    def _build_tickets_column(self, search_query=None):
        """Строит колонку с заявками"""
        tickets = self._tickets_data
        
        if search_query:
            search_query = search_query.lower()
            tickets = [t for t in tickets if 
                    search_query in t['title'].lower() or 
                    search_query in t['ticket_number'].lower()]
        
        self.tickets_column.controls.clear()
        
        if not tickets:
            if self.auth_manager.is_client():
                self.tickets_column.controls.append(
                    ft.Column([
                        ft.Text("У вас пока нет заявок", size=16, color=AppColors.GREY),
                        create_create_ticket_button(
                            lambda _: self.on_create_ticket() if self.on_create_ticket else None
                        ) if self.on_create_ticket else None
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                )
            else:
                self.tickets_column.controls.append(
                    ft.Text("Заявки не найдены", size=16, color=AppColors.GREY)
                )
        else:
            for ticket in tickets:
                # Для клиентов не показываем кнопку комментариев
                if self.auth_manager.is_client():
                    card = create_ticket_card(
                        ticket, 
                        self.auth_manager.current_user,
                        on_edit=self._edit_ticket,
                        on_delete=self._delete_ticket,
                        on_comments=None  # Не передаем колбэк для комментариев
                    )
                else:
                    card = create_ticket_card(
                        ticket, 
                        self.auth_manager.current_user,
                        on_edit=self._edit_ticket,
                        on_delete=self._delete_ticket,
                        on_comments=self._show_comments
                    )
                self.tickets_column.controls.append(card)
    
    def _on_search(self, e):
        """Обработчик поиска"""
        self._build_tickets_column(e.control.value)
        self.tickets_column.update()
    
    def _on_refresh(self, e):
        """Обработчик обновления"""
        self._tickets_data = self._get_tickets_data()
        self._build_tickets_column(self.search_field.value)
        self.tickets_column.update()
    
    def build(self, page: ft.Page = None):
        """Строит весь интерфейс"""
        if page:
            self.page = page
                
        # Инициализируем кнопку уведомлений
        if not hasattr(self, 'notification_button') or not self.notification_button:
            if self.notification_manager:
                unread_count = self.notification_manager.get_unread_count(
                    self.auth_manager.current_user['id']
                )
            else:
                unread_count = 0
            
            if unread_count > 0:
                self.notification_button = create_notification_button(unread_count, self._show_notifications, show_count=True)
            else:
                self.notification_button = create_notification_button(unread_count, self._show_notifications, show_count=False)
        
        role_text = {
            'admin': 'Панель администратора',
            'manager': 'Панель менеджера', 
            'master': 'Панель мастера',
            'client': 'Мои заявки'
        }
        
        self._build_tickets_column()
        
        action_buttons = []
        
        if self.auth_manager.is_client():
            action_buttons.append(
                create_create_ticket_button(
                    lambda _: self.on_create_ticket() if self.on_create_ticket else None
                )
            )
        
        action_buttons.extend([
            self.notification_button,
            create_logout_button(lambda _: self.on_logout())
        ])
        
        nav_bar = create_nav_bar(
            role_text.get(self.auth_manager.current_user['role'], 'Панель управления'),
            self.auth_manager.current_user['full_name'],
            action_buttons
        )
        
        if self.auth_manager.is_client():
            title = "Мои заявки"
        else:
            title = "Все заявки системы"
        
        # Сохраняем созданный контент
        self._current_content = ft.Column([
            nav_bar,
            ft.Divider(),
            ft.Row([
                ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
                self.search_field
            ]),
            self.tickets_column
        ])
        
        return self._current_content