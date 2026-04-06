from django.apps import AppConfig


class EwaybillConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ewaybill'
    verbose_name = 'E-Way Bill'

    def ready(self):
        pass