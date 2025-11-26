import flet as ft
from app.core.mysql_notifications import MySQLNotificationManager as NotificationManager
from app.ui.themes.colors import AppColors

class NotificationsView:
    def __init__(self, notification_manager: NotificationManager, current_user_id: int, on_ticket_click=None, on_notifications_update=None):
        self.notification_manager = notification_manager
        self.current_user_id = current_user_id
        self.on_ticket_click = on_ticket_click
        self.on_notifications_update = on_notifications_update
        self.page = None
        self.on_close_callback = None
        
    def build_popup_content(self, page: ft.Page, on_close):
        """Строит содержимое для всплывающего окна"""
        self.page = page
        self.on_close_callback = on_close
        
        # Обновляем данные уведомлений
        self._refresh_notifications_data()
        
        return self._create_notifications_ui()
    
    def _refresh_notifications_data(self):
        """Обновляет данные уведомлений"""
        self.notifications = self.notification_manager.get_user_notifications(self.current_user_id)
        self.unread_count = self.notification_manager.get_unread_count(self.current_user_id)
        print(f"Обновлены данные уведомлений: {self.unread_count} непрочитанных")
    
    def _create_notifications_ui(self):
        """Создает интерфейс уведомлений"""
        # Создаем колонку для уведомлений
        self.notifications_column = ft.Column(
            scroll=ft.ScrollMode.AUTO, 
            expand=True,
            spacing=10
        )
        
        # Заполняем колонку, но НЕ обновляем ее (она еще не добавлена на страницу)
        self._fill_notifications_column()
        
        # Заголовок с счетчиком
        self.unread_count_text = ft.Text(f"Непрочитанные: {self.unread_count}", weight=ft.FontWeight.BOLD)
        
        # Кнопки действий
        action_buttons = ft.Row([
            ft.TextButton(
                "Все",
                on_click=lambda e: self._show_all_notifications()
            ),
            ft.TextButton(
                "Непрочитанные", 
                on_click=lambda e: self._show_unread_notifications()
            ),
            ft.TextButton(
                "Прочитать все",
                on_click=lambda e: self._mark_all_read()
            )
        ], spacing=5)
        
        # Основной контент
        content = ft.Column([
            ft.Row([self.unread_count_text]),
            action_buttons,
            ft.Divider(),
            ft.Container(
                content=self.notifications_column,
                expand=True
            )
        ], expand=True)
        
        return content
    
    def _fill_notifications_column(self, notifications_filter=None):
        """Заполняет колонку уведомлениями с учетом фильтра"""
        self.notifications_column.controls.clear()
        
        if notifications_filter:
            notifications_to_show = notifications_filter
        else:
            notifications_to_show = self.notifications
        
        if not notifications_to_show:
            self.notifications_column.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon("NOTIFICATIONS_NONE", size=48, color=ft.Colors.GREY),
                        ft.Text("Нет уведомлений", size=16, color=ft.Colors.GREY)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
                    padding=40,
                    alignment=ft.alignment.center
                )
            )
        else:
            for notification in notifications_to_show:
                card = self._create_notification_card(notification)
                self.notifications_column.controls.append(card)
    
    def _create_notification_card(self, notification):
        """Создает карточку уведомления"""
        bg_color = AppColors.GREY_LIGHT if notification['is_read'] else AppColors.WHITE
        border_color = AppColors.GREY_LIGHT if notification['is_read'] else AppColors.PRIMARY
        
        card_content = [
            ft.Row([
                ft.Text(notification['title'], weight=ft.FontWeight.BOLD, size=14, expand=True),
                ft.Container(
                    content=ft.Text(
                        "НОВОЕ" if not notification['is_read'] else "ПРОЧИТАНО",
                        size=10,
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.BOLD
                    ),
                    bgcolor=AppColors.PRIMARY if not notification['is_read'] else AppColors.GREY,
                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    border_radius=6
                )
            ]),
            ft.Text(notification['message'], size=12),
            ft.Row([
                ft.Text(
                    f"Заявка: #{notification['ticket_number']}" if notification['ticket_number'] else "Системное",
                    size=10,
                    color=AppColors.GREY
                ),
                ft.Text(
                    notification['created_date'][:16].replace('T', ' '),
                    size=10,
                    color=AppColors.GREY
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ]
        
        # Кнопки действий для непрочитанных уведомлений
        if not notification['is_read']:
            actions_row = ft.Row([], alignment=ft.MainAxisAlignment.END)
            
            # Кнопка "Прочитать" для одного уведомления
            mark_read_btn = ft.TextButton(
                "Прочитать",
                on_click=lambda e, nid=notification['id']: self._mark_as_read(nid)
            )
            actions_row.controls.append(mark_read_btn)
            
            # Кнопка перехода к заявке
            if notification['related_ticket_id'] and self.on_ticket_click:
                go_to_ticket_btn = ft.TextButton(
                    "К заявке",
                    on_click=lambda e, tid=notification['related_ticket_id']: self._go_to_ticket(tid),
                    style=ft.ButtonStyle(color=AppColors.SUCCESS)
                )
                actions_row.controls.append(go_to_ticket_btn)
            
            card_content.append(actions_row)
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column(card_content),
                padding=12,
                bgcolor=bg_color,
                border=ft.border.all(1, border_color),
                border_radius=8
            ),
            elevation=1
        )
    
    def _show_all_notifications(self):
        """Показывает все уведомления"""
        self._fill_notifications_column(self.notifications)
        # Теперь можно обновлять, так как колонка уже на странице
        if self.page:
            self.notifications_column.update()
    
    def _show_unread_notifications(self):
        """Показывает только непрочитанные уведомления"""
        unread_notifications = [n for n in self.notifications if not n['is_read']]
        self._fill_notifications_column(unread_notifications)
        if self.page:
            self.notifications_column.update()
    
    def _update_ui_after_change(self):
        """Полностью обновляет интерфейс после изменений"""
        # Обновляем данные
        self._refresh_notifications_data()
        
        print(f"Обновление UI после изменений: {self.unread_count} непрочитанных")
        
        # Обновляем счетчик в заголовке
        if hasattr(self, 'unread_count_text'):
            self.unread_count_text.value = f"Непрочитанные: {self.unread_count}"
            if self.page:
                self.unread_count_text.update()
        
        # Обновляем колонку уведомлений
        self._fill_notifications_column()
        if self.page:
            self.notifications_column.update()
        
        # ВАЖНО: Обновляем счетчик в главном интерфейсе
        if self.on_notifications_update:
            print(f"Вызываем колбэк обновления с unread_count: {self.unread_count}")
            self.on_notifications_update(self.unread_count)
    
    def _mark_as_read(self, notification_id: int):
        """Помечает уведомление как прочитанное и обновляет интерфейс"""
        print(f"Помечаем уведомление {notification_id} как прочитанное")
        
        success = self.notification_manager.mark_as_read(notification_id)
        if success:
            print("Уведомление успешно помечено как прочитанное")
            
            # Полностью обновляем интерфейс
            self._update_ui_after_change()
            
            # Показываем сообщение
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Уведомление прочитано"),
                    bgcolor=AppColors.SUCCESS
                )
                self.page.snack_bar.open = True
                self.page.update()
        else:
            print("Ошибка при отметке уведомления как прочитанного")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Ошибка при отметке уведомления"),
                    bgcolor=AppColors.ERROR
                )
                self.page.snack_bar.open = True
                self.page.update()

    def _mark_all_read(self):
        """Помечает все уведомления как прочитанные"""
        print("Помечаем все уведомления как прочитанные")
        
        success = self.notification_manager.mark_all_as_read(self.current_user_id)
        if success:
            print("Все уведомления помечены как прочитанные")
            
            # Полностью обновляем интерфейс
            self._update_ui_after_change()
            
            # Показываем сообщение
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Все уведомления прочитаны"),
                    bgcolor=AppColors.SUCCESS
                )
                self.page.snack_bar.open = True
                self.page.update()
        else:
            print("Ошибка при отметке всех уведомлений")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Ошибка при отметке уведомлений"),
                    bgcolor=AppColors.ERROR
                )
                self.page.snack_bar.open = True
                self.page.update()
    
    def _go_to_ticket(self, ticket_id: int):
        """Переходит к заявке"""
        if self.on_ticket_click:
            self.on_ticket_click(ticket_id)
        if self.on_close_callback:
            self.on_close_callback(None)