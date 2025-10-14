"""
Implementación de Listas Doblemente Enlazadas Circulares para Reloj Moderno

"""

import datetime
import pytz


class Node:
    """Node for circular double linked list / Nodo para lista doblemente enlazada circular"""
    def __init__(self, value):
        self.value = value
        self.next = None
        self.previous = None
        
    def __str__(self):
        return str(self.value)


class CircularDoubleLinkedList:
    """Base class for circular double linked list / Clase base para lista doblemente enlazada circular"""
    def __init__(self):
        self.current = None  # Current node / Nodo actual
        self.size = 0  # List size / Tamaño de la lista
        
    def add(self, value):
        """Add element to circular list / Agregar elemento a la lista circular"""
        new_node = Node(value)
        
        if self.current is None:
            # First insertion / Primera inserción
            new_node.next = new_node
            new_node.previous = new_node
            self.current = new_node
        else:
            # Insert at end / Insertar al final
            last = self.current.previous
            new_node.next = self.current
            new_node.previous = last
            last.next = new_node
            self.current.previous = new_node
            
        self.size += 1
        
    def advance(self):
        """Move to next element / Mover al siguiente elemento"""
        if self.current:
            self.current = self.current.next
            
    def retreat(self):
        """Move to previous element / Mover al elemento anterior"""
        if self.current:
            self.current = self.current.previous
            
    def get_value(self):
        """Get current value / Obtener valor actual"""
        return self.current.value if self.current else None
        
    def set_value(self, value):
        """Set current node based on value / Establecer nodo actual basado en valor"""
        if self.current is None:
            return False
            
        initial_node = self.current
        while True:
            if self.current.value == value:
                return True
            self.advance()
            if self.current == initial_node:
                break
        return False
        
    def get_all_values(self):
        """Get all elements in the list / Obtener todos los elementos de la lista"""
        if self.current is None:
            return []
            
        values = []
        initial_node = self.current
        values.append(self.current.value)
        self.advance()
        
        while self.current != initial_node:
            values.append(self.current.value)
            self.advance()
            
        return values


class HoursList(CircularDoubleLinkedList):
    """Circular list for hours (1-12 or 0-23) / Lista circular para horas (1-12 o 0-23)"""
    def __init__(self, format_24h=False):
        super().__init__()
        self.format_24h = format_24h  # 24h format flag / Bandera de formato 24h
        
        if format_24h:
            for hour in range(24):
                self.add(hour)
        else:
            for hour in range(1, 13):
                self.add(hour)
                
    def get_12h_hour(self):
        """Get hour in 12h format / Obtener hora en formato 12h"""
        if self.format_24h:
            hour = self.get_value()
            if hour == 0:
                return 12
            elif hour > 12:
                return hour - 12
            else:
                return hour
        return self.get_value()
        
    def get_24h_hour(self):
        """Get hour in 24h format / Obtener hora en formato 24h"""
        return self.get_value()
        
    def is_am(self):
        """Check if it's AM (only for 24h format) / Verificar si es AM (solo para formato 24h)"""
        if self.format_24h:
            return self.get_value() < 12
        return True  # For 12h format, would need additional indicator / Para formato 12h, necesitaría indicador adicional


class MinutesList(CircularDoubleLinkedList):
    """Circular list for minutes (0-59) / Lista circular para minutos (0-59)"""
    def __init__(self):
        super().__init__()
        for minute in range(60):
            self.add(minute)


class SecondsList(CircularDoubleLinkedList):
    """Circular list for seconds (0-59) / Lista circular para segundos (0-59)"""
    def __init__(self):
        super().__init__()
        for second in range(60):
            self.add(second)


class DaysList(CircularDoubleLinkedList):
    """Circular list for days of the week / Lista circular para días de la semana"""
    def __init__(self):
        super().__init__()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in days:
            self.add(day)
            
    def get_day_number(self):
        """Get day number (0=Monday, 6=Sunday) / Obtener número del día (0=Lunes, 6=Domingo)"""
        days_map = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }
        return days_map.get(self.get_value(), 0)
        
    def set_day_number(self, day_number):
        """Set day by number (0=Monday, 6=Sunday) / Establecer día por número (0=Lunes, 6=Domingo)"""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        if 0 <= day_number <= 6:
            return self.set_value(days[day_number])
        return False

    def get_spanish_day(self):
        """Get day name in Spanish for UI / Obtener nombre del día en español para la interfaz"""
        spanish_days = {
            'Monday': 'Lunes',
            'Tuesday': 'Martes', 
            'Wednesday': 'Miércoles',
            'Thursday': 'Jueves',
            'Friday': 'Viernes',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        return spanish_days.get(self.get_value(), 'Lunes')


# Time manipulation utility functions / Funciones de utilidad para manipulación de tiempo
def get_colombia_time():
    """Get current Colombia time (UTC-5) / Obtener hora actual de Colombia (UTC-5)"""
    colombia_tz = pytz.timezone('America/Bogota')
    now = datetime.datetime.now(colombia_tz)
    
    return {
        'hour': now.hour,
        'minute': now.minute,
        'second': now.second,
        'weekday': now.weekday()  # 0=Monday, 6=Sunday / 0=Lunes, 6=Domingo
    }


def format_time_12h(hour, minute, second):
    """Format time in 12h format with AM/PM / Formatear tiempo en formato 12h con AM/PM"""
    am_pm = "AM" if hour < 12 else "PM"
    hour_12 = 12 if hour == 0 else (hour if hour <= 12 else hour - 12)
    return f"{hour_12:02d}:{minute:02d}:{second:02d} {am_pm}"


def format_time_24h(hour, minute, second):
    """Format time in 24h format / Formatear tiempo en formato 24h"""
    return f"{hour:02d}:{minute:02d}:{second:02d}"


def get_spanish_month_name(month_number):
    """Get Spanish month name for UI / Obtener nombre del mes en español para la interfaz"""
    months = [
        '', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
    ]
    return months[month_number] if 1 <= month_number <= 12 else 'enero'


if __name__ == "__main__":
    # Test circular double linked lists / Probar listas doblemente enlazadas circulares
    print("=== Circular Double Linked Lists Tests / Pruebas de Listas Doblemente Enlazadas Circulares ===")
    
    # Test hours list / Probar lista de horas
    print("\n--- Hours List (12h) / Lista de Horas (12h) ---")
    hours_12 = HoursList(format_24h=False)
    hours_12.set_value(6)
    print(f"Current hour: {hours_12.get_value()} / Hora actual: {hours_12.get_value()}")
    hours_12.advance()
    print(f"Next hour: {hours_12.get_value()} / Siguiente hora: {hours_12.get_value()}")
    
    # Test days list / Probar lista de días
    print("\n--- Days List / Lista de Días ---")
    days = DaysList()
    days.set_value('Friday')
    print(f"Current day: {days.get_value()} / Día actual: {days.get_value()}")
    print(f"Spanish day: {days.get_spanish_day()} / Día en español: {days.get_spanish_day()}")
    days.advance()
    print(f"Next day: {days.get_value()} / Siguiente día: {days.get_value()}")
    print(f"Spanish next day: {days.get_spanish_day()} / Siguiente día en español: {days.get_spanish_day()}")
    
    # Test Colombia time / Probar hora de Colombia
    print("\n--- Colombia Time / Hora de Colombia ---")
    colombia_time = get_colombia_time()
    print(f"Colombia time: {colombia_time} / Hora de Colombia: {colombia_time}")
    print(f"12h format: {format_time_12h(colombia_time['hour'], colombia_time['minute'], colombia_time['second'])} / Formato 12h: {format_time_12h(colombia_time['hour'], colombia_time['minute'], colombia_time['second'])}")
    print(f"24h format: {format_time_24h(colombia_time['hour'], colombia_time['minute'], colombia_time['second'])} / Formato 24h: {format_time_24h(colombia_time['hour'], colombia_time['minute'], colombia_time['second'])}")