from django.apps import AppConfig


class GstLedgerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gst_ledger'
    label = 'gst_ledger'
    verbose_name = 'GST Ledger'

    def ready(self):
        pass