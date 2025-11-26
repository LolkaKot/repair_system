# app/ui/views/dashboard/admin.py

import flet as ft
import sqlite3
import threading
import time
from app.core.database import Database
from app.core.auth import AuthManager
from app.ui.components.navigation import create_nav_bar, create_notification_button, create_logout_button, create_stats_button
from app.ui.components.forms import create_search_field, create_status_filter, create_date_filter
from app.ui.components.ticket_cards import create_admin_ticket_card
from app.ui.views.shared.notifications import NotificationsView
from app.ui.themes.colors import AppColors

class AdminDashboardView:
    def __init__(self, auth_manager, db: Database, on_logout, on_edit_ticket=None, on_show_comments=None, on_show_stats=None, notification_service=None):
        self.auth_manager = auth_manager
        self.db = db
        self.on_logout = on_logout
        self.on_edit_ticket = on_edit_ticket
        self.on_show_comments = on_show_comments
        self.on_show_stats = on_show_stats
        self.notification_service = notification_service
        self.page = None
        
        # Добавляем инициализацию кнопки уведомлений
        self.notification_button = None
        
        self.tickets_column = ft.Column(scroll=ft.ScrollMode.AUTO)
        self.search_field = create_search_field(on_change=self._on_search, width=400)
        self.status_filter = create_status_filter(on_change=self._on_filter_change, width=200)
        self.date_filter = create_date_filter(on_change=self._on_date_filter_change, width=200)

        # Сразу загружаем данные
        self._tickets_data = self._get_tickets_data()
    
    def _show_stats(self):
        """Показывает статистику"""
        if hasattr(self, 'on_show_stats') and self.on_show_stats:
            self.on_show_stats()
        else:
            print("Would show stats")

    def _on_date_filter_change(self, e):
        """Обработчик изменения фильтра по дате"""
        self._load_tickets(self.status_filter.value, self.search_field.value)

    def _show_comments(self, ticket: dict):
        """Показывает комментарии к заявке"""
        if hasattr(self, 'on_show_comments') and self.on_show_comments:
            self.on_show_comments(ticket['id'])
        else:
            print(f"Would show comments for ticket {ticket['id']}")

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
    
    def _get_tickets_data(self):
        """Получаем данные о заявках без обновления UI"""
        return self.db.get_all_tickets()
    
    def _load_tickets(self, status_filter="all", search_query=None):
        """Загружает заявки в колонку"""
        self.tickets_column.controls.clear()
        
        tickets = self._tickets_data
        
        # Фильтрация по статусу
        if status_filter != "all":
            tickets = [t for t in tickets if t['status'] == status_filter]
        
        # Фильтрация по поисковому запросу
        if search_query:
            search_query = search_query.lower()
            tickets = [t for t in tickets if 
                    search_query in t['title'].lower() or 
                    search_query in t['ticket_number'].lower() or
                    search_query in (t['client_name'] or '').lower()]
        
        # Сортировка по дате
        if hasattr(self, 'date_filter') and self.date_filter.value == "oldest":
            tickets.sort(key=lambda x: x['created_date'])
        else:
            # По умолчанию - сначала новые
            tickets.sort(key=lambda x: x['created_date'], reverse=True)
        
        if not tickets:
            self.tickets_column.controls.append(
                ft.Text("Заявки не найдены", size=16, color="grey")
            )
        else:
            for ticket in tickets:
                card = create_admin_ticket_card(
                    ticket,
                    on_assign=self._show_assign_dialog,
                    on_status_change=self._update_ticket_status,
                    on_edit=self._edit_ticket,
                    on_comments=self._show_comments,
                    on_delete=self._delete_ticket
                )
                self.tickets_column.controls.append(card)
        
        # Обновляем только если уже добавлено на страницу
        if self.page:
            self.tickets_column.update()
    
    def _on_search(self, e):
        """Обработчик поиска"""
        self._load_tickets(self.status_filter.value, e.control.value)
    
    def _on_filter_change(self, e):
        """Обработчик изменения фильтра"""
        self._load_tickets(e.control.value, self.search_field.value)
    
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
        """Редактирует заявку (для администратора)"""
        if hasattr(self, 'on_edit_ticket') and self.on_edit_ticket:
            self.on_edit_ticket(ticket['id'])
        else:
            print(f"Would edit ticket {ticket['id']}")

    def _show_assign_dialog(self, ticket: dict):
        """Показывает диалог назначения мастера через BottomSheet"""
        print(f"Открытие диалога назначения мастера для заявки {ticket['id']}")
        
        masters = self.db.get_masters()
        print(f"Available masters: {masters}")
        
        if not masters:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Нет доступных мастеров"),
                bgcolor=AppColors.ERROR
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        # Создаем выпадающий список с мастерами
        master_dropdown = ft.Dropdown(
            label="Выберите мастера",
            options=[ft.dropdown.Option(str(m['id']), m['full_name']) for m in masters],
            width=400
        )

        def assign_ticket(e):
            if not master_dropdown.value:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Выберите мастера"),
                    bgcolor=AppColors.WARNING
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
                
            master_id = int(master_dropdown.value)
            print(f"Назначение мастера {master_id} для заявки {ticket['id']}")
            
            if hasattr(self, 'notification_service') and self.notification_service:
                success = self.db.assign_ticket_to_master_with_notification(
                    ticket['id'], master_id, self.notification_service
                )
            else:
                success = self.db.assign_ticket_to_master(ticket['id'], master_id)
            
            print(f"Результат назначения: {success}")
            
            if success:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Мастер успешно назначен!"),
                    bgcolor=AppColors.SUCCESS
                )
                self.page.snack_bar.open = True
                self._tickets_data = self._get_tickets_data()
                self._load_tickets(self.status_filter.value, self.search_field.value)
            else:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Ошибка при назначении мастера"),
                    bgcolor=AppColors.ERROR
                )
                self.page.snack_bar.open = True
            
            # Закрываем BottomSheet
            bottom_sheet.open = False
            self.page.update()
        
        def close_bottom_sheet(e):
            bottom_sheet.open = False
            self.page.update()
        
        # Создаем BottomSheet
        bottom_sheet = ft.BottomSheet(
            ft.Container(
                ft.Column([
                    ft.Row([
                        ft.Text("Назначение мастера", size=18, weight=ft.FontWeight.BOLD, expand=True),
                        ft.TextButton("Закрыть", on_click=close_bottom_sheet),
                    ]),
                    ft.Divider(),
                    ft.Text(f"Заявка: #{ticket['ticket_number']} - {ticket['title']}"),
                    ft.Text(f"Клиент: {ticket['client_name']}"),
                    ft.Text(f"Текущий мастер: {ticket.get('master_name', 'Не назначен')}"),
                    ft.Divider(),
                    ft.Text("Выберите мастера:", weight=ft.FontWeight.BOLD),
                    master_dropdown,
                    ft.Container(height=20),
                    ft.Row([
                        ft.ElevatedButton("Отмена", on_click=close_bottom_sheet),
                        ft.ElevatedButton("Назначить", on_click=assign_ticket),
                    ], alignment=ft.MainAxisAlignment.END)
                ]),
                padding=20,
            ),
            open=True,
            dismissible=True
        )
        
        self.page.overlay.append(bottom_sheet)
        self.page.update()
        print("BottomSheet для назначения мастера открыт")
    
    def _update_ticket_status(self, ticket: dict, new_status: str):
        """Обновляет статус заявки с проверкой"""
        if not self.page:
            return
        
        print(f"Обновление статуса заявки {ticket['id']} на {new_status}")
        
        # Проверяем есть ли назначенный мастер для определенных статусов
        if new_status in ['in_progress', 'completed'] and not ticket.get('assigned_master_id'):
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("❌ Сначала назначьте мастера для этой заявки!"),
                bgcolor="#F44336"
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        # Если проверка пройдена - обновляем статус
        if hasattr(self, 'notification_service') and self.notification_service:
            success = self.db.update_ticket_status_with_notification(
                ticket['id'], new_status, self.notification_service
            )
        else:
            success = self.db.update_ticket_status(ticket['id'], new_status)
        
        if success:
            status_text = self._get_status_text(new_status)
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"✅ Статус заявки изменен на: {status_text}"),
                bgcolor="#4CAF50"
            )
            self.page.snack_bar.open = True
            
            self._tickets_data = self._get_tickets_data()
            self._load_tickets(self.status_filter.value, self.search_field.value)
        else:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("❌ Ошибка при изменении статуса"),
                bgcolor="#F44336"
            )
            self.page.snack_bar.open = True
        
        self.page.update()
    
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
            self._load_tickets(self.status_filter.value, self.search_field.value)
        else:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Ошибка: Не удалось удалить заявку"),
                bgcolor=AppColors.ERROR
            )
            self.page.snack_bar.open = True
        
        self.page.update()
    
    def _get_status_text(self, status: str) -> str:
        """Возвращает читаемый текст статуса"""
        status_texts = {
            'pending': 'ОЖИДАЕТ',
            'in_progress': 'В РАБОТЕ',
            'completed': 'ЗАВЕРШЕНА',
            'cancelled': 'ОТМЕНЕНА'
        }
        return status_texts.get(status, status.upper())

    def _on_refresh(self, e):
        """Обработчик обновления"""
        self._tickets_data = self._get_tickets_data()
        self._load_tickets(self.status_filter.value, self.search_field.value)
    
    def build(self, page: ft.Page):
        self.page = page
        
        # Инициализируем кнопку уведомлений
        self._update_notification_button()
        
        # Создаем кнопки для навигационной панели (без кнопки "Обновить")
        nav_buttons = [
            create_stats_button(lambda _: self._show_stats()),
            self.notification_button,
            create_logout_button(lambda _: self.on_logout())
        ]
        
        # Навигационная панель
        nav_bar = create_nav_bar(
            "Панель администратора",
            self.auth_manager.current_user['full_name'],
            nav_buttons
        )
        
        # Сохраняем ссылку на навигационную панель для будущих обновлений
        self._current_nav_bar = nav_bar
        
        # Фильтры
        filters_row = ft.Row([
            ft.Text("Управление заявками", size=20, weight=ft.FontWeight.BOLD),
            self.status_filter,
            self.date_filter,
            self.search_field
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Легенда статусов
        status_legend = ft.Row([
            ft.Text("Статусы:", size=14, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Text("ОЖИДАЕТ", size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                bgcolor=AppColors.PENDING,
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                border_radius=6
            ),
            ft.Container(
                content=ft.Text("В РАБОТЕ", size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                bgcolor=AppColors.IN_PROGRESS,
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                border_radius=6
            ),
            ft.Container(
                content=ft.Text("ЗАВЕРШЕНА", size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                bgcolor=AppColors.COMPLETED,
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                border_radius=6
            ),
            ft.Container(
                content=ft.Text("ОТМЕНЕНА", size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                bgcolor=AppColors.CANCELLED,
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                border_radius=6
            ),
        ], spacing=10)
        
        # Создаем основной контейнер
        main_content = ft.Column([
            nav_bar,
            ft.Divider(),
            filters_row,
            status_legend,
            ft.Text(f"Всего заявок: {len(self._tickets_data)}", size=14, color=AppColors.GREY),
            self.tickets_column
        ])
        
        # Загружаем заявки после создания интерфейса
        def delayed_load():
            time.sleep(0.1)
            self._load_tickets()
        
        threading.Thread(target=delayed_load, daemon=True).start()
        
        return main_content