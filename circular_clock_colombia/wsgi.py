

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'circular_clock_colombia.settings')  # Set Django settings module / Establecer módulo de configuraciones de Django

application = get_wsgi_application()  # WSGI application instance / Instancia de aplicación WSGI
