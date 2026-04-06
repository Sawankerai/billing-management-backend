from django.apps import AppConfig


class EInvoiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'e_invoice'
    label = 'e_invoice'
    verbose_name = 'E-Invoice'

    def ready(self):
        pass