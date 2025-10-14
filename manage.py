#!/usr/bin/env python
"""Django's command-line utility for administrative tasks. / Utilidad de línea de comandos de Django para tareas administrativas."""
import os
import sys


def main():
    """Run administrative tasks. / Ejecutar tareas administrativas."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'circular_clock_colombia.settings')  # Set Django settings module / Establecer módulo de configuraciones de Django
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "  # No se pudo importar Django. ¿Estás seguro de que está instalado y
            "available on your PYTHONPATH environment variable? Did you "  # disponible en tu variable de entorno PYTHONPATH? ¿Olvidaste
            "forget to activate a virtual environment?"  # activar un entorno virtual?
        ) from exc
    execute_from_command_line(sys.argv)  # Execute command line / Ejecutar línea de comandos


if __name__ == '__main__':
    main()  # Run main function if script is executed directly / Ejecutar función main si el script se ejecuta directamente
