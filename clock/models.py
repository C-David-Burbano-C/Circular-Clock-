

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class ClockConfiguration(models.Model):
    """Clock configuration settings / Configuraciones del reloj"""
    
    # Format options / Opciones de formato
    FORMAT_CHOICES = [
        ('12h', '12 Horas (AM/PM)'),
        ('24h', '24 Horas'),
    ]
    
    # Theme options / Opciones de tema
    THEME_CHOICES = [
        ('dark', 'Tema Oscuro'),
        ('light', 'Tema Claro'),
        ('blue', 'Tema Azul'),
        ('green', 'Tema Verde'),
    ]
    
    name = models.CharField(max_length=100, default="Configuración Principal", verbose_name="Nombre")
    time_format = models.CharField(max_length=3, choices=FORMAT_CHOICES, default='12h', verbose_name="Formato de Hora")
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='dark', verbose_name="Tema")
    show_seconds = models.BooleanField(default=True, verbose_name="Mostrar Segundos")
    show_analog_clock = models.BooleanField(default=True, verbose_name="Mostrar Reloj Analógico")
    show_digital_clock = models.BooleanField(default=True, verbose_name="Mostrar Reloj Digital")
    auto_sync = models.BooleanField(default=True, verbose_name="Sincronización Automática")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")
    
    class Meta:
        verbose_name = "Configuración del Reloj"
        verbose_name_plural = "Configuraciones del Reloj"
        
    def __str__(self):
        return f"{self.name} - {self.get_time_format_display()}"


class Alarm(models.Model):
    """Alarm model with circular list integration / Modelo de alarma con integración de listas circulares"""
    
    # Priority levels / Niveles de prioridad
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('normal', 'Normal'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    # Sound types / Tipos de sonido
    SOUND_CHOICES = [
        ('beep', 'Pitido Simple'),
        ('chime', 'Campanilla'),
        ('bell', 'Campana'),
        ('tone', 'Tono'),
        ('custom', 'Personalizado'),
    ]
    
    # Days of week for repeat / Días de la semana para repetir
    WEEKDAY_CHOICES = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    # AM/PM choices / Opciones AM/PM
    PERIOD_CHOICES = [
        ('AM', 'AM'),
        ('PM', 'PM'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    # Time settings using circular list values / Configuraciones de tiempo usando valores de listas circulares
    hour = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name="Hora"
    )
    minute = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(59)],
        verbose_name="Minuto"
    )
    period = models.CharField(
        max_length=2,
        choices=PERIOD_CHOICES,
        default='AM',
        verbose_name="Período"
    )
    day_of_week = models.IntegerField(
        choices=WEEKDAY_CHOICES,
        null=True,
        blank=True,
        verbose_name="Día de la Semana"
    )
    # Optional calendar date for one-off alarms / Fecha opcional del calendario para alarmas únicas
    alarm_date = models.DateField(null=True, blank=True, verbose_name="Fecha del Calendario")
    second = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(59)],
        default=0,
        verbose_name="Segundo"
    )
    
    # Alarm settings / Configuraciones de alarma
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    repeat_daily = models.BooleanField(default=False, verbose_name="Repetir Diariamente")
    repeat_weekdays = models.JSONField(default=list, blank=True, verbose_name="Días de Repetición")
    
    # Alarm properties / Propiedades de alarma
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal', verbose_name="Prioridad")
    sound_type = models.CharField(max_length=10, choices=SOUND_CHOICES, default='beep', verbose_name="Tipo de Sonido")
    volume = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=50,
        verbose_name="Volumen"
    )
    
    # Snooze settings / Configuraciones de snooze
    snooze_enabled = models.BooleanField(default=True, verbose_name="Snooze Habilitado")
    snooze_duration = models.IntegerField(default=5, verbose_name="Duración Snooze (minutos)")
    max_snooze_count = models.IntegerField(default=3, verbose_name="Máximo Snoozes")
    
    # Tracking / Seguimiento
    times_triggered = models.IntegerField(default=0, verbose_name="Veces Disparada")
    last_triggered = models.DateTimeField(null=True, blank=True, verbose_name="Última Vez Disparada")
    # Temporary silencing: if set to a future datetime, alarm will not trigger until then / Silenciamiento temporal: si se establece en una fecha futura, la alarma no se disparará hasta entonces
    silenced_until = models.DateTimeField(null=True, blank=True, verbose_name="Silenciada Hasta")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creada")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizada")
    
    class Meta:
        verbose_name = "Alarma"
        verbose_name_plural = "Alarmas"
        ordering = ['hour', 'minute']
        
    def __str__(self):
        return f"{self.title} - {self.hour:02d}:{self.minute:02d}"
    
    def get_time_display(self):
        """Get formatted time display / Obtener visualización de tiempo formateada"""
        return f"{self.hour:02d}:{self.minute:02d}:{self.second:02d}"
    
    def get_12h_time_display(self):
        """Get 12h formatted time display / Obtener visualización de tiempo formateada en 12h"""
        am_pm = "AM" if self.hour < 12 else "PM"
        hour_12 = 12 if self.hour == 0 else (self.hour if self.hour <= 12 else self.hour - 12)
        return f"{hour_12:02d}:{self.minute:02d}:{self.second:02d} {am_pm}"
    
    def is_time_to_trigger(self, current_hour, current_minute, current_second):
        """Check if it's time to trigger this alarm / Verificar si es hora de disparar esta alarma"""
        return (self.is_active and 
                self.hour == current_hour and 
                self.minute == current_minute and 
                self.second == current_second)
    
    def should_trigger_today(self, weekday):
        """Check if alarm should trigger today based on repeat settings / Verificar si la alarma debe dispararse hoy basado en configuraciones de repetición"""
        if self.repeat_daily:
            return True
        if self.repeat_weekdays and weekday in self.repeat_weekdays:
            return True
        return not self.repeat_daily and not self.repeat_weekdays
    
    def trigger(self):
        """Mark alarm as triggered / Marcar alarma como disparada"""
        self.times_triggered += 1
        self.last_triggered = timezone.now()
        self.save()


class AlarmLog(models.Model):
    """Log of alarm triggers / Registro de disparos de alarmas"""
    
    STATUS_CHOICES = [
        ('triggered', 'Disparada'),
        ('snoozed', 'Pospuesta'),
        ('dismissed', 'Descartada'),
        ('missed', 'Perdida'),
    ]
    
    # Keep a nullable FK so logs survive alarm deletion, and store a denormalized title / Mantener FK nullable para que los logs sobrevivan a la eliminación de alarmas, y almacenar un título desnormalizado
    alarm = models.ForeignKey(Alarm, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs', verbose_name="Alarma")
    alarm_title = models.CharField(max_length=200, blank=True, verbose_name="Título de la Alarma")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name="Estado")
    triggered_at = models.DateTimeField(auto_now_add=True, verbose_name="Disparada En")
    user_action = models.CharField(max_length=100, blank=True, verbose_name="Acción del Usuario")
    response_time = models.DurationField(null=True, blank=True, verbose_name="Tiempo de Respuesta")
    
    class Meta:
        verbose_name = "Registro de Alarma"
        verbose_name_plural = "Registros de Alarmas"
        ordering = ['-triggered_at']
        
    def __str__(self):
        return f"{self.alarm.title} - {self.get_status_display()} - {self.triggered_at}"


class CircularListState(models.Model):
    """State of circular lists (for persistence) / Estado de listas circulares (para persistencia)"""
    
    LIST_TYPES = [
        ('hours_24', 'Horas 24h'),
        ('hours_12', 'Horas 12h'),
        ('minutes', 'Minutos'),
        ('seconds', 'Segundos'),
        ('days', 'Días'),
    ]
    
    list_type = models.CharField(max_length=10, choices=LIST_TYPES, unique=True, verbose_name="Tipo de Lista")
    current_value = models.IntegerField(verbose_name="Valor Actual")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Estado de Lista Circular"
        verbose_name_plural = "Estados de Listas Circulares"
        
    def __str__(self):
        return f"{self.get_list_type_display()}: {self.current_value}"


class ClockStatistics(models.Model):
    """Clock usage statistics / Estadísticas de uso del reloj"""
    
    date = models.DateField(unique=True, verbose_name="Fecha")
    total_runtime_minutes = models.IntegerField(default=0, verbose_name="Tiempo Total Ejecutándose (minutos)")
    alarms_triggered = models.IntegerField(default=0, verbose_name="Alarmas Disparadas")
    format_changes = models.IntegerField(default=0, verbose_name="Cambios de Formato")
    sync_operations = models.IntegerField(default=0, verbose_name="Sincronizaciones")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    
    class Meta:
        verbose_name = "Estadística del Reloj"
        verbose_name_plural = "Estadísticas del Reloj"
        ordering = ['-date']
        
    def __str__(self):
        return f"Estadísticas {self.date}"
