from django.apps import AppConfig


class GstReportConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gst_report'
    verbose_name = 'GST Report'

    def ready(self):
        pass