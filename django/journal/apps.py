from django.apps import AppConfig

from material.frontend.apps import ModuleMixin


class JournalConfig(ModuleMixin, AppConfig):
    name = 'journal'
    icon = '<i class="material-icons">flight_takeoff</i>'
