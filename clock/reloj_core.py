"""
Modern Circular Clock Core Engine / Motor Central del Reloj Circular Moderno
Colombia Time Zone Support with Real-time Updates / Soporte de Zona Horaria de Colombia con Actualizaciones en Tiempo Real



"""

import threading
import time
import datetime
import pytz
from .circular_lists import HoursList, MinutesList, SecondsList, DaysList


class CircularClock:
    """Main clock engine using circular double linked lists / Motor principal del reloj usando listas doblemente enlazadas circulares"""
    
    def __init__(self):
        # Initialize circular lists / Inicializar listas circulares
        self.hours_24 = HoursList(format_24h=True)
        self.hours_12 = HoursList(format_24h=False)
        self.minutes = MinutesList()
        self.seconds = SecondsList()
        self.days = DaysList()
        
        # Configuration / Configuración
        self.format_24h = False  # Default to 12h format / Predeterminado a formato 12h
        self.running = False
        self.clock_thread = None
        self.observers = []  # For GUI notifications / Para notificaciones de GUI
        
        # Colombia timezone / Zona horaria de Colombia
        self.colombia_tz = pytz.timezone('America/Bogota')
        
        # Sync with current time / Sincronizar con hora actual
        self.sync_colombia_time()
        
    def add_observer(self, callback):
        """Add observer for change notifications / Agregar observador para notificaciones de cambios"""
        self.observers.append(callback)
        
    def notify_observers(self):
        """Notify all observers about changes / Notificar a todos los observadores sobre cambios"""
        for callback in self.observers:
            try:
                callback(self.get_current_time())
            except Exception as e:
                print(f"Error notifying observer: {e}")
                
    def sync_colombia_time(self):
        """Sync clock with current Colombia time / Sincronizar reloj con hora actual de Colombia"""
        now = datetime.datetime.now(self.colombia_tz)
        
        # Set values in circular lists / Establecer valores en listas circulares
        self.hours_24.set_value(now.hour)
        self.hours_12.set_value(12 if now.hour == 0 else 
                               (now.hour if now.hour <= 12 else now.hour - 12))
        self.minutes.set_value(now.minute)
        self.seconds.set_value(now.second)
        self.days.set_day_number(now.weekday())
        
    def change_format(self, format_24h=True):
        """Switch between 12h and 24h format / Cambiar entre formato 12h y 24h"""
        self.format_24h = format_24h
        
    def get_current_time(self):
        """Get current clock time / Obtener hora actual del reloj"""
        if self.format_24h:
            hour = self.hours_24.get_value()
            am_pm = ""
        else:
            hour = self.hours_12.get_value()
            am_pm = "AM" if self.hours_24.get_value() < 12 else "PM"
            
        return {
            'hour': hour,
            'minute': self.minutes.get_value(),
            'second': self.seconds.get_value(),
            'day': self.days.get_spanish_day(),  # Spanish for UI / Español para interfaz
            'day_english': self.days.get_value(),  # English for internal use / Inglés para uso interno
            'am_pm': am_pm,
            'format_24h': self.format_24h,
            'hour_24h': self.hours_24.get_value()
        }
        
    def get_current_display(self):
        """Get current display data for Django templates / Obtener datos de visualización actuales para plantillas Django"""
        if self.format_24h:
            hour = self.hours_24.get_value()
            period = ""
        else:
            hour = self.hours_12.get_value()
            period = "AM" if self.hours_24.get_value() < 12 else "PM"
            
        return {
            'hours': hour,
            'minutes': self.minutes.get_value(),
            'seconds': self.seconds.get_value(),
            'weekday': self.days.get_spanish_day(),
            'period': period
        }
        
    def format_time(self):
        """Format time as string / Formatear tiempo como cadena"""
        time_data = self.get_current_time()
        
        if self.format_24h:
            return f"{time_data['hour']:02d}:{time_data['minute']:02d}:{time_data['second']:02d}"
        else:
            return f"{time_data['hour']:02d}:{time_data['minute']:02d}:{time_data['second']:02d} {time_data['am_pm']}"
            
    def format_date(self):
        """Format date as string in Spanish for UI / Formatear fecha como cadena en español para interfaz"""
        time_data = self.get_current_time()
        now = datetime.datetime.now(self.colombia_tz)
        
        # Get Spanish month name / Obtener nombre del mes en español
        from circular_lists import get_spanish_month_name
        month_spanish = get_spanish_month_name(now.month)
        
        return f"{time_data['day']}, {now.day} de {month_spanish} de {now.year}"
        
    def advance_second(self):
        """Advance one second and handle cascade / Avanzar un segundo y manejar cascada"""
        self.seconds.advance()
        
        # If we completed a minute (back to 0) / Si completamos un minuto (volver a 0)
        if self.seconds.get_value() == 0:
            self.advance_minute()
            
    def advance_minute(self):
        """Advance one minute and handle cascade / Avanzar un minuto y manejar cascada"""
        self.minutes.advance()
        
        # If we completed an hour (back to 0) / Si completamos una hora (volver a 0)
        if self.minutes.get_value() == 0:
            self.advance_hour()
            
    def advance_hour(self):
        """Advance one hour and handle cascade / Avanzar una hora y manejar cascada"""
        self.hours_24.advance()
        
        # Update 12h format hour / Actualizar hora en formato 12h
        hour_24 = self.hours_24.get_value()
        if hour_24 == 0:
            self.hours_12.set_value(12)
        elif hour_24 <= 12:
            self.hours_12.set_value(hour_24)
        else:
            self.hours_12.set_value(hour_24 - 12)
            
        # If we completed a day (back to 0) / Si completamos un día (volver a 0)
        if hour_24 == 0:
            self.days.advance()
            
    def set_time(self, hour, minute, second):
        """Set time manually / Establecer tiempo manualmente"""
        self.hours_24.set_value(hour)
        self.minutes.set_value(minute)
        self.seconds.set_value(second)
        
        # Update 12h format hour / Actualizar hora en formato 12h
        if hour == 0:
            self.hours_12.set_value(12)
        elif hour <= 12:
            self.hours_12.set_value(hour)
        else:
            self.hours_12.set_value(hour - 12)
            
    def start_clock(self):
        """Start real-time clock / Iniciar reloj en tiempo real"""
        if not self.running:
            self.running = True
            self.clock_thread = threading.Thread(target=self._run_clock, daemon=True)
            self.clock_thread.start()
            
    def stop_clock(self):
        """Stop clock / Detener reloj"""
        self.running = False
        if self.clock_thread:
            self.clock_thread.join(timeout=1)
            
    def _run_clock(self):
        """Run clock in separate thread / Ejecutar reloj en hilo separado"""
        while self.running:
            time.sleep(1)  # Wait 1 second / Esperar 1 segundo
            if self.running:  # Check again in case it was stopped / Verificar nuevamente en caso de que se haya detenido
                self.advance_second()
                self.notify_observers()
                
    def get_seconds_angle(self):
        """Get angle for seconds hand (0-360 degrees) / Obtener ángulo para la manecilla de segundos (0-360 grados)"""
        return (self.seconds.get_value() * 6) % 360
        
    def get_minutes_angle(self):
        """Get angle for minutes hand (0-360 degrees) / Obtener ángulo para la manecilla de minutos (0-360 grados)"""
        minutes = self.minutes.get_value()
        seconds = self.seconds.get_value()
        return ((minutes * 6) + (seconds * 0.1)) % 360
        
    def get_hours_angle(self):
        """Get angle for hours hand (0-360 degrees) / Obtener ángulo para la manecilla de horas (0-360 grados)"""
        hour = self.hours_12.get_value()
        minutes = self.minutes.get_value()
        return ((hour * 30) + (minutes * 0.5)) % 360
        
    def is_running(self):
        """Check if clock is running / Verificar si el reloj está ejecutándose"""
        return self.running
        
    def __del__(self):
        """Destructor - stop clock / Destructor - detener reloj"""
        self.stop_clock()


class AlarmManager:
    """Alarm manager for the clock / Administrador de alarmas para el reloj"""
    
    def __init__(self, clock):
        self.clock = clock
        self.alarms = []
        self.check_thread = None
        self.checking = False
        
    def add_alarm(self, hour, minute, second=0, description="Alarm", active=True, repeat_daily=False):
        """Add new alarm / Agregar nueva alarma"""
        alarm = {
            'id': len(self.alarms) + 1,
            'hour': hour,
            'minute': minute,
            'second': second,
            'description': description,
            'active': active,
            'repeat_daily': repeat_daily,
            'triggered_today': False,
            'callback': None
        }
        self.alarms.append(alarm)
        return alarm['id']
        
    def remove_alarm(self, alarm_id):
        """Remove alarm by ID / Remover alarma por ID"""
        self.alarms = [a for a in self.alarms if a['id'] != alarm_id]
        
    def toggle_alarm(self, alarm_id, active=True):
        """Activate/deactivate alarm / Activar/desactivar alarma"""
        for alarm in self.alarms:
            if alarm['id'] == alarm_id:
                alarm['active'] = active
                return True
        return False
        
    def set_alarm_callback(self, alarm_id, callback):
        """Set callback for when alarm triggers / Establecer callback para cuando la alarma se active"""
        for alarm in self.alarms:
            if alarm['id'] == alarm_id:
                alarm['callback'] = callback
                return True
        return False
        
    def get_alarms(self):
        """Get list of all alarms / Obtener lista de todas las alarmas"""
        return self.alarms.copy()
        
    def start_checking(self):
        """Start alarm checking / Iniciar verificación de alarmas"""
        if not self.checking:
            self.checking = True
            self.check_thread = threading.Thread(target=self._check_alarms, daemon=True)
            self.check_thread.start()
            
    def stop_checking(self):
        """Stop alarm checking / Detener verificación de alarmas"""
        self.checking = False
        if self.check_thread:
            self.check_thread.join(timeout=1)
            
    def _check_alarms(self):
        """Check alarms in separate thread / Verificar alarmas en hilo separado"""
        while self.checking:
            current_time = self.clock.get_current_time()
            
            for alarm in self.alarms:
                if (alarm['active'] and 
                    alarm['hour'] == current_time['hour_24h'] and
                    alarm['minute'] == current_time['minute'] and
                    alarm['second'] == current_time['second']):
                    
                    # Check if already triggered today (for non-repeating alarms) / Verificar si ya se activó hoy (para alarmas no repetitivas)
                    if not alarm['repeat_daily'] and alarm['triggered_today']:
                        continue
                        
                    # Trigger alarm / Activar alarma
                    self._trigger_alarm(alarm)
                    
                    if not alarm['repeat_daily']:
                        alarm['triggered_today'] = True
                        
            # Reset triggered_today flag at midnight / Reiniciar bandera triggered_today a medianoche
            if current_time['hour_24h'] == 0 and current_time['minute'] == 0 and current_time['second'] == 0:
                for alarm in self.alarms:
                    alarm['triggered_today'] = False
                    
            time.sleep(1)
            
    def _trigger_alarm(self, alarm):
        """Trigger specific alarm / Activar alarma específica"""
        print(f"🔔 ALARM: {alarm['description']} - {alarm['hour']:02d}:{alarm['minute']:02d}:{alarm['second']:02d}")
        
        if alarm['callback']:
            try:
                alarm['callback'](alarm)
            except Exception as e:
                print(f"Error executing alarm callback: {e}")


if __name__ == "__main__":
    # Clock tests / Pruebas del reloj
    print("=== Circular Clock Tests / Pruebas del Reloj Circular ===")
    
    # Create clock / Crear reloj
    clock = CircularClock()
    print(f"Initial time: {clock.format_time()} / Hora inicial: {clock.format_time()}")
    print(f"Date: {clock.format_date()} / Fecha: {clock.format_date()}")
    
    # Test format change / Probar cambio de formato
    print("\n--- Format Change / Cambio de Formato ---")
    clock.change_format(True)  # 24h
    print(f"24h format: {clock.format_time()} / Formato 24h: {clock.format_time()}")
    clock.change_format(False)  # 12h
    print(f"12h format: {clock.format_time()} / Formato 12h: {clock.format_time()}")
    
    # Test angles for analog clock / Probar ángulos para reloj analógico
    print("\n--- Angles for analog clock / Ángulos para reloj analógico ---")
    print(f"Seconds angle: {clock.get_seconds_angle()}° / Ángulo de segundos: {clock.get_seconds_angle()}°")
    print(f"Minutes angle: {clock.get_minutes_angle()}° / Ángulo de minutos: {clock.get_minutes_angle()}°")
    print(f"Hours angle: {clock.get_hours_angle()}° / Ángulo de horas: {clock.get_hours_angle()}°")
    
    # Test alarms / Probar alarmas
    print("\n--- Alarm system / Sistema de alarmas ---")
    alarm_manager = AlarmManager(clock)
    time_data = clock.get_current_time()
    
    # Add alarm in 5 seconds / Agregar alarma en 5 segundos
    alarm_id = alarm_manager.add_alarm(
        time_data['hour_24h'], 
        time_data['minute'], 
        (time_data['second'] + 5) % 60,
        "Test alarm"
    )
    
    print(f"Alarm created with ID: {alarm_id} / Alarma creada con ID: {alarm_id}")
    print("Current alarms:", alarm_manager.get_alarms())
    
    print("\nFunctional clock created successfully! ✅ / ¡Reloj funcional creado exitosamente! ✅")