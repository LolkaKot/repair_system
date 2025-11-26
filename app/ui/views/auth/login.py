import flet as ft
from app.core.auth import AuthManager
from app.ui.components.forms import create_form_field, create_button
from app.ui.components.base import BaseComponent

class LoginView(BaseComponent):
    def __init__(self, auth_manager: AuthManager, on_login_success, on_show_register):
        super().__init__()
        self.auth_manager = auth_manager
        self.on_login_success = on_login_success
        self.on_show_register = on_show_register
        
        self.username_field = create_form_field("Имя пользователя", width=300)
        self.password_field = create_form_field("Пароль", width=300, password=True)
        self.error_text = ft.Text("", color="red")
        
        self.login_button = create_button("Войти", self._login_click, width=300)
        
        self.register_button = ft.TextButton(
            "Зарегистрироваться как клиент",
            on_click=lambda _: on_show_register()
        )
    
    def _login_click(self, e):
        if not self.username_field.value or not self.password_field.value:
            self.error_text.value = "Заполните все поля"
            self.error_text.update()
            return
        
        if self.auth_manager.login(self.username_field.value, self.password_field.value):
            self.on_login_success()
        else:
            self.error_text.value = "Неверное имя пользователя или пароль"
            self.error_text.update()
    
    def build(self):
        return ft.Container(
            content=ft.Column([
                ft.Text("Система учета заявок на ремонт", 
                       size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Войдите в систему", size=16),
                self.username_field,
                self.password_field,
                self.login_button,
                self.error_text,
                self.register_button
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            alignment=ft.alignment.center,
            expand=True
        )