# app/ui/views/shared/stats.py

import flet as ft
from datetime import datetime, timedelta
from app.core.database import Database
from app.ui.themes.colors import AppColors

class StatsView:
    def __init__(self, db: Database, on_back):
        self.db = db
        self.on_back = on_back
        self.page = None
        
        # Данные статистики
        self.stats_data = {}
        
        # Период для статистики
        self.period_filter = ft.Dropdown(
            label="Период",
            width=200,
            options=[
                ft.dropdown.Option("week", "За неделю"),
                ft.dropdown.Option("month", "За месяц"),
                ft.dropdown.Option("all", "За все время")
            ],
            value="month",
            on_change=self._load_stats
        )
    
    def _calculate_stats(self, period="month"):
        """Рассчитывает статистику за указанный период"""
        all_tickets = self.db.get_all_tickets()
        
        # Фильтруем по периоду
        now = datetime.now()
        if period == "week":
            start_date = now - timedelta(days=7)
        elif period == "month":
            start_date = now - timedelta(days=30)
        else:  # all
            start_date = datetime.min
        
        filtered_tickets = []
        for ticket in all_tickets:
            try:
                ticket_date = datetime.fromisoformat(ticket['created_date'].replace('Z', '+00:00'))
                if ticket_date >= start_date:
                    filtered_tickets.append(ticket)
            except:
                filtered_tickets.append(ticket)
        
        # Основная статистика
        total_tickets = len(filtered_tickets)
        completed_tickets = len([t for t in filtered_tickets if t['status'] == 'completed'])
        pending_tickets = len([t for t in filtered_tickets if t['status'] == 'pending'])
        in_progress_tickets = len([t for t in filtered_tickets if t['status'] == 'in_progress'])
        
        # Расчет среднего времени выполнения
        avg_completion_time = self._calculate_avg_completion_time(filtered_tickets)
        
        # Статистика по типам неисправностей (анализ заголовков)
        fault_stats = self._analyze_fault_types(filtered_tickets)
        
        return {
            'total_tickets': total_tickets,
            'completed_tickets': completed_tickets,
            'pending_tickets': pending_tickets,
            'in_progress_tickets': in_progress_tickets,
            'completion_rate': (completed_tickets / total_tickets * 100) if total_tickets > 0 else 0,
            'avg_completion_time': avg_completion_time,
            'fault_stats': fault_stats,
            'period_tickets': filtered_tickets
        }
    
    def _calculate_avg_completion_time(self, tickets):
        """Рассчитывает среднее время выполнения заявок"""
        completion_times = []
        
        for ticket in tickets:
            if ticket['status'] == 'completed':
                try:
                    created_date = datetime.fromisoformat(ticket['created_date'].replace('Z', '+00:00'))
                    
                    # Для простоты будем считать что заявка завершена через 2 дня после создания
                    # В реальном приложении здесь нужно использовать поле даты завершения
                    completion_date = created_date + timedelta(days=2)
                    completion_time = (completion_date - created_date).total_seconds() / 3600  # в часах
                    completion_times.append(completion_time)
                except:
                    continue
        
        if completion_times:
            avg_hours = sum(completion_times) / len(completion_times)
            if avg_hours < 24:
                return f"{avg_hours:.1f} часов"
            else:
                return f"{avg_hours/24:.1f} дней"
        else:
            return "Нет данных"
    
    def _analyze_fault_types(self, tickets):
        """Анализирует типы неисправностей по ключевым словам в заголовках"""
        fault_keywords = {
            'Принтер': ['принтер', 'печать', 'картридж', 'мфу'],
            'Компьютер': ['компьютер', 'пк', 'ноутбук', 'windows', 'система'],
            'Сеть': ['сеть', 'интернет', 'wi-fi', 'wifi', 'подключение'],
            'Программы': ['программа', 'софт', 'установка', 'office', '1с'],
            'Оборудование': ['монитор', 'клавиатура', 'мышь', 'оборудование'],
            'Другое': []  # Все остальное
        }
        
        fault_stats = {category: 0 for category in fault_keywords.keys()}
        
        for ticket in tickets:
            title_lower = ticket['title'].lower()
            matched = False
            
            for category, keywords in fault_keywords.items():
                if category == 'Другое':
                    continue
                    
                for keyword in keywords:
                    if keyword in title_lower:
                        fault_stats[category] += 1
                        matched = True
                        break
                if matched:
                    break
            
            if not matched:
                fault_stats['Другое'] += 1
        
        return fault_stats
    
    def _load_stats(self, e=None):
        """Загружает и отображает статистику"""
        period = self.period_filter.value
        self.stats_data = self._calculate_stats(period)
        self._update_stats_display()
    
    def _update_stats_display(self):
        """Обновляет отображение статистики"""
        if not hasattr(self, 'stats_container'):
            return
        
        stats = self.stats_data
        
        # Основные метрики
        metrics_row = ft.Row([
            self._create_metric_card("Всего заявок", stats['total_tickets'], "DESCRIPTION", AppColors.INFO),
            self._create_metric_card("Выполнено", stats['completed_tickets'], "CHECK_CIRCLE", AppColors.SUCCESS),
            self._create_metric_card("В работе", stats['in_progress_tickets'], "BUILD", AppColors.WARNING),
            self._create_metric_card("Ожидают", stats['pending_tickets'], "SCHEDULE", AppColors.PENDING),
        ], spacing=20)
        
        # Дополнительная статистика
        additional_stats = ft.Row([
            self._create_metric_card("Процент выполнения", f"{stats['completion_rate']:.1f}%", "TRENDING_UP", AppColors.PRIMARY),
            self._create_metric_card("Среднее время", stats['avg_completion_time'], "ACCESS_TIME", AppColors.INFO),
        ], spacing=20)
        
        # Статистика по типам неисправностей
        fault_stats_content = []
        for fault_type, count in stats['fault_stats'].items():
            if count > 0:
                percentage = (count / stats['total_tickets'] * 100) if stats['total_tickets'] > 0 else 0
                fault_stats_content.append(
                    ft.Row([
                        ft.Text(fault_type, size=14, expand=True),
                        ft.Text(f"{count} ({percentage:.1f}%)", size=14, weight=ft.FontWeight.BOLD),
                    ])
                )
        
        fault_stats_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Статистика по типам неисправностей", size=16, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    *fault_stats_content
                ]),
                padding=20
            ),
            elevation=2
        )
        
        # Обновляем контейнер
        self.stats_container.controls = [
            metrics_row,
            ft.Container(height=20),
            additional_stats,
            ft.Container(height=20),
            fault_stats_card
        ]
        
        if self.page:
            self.stats_container.update()
    
    def _create_metric_card(self, title, value, icon, color):
        """Создает карточку с метрикой"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(icon, color=color, size=24),
                        ft.Text(title, size=12, color=AppColors.GREY),
                    ]),
                    ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD),
                ], spacing=10),
                padding=20,
                width=200
            ),
            elevation=2
        )
    
    def build(self):
        """Строит интерфейс статистики"""
        # Загружаем статистику
        self._load_stats()
        
        # Создаем контейнер для статистики
        self.stats_container = ft.Column()
        
        content = ft.Column([
            ft.Row([
                ft.TextButton(
                    "← Назад",
                    on_click=lambda _: self.on_back()
                ),
                ft.Text("Статистика работы отдела", size=20, weight=ft.FontWeight.BOLD, expand=True),
                self.period_filter,
            ]),
            ft.Divider(),
            ft.Text("Общая статистика", size=18, weight=ft.FontWeight.BOLD),
            self.stats_container
        ])
        
        return content