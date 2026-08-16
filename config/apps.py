import os
from django.apps import AppConfig


class ConfigConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "config"

    def ready(self):
        if os.environ.get("RUN_MAIN") != "true":
            return

        # Only apply this behavior during local development.
        from django.conf import settings

        if not settings.DEBUG:
            return

        try:
            from django.contrib.sessions.models import Session
            Session.objects.all().delete()
        except Exception:
            pass
