

from django.urls import path
from . import views

app_name = 'clock'  # App namespace / Espacio de nombres de la app

urlpatterns = [
    # Main clock view / Vista principal del reloj
    path('', views.index, name='index'),
    
    # API endpoints / Endpoints de API
    path('api/current-time/', views.get_current_time, name='api_current_time'),
    path('api/toggle-format/', views.toggle_format, name='api_toggle_format'),
    path('api/sync-time/', views.sync_time, name='api_sync_time'),
    
    # Alarm management / Gestión de alarmas
    path('api/alarms/create/', views.create_alarm, name='api_create_alarm'),
    path('api/alarms/<int:alarm_id>/delete/', views.delete_alarm, name='api_delete_alarm'),
    path('api/alarms/<int:alarm_id>/toggle/', views.toggle_alarm, name='api_toggle_alarm'),
    path('api/alarms/list/', views.list_alarms, name='api_list_alarms'),
    path('api/check-alarms/', views.check_alarms, name='api_check_alarms'),
    path('api/alarms/dismiss/', views.dismiss_alarm, name='api_dismiss_alarm'),
    
    # Configuration / Configuración
    path('api/configuration/update/', views.update_configuration, name='api_update_configuration'),
    
    # Statistics / Estadísticas
    path('statistics/', views.statistics, name='statistics'),
]