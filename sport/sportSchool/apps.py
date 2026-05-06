from django.apps import AppConfig


class SportschoolConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sportSchool'

    def ready(self):
        import sportSchool.signals  # Регистрируем сигнал

    

