

import os
import environ
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = ['192.168.254.5', 'localhost', '127.0.0.1']
AUTH_USER_MODEL = 'Vegetable.User'  # 'app_name.model_name'


# Application definition

INSTALLED_APPS = [
    'Vegetable',
    'simpleui',
    'rest_framework',
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters'
]

SIMPLEUI_HOME_INFO = False  # Remove simpleui advertising
SIMPLEUI_ANALYSIS = False   # Disable analytics
SIMPLEUI_LOGO = '\media\logo.png'  # Your logo path

# settings.py (or development.py)
SIMPLEUI_CONFIG = {
    'system_keep': False,  # Use custom menu
    'dynamic': False,  # Set to False
    
    # Home page info card
    'home_title': 'Dashboard',
    'home_icon': 'fas fa-tachometer-alt',
    
    # Menu configuration
    'menus': [
        {
            'name': 'Users',
            'icon': 'fas fa-users',
            'url': 'Vegetable/user/'  # Correct URL format
        },
        {
            'name': 'Vegetables',
            'icon': 'fas fa-carrot',
            'url': 'Vegetable/veg/'  # Correct URL format
        },
        {
            'name': 'Daily Prices',
            'icon': 'fas fa-chart-line',
            'url': 'Vegetable/dailyprice/'  # Correct URL format
        },
        {
            'name': 'Orders',
            'icon': 'fas fa-shopping-cart',
            'url': 'Vegetable/order/'  # Correct URL format
        },
        {
            'name': 'VendorResponse',
            'icon': 'fa-solid fa-bullhorn',
            'url': 'Vegetable/vendorresponse/'  # Correct URL format
        },
        {
            'name': 'Notifications',
            'icon': 'fa-solid fa-bell',
            'url': 'Vegetable/notification/'  # Correct URL format
        },
       
    ]
}
# Customize Simple UI icons for your models
SIMPLEUI_ICON = {
    'User': 'fas fa-user',
    'Veg': 'fas fa-carrot',
    'Order': 'fas fa-shopping-cart',
    'DailyPrice': 'fas fa-chart-line',
    'Group': 'fas fa-users',
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'TarkariDeal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'TarkariDeal.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = '/static/'



MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

