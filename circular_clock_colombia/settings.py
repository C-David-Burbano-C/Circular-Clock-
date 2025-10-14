"""
Django settings for circular_clock_colombia project. / Configuraciones de Django para proyecto circular_clock_colombia.
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'. / Construir rutas dentro del proyecto como esta: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production / Configuraciones rápidas de desarrollo - no aptas para producción
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/ / Ver https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret! / ADVERTENCIA DE SEGURIDAD: mantener la clave secreta usada en producción secreta!
SECRET_KEY = "django-insecure-circular-clock-colombia-2025"

# SECURITY WARNING: don't run with debug turned on in production! / ADVERTENCIA DE SEGURIDAD: no ejecutar con debug activado en producción!
DEBUG = True

# Hosts allowed to serve this application / Hosts permitidos para servir esta aplicación
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Application definition / Definición de aplicación
INSTALLED_APPS = [
    "django.contrib.admin",  # Admin interface / Interfaz de admin
    "django.contrib.auth",  # Authentication system / Sistema de autenticación
    "django.contrib.contenttypes",  # Content types framework / Framework de tipos de contenido
    "django.contrib.sessions",  # Session framework / Framework de sesiones
    "django.contrib.messages",  # Messages framework / Framework de mensajes
    "django.contrib.staticfiles",  # Static files handling / Manejo de archivos estáticos
    "clock",  # Our clock app / Nuestra app del reloj
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",  # Security middleware / Middleware de seguridad
    "django.contrib.sessions.middleware.SessionMiddleware",  # Session middleware / Middleware de sesiones
    "django.middleware.common.CommonMiddleware",  # Common middleware / Middleware común
    "django.middleware.csrf.CsrfViewMiddleware",  # CSRF protection / Protección CSRF
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # Authentication middleware / Middleware de autenticación
    "django.contrib.messages.middleware.MessageMiddleware",  # Messages middleware / Middleware de mensajes
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # Clickjacking protection / Protección contra clickjacking
]

ROOT_URLCONF = "circular_clock_colombia.urls"  # Root URL configuration / Configuración de URL raíz

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",  # Template backend / Backend de plantillas
        "DIRS": [],  # Template directories / Directorios de plantillas
        "APP_DIRS": True,  # Look for templates in app directories / Buscar plantillas en directorios de apps
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",  # Debug context processor / Procesador de contexto de debug
                "django.template.context_processors.request",  # Request context processor / Procesador de contexto de request
                "django.contrib.auth.context_processors.auth",  # Auth context processor / Procesador de contexto de auth
                "django.contrib.messages.context_processors.messages",  # Messages context processor / Procesador de contexto de messages
            ],
        },
    },
]

WSGI_APPLICATION = "circular_clock_colombia.wsgi.application"  # WSGI application / Aplicación WSGI

# Database / Base de datos
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",  # SQLite database engine / Motor de base de datos SQLite
        "NAME": BASE_DIR / "db.sqlite3",  # Database file path / Ruta del archivo de base de datos
    }
}

# Internationalization / Internacionalización
# https://docs.djangoproject.com/en/5.2/topics/i18n/
LANGUAGE_CODE = "es-co"  # Language code for Colombia Spanish / Código de idioma para español de Colombia
TIME_ZONE = "America/Bogota"  # Time zone for Colombia / Zona horaria para Colombia
USE_I18N = True  # Enable internationalization / Habilitar internacionalización
USE_TZ = True  # Use timezone-aware datetimes / Usar datetimes conscientes de zona horaria

# Static files (CSS, JavaScript, Images) / Archivos estáticos (CSS, JavaScript, Imágenes)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = "/static/"  # URL for static files / URL para archivos estáticos

# Default primary key field type / Tipo de campo de clave primaria por defecto
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
