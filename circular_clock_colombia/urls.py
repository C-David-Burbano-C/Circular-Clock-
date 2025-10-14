"""
URL configuration for circular_clock_colombia project. / Configuración de URLs para proyecto circular_clock_colombia.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin interface / Interfaz de admin
    path('', include('clock.urls')),  # Include clock app URLs / Incluir URLs de la app clock
]
