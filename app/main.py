import flet as ft
from app.core.database_factory import create_database
from app.core.auth import AuthManager
from app.core.mysql_notifications import MySQLNotificationManager  # Добавьте этот импорт
from app.core.notifications import NotificationService
from app.ui.views.auth.login import LoginView
from app.ui.views.auth.register import RegisterView
from app.ui.views.dashboard.admin import AdminDashboardView
from app.ui.views.dashboard.master import MasterDashboardView
from app.ui.views.dashboard.client import ClientDashboardView
from app.ui.views.tickets.create import TicketCreateView
from app.ui.views.tickets.edit import TicketEditView
from app.ui.views.tickets.view import TicketCommentsView
from app.ui.views.shared.stats import StatsView
import app.config as config

class RepairSystemApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        
        # Инициализация компонентов
        self.db = create_database()
        self.auth_manager = AuthManager(self.db)
        
        # Используем MySQL NotificationManager
        self.notification_manager = MySQLNotificationManager(self.db)
        self.notification_service = NotificationService(self.db, self.notification_manager)
        
        # Показываем экран входа при запуске
        self.show_login()
    
    def setup_page(self):
        self.page.title = config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.window.width = config.APP_WIDTH
        self.page.window.height = config.APP_HEIGHT
        self.page.window.min_width = config.APP_MIN_WIDTH
        self.page.window.min_height = config.APP_MIN_HEIGHT
    
    def show_login(self):
        """Показать экран входа"""
        self.page.clean()
        login_view = LoginView(
            auth_manager=self.auth_manager,
            on_login_success=self.show_role_based_dashboard,
            on_show_register=self.show_register
        )
        self.page.add(login_view.build())
        self.page.update()
    
    def show_register(self):
        """Показать экран регистрации"""
        self.page.clean()
        register_view = RegisterView(
            auth_manager=self.auth_manager,
            on_register_success=self.show_role_based_dashboard,
            on_show_login=self.show_login
        )
        self.page.add(register_view.build())
        self.page.update()
    
    def show_role_based_dashboard(self):
        """Показать интерфейс в зависимости от роли пользователя"""
        self.page.clean()
        
        if self.auth_manager.is_admin():
            self.show_admin_dashboard()
        elif self.auth_manager.is_master():
            self.show_master_dashboard()
        else:
            self.show_client_dashboard()
    
    def show_admin_dashboard(self):
        """Показать панель администратора"""
        admin_view = AdminDashboardView(
            auth_manager=self.auth_manager,
            db=self.db,
            on_logout=self.show_login,
            on_edit_ticket=self.show_edit_ticket,
            on_show_comments=self.show_ticket_comments,
            on_show_stats=self.show_stats,
            notification_service=self.notification_service
        )
        self.page.add(admin_view.build(self.page))
        self.page.update()

    def show_master_dashboard(self):
        """Показать панель мастера"""
        master_view = MasterDashboardView(
            auth_manager=self.auth_manager,
            db=self.db,
            on_logout=self.show_login,
            on_edit_ticket=self.show_edit_ticket,
            on_show_comments=self.show_ticket_comments,
            notification_service=self.notification_service
        )
        self.page.add(master_view.build(self.page))
        self.page.update()
    
    def show_client_dashboard(self):
        """Показать панель клиента"""
        dashboard_view = ClientDashboardView(
            auth_manager=self.auth_manager,
            db=self.db,
            on_logout=self.show_login,
            on_create_ticket=self.show_create_ticket,
            on_edit_ticket=self.show_edit_ticket,
            notification_manager=self.notification_manager,
            notification_service=self.notification_service
        )
        dashboard_content = dashboard_view.build(self.page)
        self.page.add(dashboard_content)
        self.page.update()
    
    def show_create_ticket(self):
        """Показать форму создания заявки"""
        self.page.clean()
        ticket_view = TicketCreateView(
            db=self.db,
            current_user=self.auth_manager.current_user,
            on_back=self.show_role_based_dashboard,
            on_ticket_created=lambda: self.show_success_message("Заявка успешно создана!"),
            notification_service=self.notification_service
        )
        self.page.add(ticket_view.build())
        self.page.update()
    
    def show_ticket_comments(self, ticket_id: int):
        """Показывает комментарии к заявке"""
        self.page.clean()
        comments_view = TicketCommentsView(
            db=self.db,
            current_user=self.auth_manager.current_user,
            ticket_id=ticket_id,
            on_back=self.show_role_based_dashboard
        )
        content = comments_view.build()
        
        # Сохраняем ссылку на страницу для обновлений
        comments_view.page = self.page
        
        self.page.add(content)
        self.page.update()
        print(f"Открыты комментарии для заявки {ticket_id}")

    def show_stats(self):
        """Показывает статистику"""
        self.page.clean()
        stats_view = StatsView(
            db=self.db,
            on_back=self.show_role_based_dashboard
        )
        content = stats_view.build()
        
        # Сохраняем ссылку на страницу
        stats_view.page = self.page
        
        self.page.add(content)
        self.page.update()

    def show_edit_ticket(self, ticket_id: int):
        """Показать форму редактирования заявки"""
        self.page.clean()
        edit_view = TicketEditView(
            db=self.db,
            current_user=self.auth_manager.current_user,
            ticket_id=ticket_id,
            on_back=self.show_role_based_dashboard,
            on_ticket_updated=lambda: self.show_success_message("Заявка успешно обновлена!")
        )
        self.page.add(edit_view.build())
        self.page.update()
    
    def show_success_message(self, message: str):
        """Показать сообщение об успехе и вернуться на дашборд"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor="#4CAF50"
        )
        self.page.snack_bar.open = True
        self.show_role_based_dashboard()
        
def main(page: ft.Page):
    app = RepairSystemApp(page)