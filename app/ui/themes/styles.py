import flet as ft
from app.ui.themes.colors import AppColors

def get_button_style(color: str = AppColors.PRIMARY, text_color: str = AppColors.WHITE):
    """Возвращает стиль для кнопки"""
    return ft.ButtonStyle(
        color=text_color,
        bgcolor=color,
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        overlay_color=ft.Colors.TRANSPARENT,
        elevation=2,
        animation_duration=300
    )

def get_card_style(elevation: int = 2, bgcolor: str = AppColors.CARD):
    """Возвращает стиль для карточки"""
    return {
        "elevation": elevation,
        "bgcolor": bgcolor,
        "border_radius": 8,
        "padding": 16
    }

def get_text_style(size: int = 14, weight: str = "normal", color: str = AppColors.BLACK):
    """Возвращает стиль для текста"""
    weight_map = {
        "normal": ft.FontWeight.NORMAL,
        "bold": ft.FontWeight.BOLD,
        "w100": ft.FontWeight.W100,
        "w200": ft.FontWeight.W200,
        "w300": ft.FontWeight.W300,
        "w400": ft.FontWeight.W400,
        "w500": ft.FontWeight.W500,
        "w600": ft.FontWeight.W600,
        "w700": ft.FontWeight.W700,
        "w800": ft.FontWeight.W800,
        "w900": ft.FontWeight.W900
    }
    
    return ft.TextStyle(
        size=size,
        weight=weight_map.get(weight, ft.FontWeight.NORMAL),
        color=color
    )

def get_status_badge_style(status: str):
    """Возвращает стиль для бейджа статуса"""
    status_colors = {
        'pending': AppColors.PENDING,
        'in_progress': AppColors.IN_PROGRESS,
        'waiting_parts': AppColors.WAITING_PARTS,
        'completed': AppColors.COMPLETED,
        'cancelled': AppColors.CANCELLED
    }
    
    return {
        "bgcolor": status_colors.get(status, AppColors.GREY),
        "color": AppColors.WHITE,
        "padding": ft.padding.symmetric(horizontal=8, vertical=4),
        "border_radius": 6
    }