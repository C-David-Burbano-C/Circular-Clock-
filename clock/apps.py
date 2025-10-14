"""
Django App Configuration for Circular Clock / Configuración de App de Django para Reloj Circular
App configuration and initialization / Configuración de app e inicialización


"""

from django.apps import AppConfig


class ClockConfig(AppConfig):
    """Clock app configuration / Configuración de la app del reloj"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clock'  # App name / Nombre de la app
