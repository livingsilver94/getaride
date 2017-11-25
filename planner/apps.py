from django.apps import AppConfig


class PlannerConfig(AppConfig):
    name = 'planner'

    def ready(self):
        import planner.signals