from django.apps import AppConfig
from django.db.models.signals import post_save


class AnalysisConfig(AppConfig):
    name = 'analysis'

    def ready(self):
        import analysis.servers.singaltask