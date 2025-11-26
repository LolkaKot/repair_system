import flet as ft
from app.core.database import Database
from app.ui.components.forms import create_form_field, create_button
from app.ui.components.base import BaseComponent
from app.ui.themes.colors import AppColors

class TicketCommentsView(BaseComponent):
    def __init__(self, db: Database, current_user: dict, ticket_id: int, on_back):
        super().__init__()
        self.db = db
        self.current_user = current_user
        self.ticket_id = ticket_id
        self.on_back = on_back
        
        # Загружаем данные заявки и комментарии
        self.ticket = self.db.get_ticket_by_id(ticket_id)
        self.comments = self.db.get_comments_by_ticket(ticket_id)
        
        # Поле для ввода комментария
        self.comment_field = create_form_field(
            "Добавить комментарий",
            width=400,
            multiline=True,
            min_lines=2,
            max_lines=4,
            expand=True
        )
        
        # Колонка для отображения комментариев
        self.comments_column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def _format_date(self, date_string: str) -> str:
        """Форматирует дату в читаемый вид"""
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime("%d.%m.%Y %H:%M")
        except:
            return date_string[:16].replace('T', ' ')

    def _load_comments(self):
        """Загружает комментарии в колонку"""
        # Полностью очищаем колонку
        self.comments_column.controls.clear()
        
        if not self.comments:
            self.comments_column.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon("CHAT_BUBBLE_OUTLINE", size=48, color=ft.Colors.GREY_400),
                        ft.Text("Комментариев пока нет", size=16, color=ft.Colors.GREY),
                        ft.Text("Будьте первым, кто оставит комментарий", size=12, color=ft.Colors.GREY),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=40,
                    alignment=ft.alignment.center
                )
            )
        else:
            for comment in self.comments:
                comment_card = self._create_comment_card(comment)
                self.comments_column.controls.append(comment_card)
        
        # Принудительно обновляем колонку
        if hasattr(self, 'page') and self.page:
            self.comments_column.update()

    def _scroll_to_bottom(self):
        """Прокручивает к последнему комментарию (вызывается после добавления на страницу)"""
        if self.comments and hasattr(self, 'page') and self.page:
            # Небольшая задержка чтобы элемент успел отрендериться
            import threading
            import time
            def delayed_scroll():
                time.sleep(0.1)
                self.comments_column.scroll_to(offset=-1, duration=300)
                if hasattr(self, 'page'):
                    self.page.update()
            threading.Thread(target=delayed_scroll, daemon=True).start()

    def _create_comment_card(self, comment: dict):
        """Создает карточку комментария"""
        # Определяем цвет фона в зависимости от роли пользователя
        if comment['user_role'] == 'master':
            bg_color = "#E3F2FD"  # Светло-голубой для мастеров
            text_color = ft.Colors.BLACK
        elif comment['user_role'] == 'admin':
            bg_color = "#FFF3E0"  # Светло-оранжевый для админов
            text_color = ft.Colors.BLACK
        else:
            bg_color = "#F5F5F5"  # Светло-серый для клиентов
            text_color = ft.Colors.BLACK
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(comment['user_name'], weight=ft.FontWeight.BOLD, size=12, color=text_color),
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
                            color=ft.Colors.GREY_700
                        )
                    ]),
                    ft.Text(comment['comment_text'], size=12, color=text_color),
                ], spacing=5),
                padding=10,
                bgcolor=bg_color,
                border=ft.border.all(1, AppColors.GREY_LIGHT),
                border_radius=8,
                margin=ft.margin.only(bottom=10)
            ),
            elevation=1
        )

    def _add_comment(self, e):
        """Добавляет новый комментарий"""
        print(f"Добавление комментария для заявки {self.ticket_id}")
        
        if not self.comment_field.value.strip():
            print("Пустой комментарий - пропускаем")
            return
        
        # Сохраняем текст комментария перед очисткой
        comment_text = self.comment_field.value.strip()
        print(f"Текст комментария: {comment_text}")
        
        # Очищаем поле ввода СРАЗУ
        self.comment_field.value = ""
        print("Поле ввода очищено")
        
        # Принудительно обновляем поле ввода
        if hasattr(self, 'page'):
            self.comment_field.update()
            print("Поле ввода обновлено")
        
        success = self.db.add_comment(
            self.ticket_id,
            self.current_user['id'],
            self.current_user['full_name'],
            comment_text
        )
        
        print(f"Результат добавления в БД: {success}")
        
        if success:
            # Получаем обновленный список комментариев
            self.comments = self.db.get_comments_by_ticket(self.ticket_id)
            print(f"Получено комментариев: {len(self.comments)}")
            
            # Полностью перезагружаем комментарии
            self._load_comments()
            print("Комментарии перезагружены")
            
            # Прокручиваем к новому комментарию
            self._scroll_to_bottom()
            print("Прокрутка выполнена")
            
            # Показываем сообщение об успехе
            if hasattr(self, 'page'):
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Комментарий добавлен!"),
                    bgcolor=AppColors.SUCCESS
                )
                self.page.snack_bar.open = True
                self.page.update()
                print("Сообщение показано")
        else:
            # Показываем ошибку
            if hasattr(self, 'page'):
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Ошибка при добавлении комментария"),
                    bgcolor=AppColors.ERROR
                )
                self.page.snack_bar.open = True
                self.page.update()
                print("Ошибка показана")

    def build(self):
        """Строит интерфейс комментариев"""
        if not self.ticket:
            return ft.Column([
                ft.TextButton("← Назад", on_click=lambda _: self.on_back()),
                ft.Text("Заявка не найдена", size=20, color=AppColors.ERROR)
            ])
        
        # Загружаем комментарии
        self._load_comments()
        
        content = ft.Column([
            ft.Row([
                ft.TextButton(
                    "← Назад",
                    on_click=lambda _: self.on_back()
                ),
                ft.Text(f"Комментарии к заявке #{self.ticket['ticket_number']}", 
                    size=20, weight=ft.FontWeight.BOLD, expand=True),
            ]),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        # Информация о заявке
                        ft.Container(
                            content=ft.Column([
                                ft.Text(f"Заявка: {self.ticket['title']}", weight=ft.FontWeight.BOLD),
                                ft.Text(f"Описание: {self.ticket['description']}"),
                                ft.Text(f"Статус: {self.ticket['status']}"),
                                ft.Text(f"Клиент: {self.ticket['client_name']}"),
                            ], spacing=5),
                            padding=10,
                            bgcolor=AppColors.GREY_LIGHT,
                            border_radius=8
                        ),
                        ft.Divider(),
                        
                        # Секция добавления комментария
                        ft.Text("Добавить комментарий:", weight=ft.FontWeight.BOLD),
                        ft.Row([
                            self.comment_field,
                            create_button(
                                "Отправить",
                                self._add_comment,
                                color=AppColors.PRIMARY,
                                width=100
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        
                        ft.Divider(),
                        
                        # Список комментариев
                        ft.Row([
                            ft.Text("Комментарии:", weight=ft.FontWeight.BOLD, expand=True),
                            ft.Text(f"Всего: {len(self.comments)}", size=12, color=AppColors.GREY),
                        ]),
                        ft.Container(
                            content=self.comments_column,
                            height=400
                        )
                    ]),
                    padding=20
                )
            )
        ])
        
        # Прокручиваем к последнему комментарию после создания интерфейса
        def delayed_scroll_init():
            import time
            time.sleep(0.2)
            self._scroll_to_bottom()
        
        import threading
        threading.Thread(target=delayed_scroll_init, daemon=True).start()
        
        return content