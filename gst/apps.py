from django.apps import AppConfig


class GstConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name    = 'gst'
    label   = 'gst'
    verbose_name = 'GST'

    def ready(self):
        """
        Called once the app registry is fully populated.
        Import signals here if you add them later.
        e.g. import gst_setup.signals
        """
        pass