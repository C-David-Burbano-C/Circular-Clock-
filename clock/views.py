from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
import json
from datetime import datetime, time

from .models import Alarm, ClockConfiguration, AlarmLog, ClockStatistics
from .circular_lists import get_colombia_time
from .reloj_core import CircularClock


# Global clock instance / Instancia global del reloj
clock_instance = CircularClock()


def index(request):
    """Main clock view with modern Spanish interface / Vista principal del reloj con interfaz moderna en español"""
    config, created = ClockConfiguration.objects.get_or_create(
        defaults={
            'name': 'Configuración Principal',
            'time_format': '12h',
            'show_seconds': True,
            'show_analog_clock': True,
            'show_digital_clock': True,
            'auto_sync': True,
        }
    )
    
    # Get active alarms / Obtener alarmas activas
    active_alarms = Alarm.objects.filter(
        is_active=True
    ).order_by('hour', 'minute')
    
    # Get current Colombia time / Obtener hora actual de Colombia
    current_time = get_colombia_time()
    
    # Use clock_instance.get_current_time() to fetch the engine state / Usar clock_instance.get_current_time() para obtener el estado del motor
    engine_time = clock_instance.get_current_time()

    context = {
        'config': config,
        'active_alarms': active_alarms,
        'alarms': active_alarms,
        'current_time': current_time,
        'clock_data': {
            'hours': engine_time.get('hour', 0),
            'minutes': engine_time.get('minute', 0),
            'seconds': engine_time.get('second', 0),
            'weekday': engine_time.get('day', ''),
            'period': engine_time.get('am_pm', '')
        }
    }
    
    return render(request, 'clock/index.html', context)


def get_current_time(request):
    """API endpoint for real-time clock updates / Endpoint de API para actualizaciones de reloj en tiempo real"""
    # Ensure the engine syncs with Colombia time on each request so we return live values / Asegurar que el motor se sincronice con la hora de Colombia en cada solicitud para devolver valores en vivo
    try:
        clock_instance.sync_colombia_time()
    except Exception:
        # If sync fails, fall back to engine current time / Si la sincronización falla, volver al tiempo actual del motor
        pass
    # Keep engine format in sync with stored configuration / Mantener el formato del motor sincronizado con la configuración almacenada
    try:
        config, _ = ClockConfiguration.objects.get_or_create()
        clock_instance.change_format(config.time_format == '24h')
    except Exception:
        pass
    current_display = clock_instance.get_current_time()

    # Provide both 12h and 24h representations / Proporcionar representaciones tanto en 12h como en 24h
    response = {
        'success': True,
        'time': current_display,
        'time_12h': {
            'hour': current_display.get('hour'),
            'minute': current_display.get('minute'),
            'second': current_display.get('second'),
            'period': current_display.get('am_pm')
        },
        'time_24h': {
            'hour': current_display.get('hour_24h'),
            'minute': current_display.get('minute'),
            'second': current_display.get('second')
        },
        'colombia_time': get_colombia_time(),
        'timestamp': timezone.now().timestamp()
    }

    return JsonResponse(response)


def toggle_format(request):
    """Toggle between 12h and 24h format / Alternar entre formato 12h y 24h"""
    if request.method == 'POST':
        config, created = ClockConfiguration.objects.get_or_create()
        
        config.time_format = '24h' if config.time_format == '12h' else '12h'
        config.save()
        # Also update the global clock engine format so responses reflect the new format immediately / También actualizar el formato del motor de reloj global para que las respuestas reflejen el nuevo formato inmediatamente
        try:
            clock_instance.change_format(config.time_format == '24h')
            # sync engine to ensure hour values are updated / sincronizar motor para asegurar que los valores de hora se actualicen
            clock_instance.sync_colombia_time()
        except Exception:
            pass
        
        return JsonResponse({
            'success': True,
            'new_format': config.time_format
        })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


def create_alarm(request):
    """Create a new alarm / Crear una nueva alarma"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
            
            hour = int(data.get('hour', 1))
            minute = int(data.get('minute', 0))
            period = data.get('period', 'AM')
            day_of_week = data.get('day_of_week')
            alarm_date = data.get('alarm_date')  # Expect ISO date string YYYY-MM-DD for specific calendar date / Esperar cadena de fecha ISO YYYY-MM-DD para fecha específica del calendario
            label = data.get('label', 'Alarma')
            # Normalize empty label to default / Normalizar etiqueta vacía a predeterminada
            if not label or (isinstance(label, str) and label.strip() == ''):
                label = 'Alarma'
            
            # Validate time / Validar tiempo
            if not (1 <= hour <= 12) or not (0 <= minute <= 59):
                return JsonResponse({
                    'success': False,
                    'error': 'Hora inválida (1-12) o minuto inválido (0-59)'
                })
            
            # Validate period / Validar período
            if period not in ['AM', 'PM']:
                return JsonResponse({
                    'success': False,
                    'error': 'Período inválido (AM/PM)'
                })
            
            # Validate day of week / Validar día de la semana
            if day_of_week is not None:
                day_of_week = int(day_of_week)
                if not (0 <= day_of_week <= 6):
                    return JsonResponse({
                        'success': False,
                        'error': 'Día de la semana inválido'
                    })

            # Validate alarm_date (optional) / Validar alarm_date (opcional)
            if alarm_date:
                try:
                    from datetime import date
                    alarm_date_parsed = datetime.fromisoformat(alarm_date).date()
                    # Reject past dates / Rechazar fechas pasadas
                    today = timezone.localdate()
                    if alarm_date_parsed < today:
                        return JsonResponse({'success': False, 'error': 'No se permiten fechas pasadas para alarmas (alarm_date)'} )
                except Exception:
                    return JsonResponse({'success': False, 'error': 'Formato de fecha inválido (YYYY-MM-DD)'} )
            else:
                alarm_date_parsed = None
            
            alarm = Alarm.objects.create(
                title=label,
                hour=hour,
                minute=minute,
                period=period,
                day_of_week=day_of_week,
                alarm_date=alarm_date_parsed,
                second=0,
                is_active=True
            )
            
            day_names = {
                0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves',
                4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
            }
            day_text = day_names.get(day_of_week, 'Todos los días') if day_of_week is not None else 'Todos los días'
            
            messages.success(request, f'Alarma creada para las {hour:02d}:{minute:02d} {period} - {day_text}')
            
            return JsonResponse({
                'success': True,
                'alarm_id': alarm.id,
                'message': 'Alarma creada exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al crear alarma: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


def delete_alarm(request, alarm_id):
    """Delete an alarm / Eliminar una alarma"""
    if request.method == 'POST':
        try:
            alarm = get_object_or_404(Alarm, id=alarm_id)
            
            alarm.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Alarma eliminada exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al eliminar alarma: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


def toggle_alarm(request, alarm_id):
    """Toggle alarm active/inactive state / Alternar estado activo/inactivo de la alarma"""
    if request.method == 'POST':
        try:
            alarm = get_object_or_404(Alarm, id=alarm_id)
            
            alarm.is_active = not alarm.is_active
            alarm.save()
            
            status = 'activada' if alarm.is_active else 'desactivada'
            
            return JsonResponse({
                'success': True,
                'is_active': alarm.is_active,
                'message': f'Alarma {status} exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al cambiar alarma: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


def update_configuration(request):
    """Update clock configuration / Actualizar configuración del reloj"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
            
            config, created = ClockConfiguration.objects.get_or_create()
            
            # Update configuration fields / Actualizar campos de configuración
            if 'show_seconds' in data:
                config.show_seconds = bool(data['show_seconds'])
            if 'show_analog_clock' in data:
                config.show_analog_clock = bool(data['show_analog_clock'])
            if 'show_digital_clock' in data:
                config.show_digital_clock = bool(data['show_digital_clock'])
            if 'auto_sync' in data:
                config.auto_sync = bool(data['auto_sync'])
            
            config.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Configuración actualizada exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al actualizar configuración: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


def statistics(request):
    """Display clock usage statistics / Mostrar estadísticas de uso del reloj"""
    # Ensure we create/retrieve statistics for today's date (ClockStatistics.date is NOT NULL and unique) / Asegurar que creemos/recuperemos estadísticas para la fecha de hoy (ClockStatistics.date NO es NULL y es único)
    today = timezone.localdate()
    stats, created = ClockStatistics.objects.get_or_create(date=today)
    
    # Get recent alarm logs / Obtener registros recientes de alarmas
    recent_logs = AlarmLog.objects.all().order_by('-triggered_at')[:10]
    
    # Basic counts / Conteos básicos
    total_alarms_count = Alarm.objects.count()
    total_active_alarms = Alarm.objects.filter(is_active=True).count()

    # Determine which weekday (0=Monday) to match day_of_week / Determinar qué día de la semana (0=Lunes) para coincidir con day_of_week
    weekday = today.weekday()

    # Active alarms scheduled for today: either a specific alarm_date == today, / Alarmas activas programadas para hoy: ya sea una alarm_date específica == hoy,
    # or a day_of_week matching today's weekday, or alarms with no restriction (treated as daily) / o un day_of_week que coincida con el día de la semana de hoy, o alarmas sin restricción (tratadas como diarias)
    active_alarms_today_qs = Alarm.objects.filter(is_active=True).filter(
        Q(alarm_date=today) | Q(day_of_week=weekday) | (Q(day_of_week__isnull=True) & Q(alarm_date__isnull=True))
    )
    active_alarms_today = active_alarms_today_qs.count()

    context = {
        'stats': stats,
        'recent_logs': recent_logs,
        'total_alarms': total_alarms_count,
        'total_active_alarms': total_active_alarms,
        'active_alarms_today': active_alarms_today,
        # keep a legacy key in case templates reference it / mantener una clave heredada en caso de que las plantillas la referencien
        'active_alarms': total_active_alarms,
    }

    # Prepare last 7 days data for charting using AlarmLog counts per day / Preparar datos de los últimos 7 días para gráficos usando conteos de AlarmLog por día
    labels = []
    alarms_counts = []
    for i in range(6, -1, -1):
        d = today - timezone.timedelta(days=i)
        labels.append(d.strftime('%d %b'))
        # Count AlarmLog entries whose triggered_at date equals d / Contar entradas de AlarmLog cuya fecha triggered_at sea igual a d
        count = AlarmLog.objects.filter(triggered_at__date=d).count()
        alarms_counts.append(count)

    context['chart_payload'] = {
        'labels': labels,
        'data': alarms_counts,
    }
    # JSON string for safe injection in templates (use escapejs in template) / Cadena JSON para inyección segura en plantillas (usar escapejs en plantilla)
    context['chart_json'] = json.dumps(context['chart_payload'])

    # Additional summary metrics / Métricas de resumen adicionales
    context['total_triggers'] = AlarmLog.objects.count()
    context['unique_alarms_triggered'] = AlarmLog.objects.values('alarm').distinct().count()

    # Alarms triggered today / Alarmas disparadas hoy
    triggered_today = AlarmLog.objects.filter(triggered_at__date=today).count()
    context['triggered_today'] = triggered_today
    
    return render(request, 'clock/statistics.html', context)


def check_alarms(request):
    """Check if any alarms should be triggered / Verificar si alguna alarma debe dispararse"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            hour = int(data.get('hour'))
            minute = int(data.get('minute'))
            period = data.get('period')
            day = int(data.get('day'))
            
            # Find matching alarms: match by time + either specific date, matching weekday, or no day restriction / Encontrar alarmas coincidentes: coincidir por tiempo + ya sea fecha específica, día de la semana coincidente, o sin restricción de día
            matching_alarms = Alarm.objects.filter(
                hour=hour,
                minute=minute,
                period=period,
                is_active=True
            ).filter(
                Q(alarm_date__isnull=False, alarm_date=timezone.localdate()) |
                Q(day_of_week=day) |
                Q(day_of_week__isnull=True, alarm_date__isnull=True)
            )
            
            alarm_triggered = matching_alarms.exists()
            
            # Log triggered alarms using the AlarmLog model fields and mark alarm as triggered / Registrar alarmas disparadas usando los campos del modelo AlarmLog y marcar alarma como disparada
            for alarm in matching_alarms:
                # Skip if alarm is temporarily silenced / Omitir si la alarma está silenciada temporalmente
                if alarm.silenced_until and alarm.silenced_until > timezone.now():
                    continue
                # Increment alarm counters and last_triggered / Incrementar contadores de alarma y last_triggered
                try:
                    alarm.trigger()
                except Exception:
                    pass

                AlarmLog.objects.create(
                    alarm=alarm,
                    alarm_title=alarm.title,
                    status='triggered',
                    user_action='auto-trigger'
                )
            
            return JsonResponse({
                'alarm_triggered': alarm_triggered,
                'triggered_alarms': [
                    {
                        'id': alarm.id,
                        'title': alarm.title,
                        'time': f"{alarm.hour:02d}:{alarm.minute:02d} {alarm.period}"
                    }
                    for alarm in matching_alarms
                ]
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


def dismiss_alarm(request):
    """User dismisses an alarm: silence it for the configured snooze or permanently depending on params / Usuario descarta una alarma: silenciarla por el snooze configurado o permanentemente dependiendo de los parámetros"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            alarm_id = int(data.get('alarm_id'))
            duration_minutes = int(data.get('silence_minutes', 0))
            alarm = get_object_or_404(Alarm, id=alarm_id)

            if duration_minutes > 0:
                alarm.silenced_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
            else:
                # If duration 0, mark as inactive / Si duración 0, marcar como inactiva
                alarm.is_active = False
            alarm.save()

            # Record the dismissal in logs / Registrar el descarte en logs
            AlarmLog.objects.create(
                alarm=alarm,
                alarm_title=alarm.title,
                status='dismissed',
                user_action='user-dismiss'
            )

            return JsonResponse({'success': True, 'message': 'Alarma descartada/silenciada'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


def list_alarms(request):
    """Return a JSON list of alarms for modal display / Devolver una lista JSON de alarmas para visualización modal"""
    if request.method == 'GET':
        alarms = Alarm.objects.all().order_by('hour', 'minute')
        data = []
        for a in alarms:
            time_text = f"{a.hour:02d}:{a.minute:02d} {a.period}"
            data.append({
                'id': a.id,
                'time': time_text,
                'label': a.title,
                'is_active': a.is_active,
            })
        return JsonResponse({'success': True, 'alarms': data})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


def sync_time(request):
    """Manually sync with Colombia time / Sincronizar manualmente con la hora de Colombia"""
    if request.method == 'POST':
        try:
            clock_instance.sync_colombia_time()
            
            return JsonResponse({
                'success': True,
                'message': 'Hora sincronizada con Colombia',
                'current_time': clock_instance.get_current_display()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al sincronizar: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})
