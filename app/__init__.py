from .core.database import Database
from .core.auth import AuthManager
from .core.notifications import NotificationService
from .ui.views.auth.login import LoginView
from .ui.views.auth.register import RegisterView
from .ui.views.dashboard.client import ClientDashboardView
from .ui.views.dashboard.admin import AdminDashboardView
from .ui.views.dashboard.master import MasterDashboardView
from .ui.views.tickets.create import TicketCreateView
from .ui.views.tickets.edit import TicketEditView
from .ui.views.tickets.view import TicketCommentsView
from .ui.views.shared.notifications import NotificationsView
from .ui.views.shared.stats import StatsView
from .ui.themes.colors import AppColors

__all__ = [
    'Database',
    'AuthManager', 
    'NotificationManager',
    'NotificationService',
    'LoginView',
    'RegisterView',
    'ClientDashboardView',
    'AdminDashboardView', 
    'MasterDashboardView',
    'TicketCreateView',
    'TicketEditView',
    'TicketCommentsView',
    'NotificationsView',
    'StatsView',
    'AppColors'
]