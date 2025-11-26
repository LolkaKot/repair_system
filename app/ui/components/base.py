import flet as ft

class BaseComponent:
    """Базовый класс для всех UI компонентов"""
    
    def __init__(self):
        self.page = None
    
    def set_page(self, page: ft.Page):
        """Устанавливает ссылку на страницу"""
        self.page = page
    
    def build(self) -> ft.Control:
        """Метод для построения компонента (должен быть переопределен)"""
        raise NotImplementedError("Метод build должен быть переопределен в дочернем классе")
    
    def update(self):
        """Обновляет компонент на странице"""
        if self.page:
            self.page.update()
    
    def show_message(self, message: str, message_type: str = "info"):
        """Показывает сообщение пользователю"""
        if not self.page:
            return
            
        colors = {
            "info": "#2196F3",
            "success": "#4CAF50", 
            "warning": "#FF9800",
            "error": "#F44336"
        }
        
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=colors.get(message_type, "#2196F3")
        )
        self.page.snack_bar.open = True
        self.page.update()