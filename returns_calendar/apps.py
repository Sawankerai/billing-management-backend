from django.apps import AppConfig


class ReturnsCalendarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'returns_calendar'
    verbose_name = 'Returns Calendar'

    def ready(self):
        pass