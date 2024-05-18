from django.apps import AppConfig

class HeliosAuthConfig(AppConfig):
    name = 'helios_auth'
    verbose_name = "Helios Authentication"

    def ready(self):
        from . import signals  # Import your signals module
        signals.post_request_signal.connect(signals.post_view_function)
