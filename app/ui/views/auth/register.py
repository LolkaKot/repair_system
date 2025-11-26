import flet as ft
import threading
import time
from app.core.auth import AuthManager
from app.ui.components.forms import create_form_field, create_button
from app.ui.components.base import BaseComponent

class RegisterView(BaseComponent):
    def __init__(self, auth_manager: AuthManager, on_register_success, on_show_login):
        super().__init__()
        self.auth_manager = auth_manager
        self.on_register_success = on_register_success
        self.on_show_login = on_show_login
        
        self.username_field = create_form_field("Имя пользователя", width=300)
        self.password_field = create_form_field("Пароль", width=300, password=True)
        self.full_name_field = create_form_field("ФИО", width=300)
        self.email_field = create_form_field("Email", width=300)
        self.phone_field = create_form_field("Телефон", width=300)
        self.error_text = ft.Text("", color="red")
        self.success_text = ft.Text("", color="green")
        
        self.register_button = create_button("Зарегистрироваться", self._register_click, width=300)
        
        self.back_button = ft.TextButton(
            "Назад к входу",
            on_click=lambda _: on_show_login()
        )
    
    def _register_click(self, e):
        # Валидация
        if not all([
            self.username_field.value,
            self.password_field.value,
            self.full_name_field.value,
            self.email_field.value,
            self.phone_field.value
        ]):
            self.error_text.value = "Заполните все поля"
            self.error_text.update()
            return
        
        if len(self.password_field.value) < 6:
            self.error_text.value = "Пароль должен содержать минимум 6 символов"
            self.error_text.update()
            return
        
        # Регистрация
        if self.auth_manager.register(
            self.username_field.value,
            self.password_field.value,
            self.full_name_field.value,
            self.email_field.value,
            self.phone_field.value
        ):
            self.success_text.value = "Регистрация успешна! Теперь войдите в систему."
            self.success_text.update()
            # Автоматически переходим к входу через 2 секунды
            def delayed_login():
                time.sleep(2)
                self.on_show_login()
            threading.Thread(target=delayed_login, daemon=True).start()
        else:
            self.error_text.value = "Пользователь с таким именем уже существует"
            self.error_text.update()
    
    def build(self):
        return ft.Container(
            content=ft.Column([
                ft.Text("Регистрация клиента", 
                       size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Создайте учетную запись", size=16),
                self.username_field,
                self.password_field,
                self.full_name_field,
                self.email_field,
                self.phone_field,
                self.register_button,
                self.error_text,
                self.success_text,
                self.back_button
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            alignment=ft.alignment.center,
            expand=True
        )