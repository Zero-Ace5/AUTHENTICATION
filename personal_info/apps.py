from django.apps import AppConfig


class PersonalInfoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "personal_info"

    def ready(self):
        import personal_info.signals
