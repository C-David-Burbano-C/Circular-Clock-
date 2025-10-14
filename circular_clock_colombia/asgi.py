"""
ASGI config for circular_clock_colombia project. / Configuración ASGI para proyecto circular_clock_colombia.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'circular_clock_colombia.settings')  # Set Django settings module / Establecer módulo de configuraciones de Django

application = get_asgi_application()  # ASGI application instance / Instancia de aplicación ASGI
