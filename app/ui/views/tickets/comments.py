import flet as ft
from app.ui.themes.colors import AppColors

class TicketCommentsComponent:
    """Компонент для работы с комментариями к заявке"""
    
    def __init__(self, db, current_user, ticket_id):
        self.db = db
        self.current_user = current_user
        self.ticket_id = ticket_id
        self.comments = []
        self.comments_column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        
    def load_comments(self):
        """Загружает комментарии для заявки"""
        self.comments = self.db.get_comments_by_ticket(self.ticket_id)
        self._refresh_comments_display()
        
    def _refresh_comments_display(self):
        """Обновляет отображение комментариев"""
        self.comments_column.controls.clear()
        
        if not self.comments:
            self.comments_column.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon("CHAT_BUBBLE_OUTLINE", size=32, color=ft.Colors.GREY_400),
                        ft.Text("Комментариев пока нет", size=14, color=ft.Colors.GREY),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=20,
                    alignment=ft.alignment.center
                )
            )
        else:
            for comment in self.comments:
                comment_card = self._create_comment_card(comment)
                self.comments_column.controls.append(comment_card)
                
    def _create_comment_card(self, comment):
        """Создает карточку комментария"""
        # Определяем цвет фона в зависимости от роли пользователя
        if comment['user_role'] == 'master':
            bg_color = "#E3F2FD"  # Светло-голубой для мастеров
        elif comment['user_role'] == 'admin':
            bg_color = "#FFF3E0"  # Светло-оранжевый для админов
        else:
            bg_color = "#F5F5F5"  # Светло-серый для клиентов
            
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(comment['user_name'], weight=ft.FontWeight.BOLD, size=12),
                        ft.Container(
                            content=ft.Text(
                                comment['user_role'].upper(),
                                color=ft.Colors.WHITE,
                                size=8,
                                weight=ft.FontWeight.BOLD
                            ),
                            bgcolor=AppColors.PRIMARY if comment['user_role'] == 'master' else 
                                   AppColors.WARNING if comment['user_role'] == 'admin' else 
                                   AppColors.GREY,
                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                            border_radius=4
                        ),
                        ft.Text(
                            self._format_date(comment['created_date']),
                            size=10,
                            color=ft.Colors.GREY_600
                        )
                    ]),
                    ft.Text(comment['comment_text'], size=12),
                ], spacing=5),
                padding=10,
                bgcolor=bg_color,
                border=ft.border.all(1, AppColors.GREY_LIGHT),
                border_radius=8
            ),
            elevation=1
        )
        
    def _format_date(self, date_string):
        """Форматирует дату в читаемый вид"""
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime("%d.%m.%Y %H:%M")
        except:
            return date_string[:16].replace('T', ' ')
            
    def add_comment(self, comment_text):
        """Добавляет новый комментарий"""
        success = self.db.add_comment(
            self.ticket_id,
            self.current_user['id'],
            self.current_user['full_name'],
            comment_text
        )
        
        if success:
            self.load_comments()  # Перезагружаем комментарии
            return True
        return False
        
    def get_comments_count(self):
        """Возвращает количество комментариев"""
        return len(self.comments)
        
    def build(self):
        """Строит компонент комментариев"""
        self.load_comments()
        return self.comments_column