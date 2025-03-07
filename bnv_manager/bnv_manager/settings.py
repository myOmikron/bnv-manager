"""
Django settings for bnv_manager project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
import ldap
from django_auth_ldap.config import GroupOfNamesType, LDAPSearch, LDAPSearchUnion
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'change_me'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
]

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1",
]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'generic',
    'superadministration',
    'clubadministration',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bnv_manager.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / "templates",
        ],
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

WSGI_APPLICATION = 'bnv_manager.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

LANGUAGES = [
  ('de', _('German')),
  ('en', _('English')),
]

LOCALE_PATHS = [
    BASE_DIR / "locale"
]

LANGUAGE_COOKIE_NAME = "django_language"
LANGUAGE_COOKIE_PATH = "/"

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = "/var/www/html/static/"

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"django_auth_ldap": {"level": "DEBUG", "handlers": ["console"]}},
}

LOGIN_URL = "/login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login"

# LDAP Configuration
AUTHENTICATION_BACKENDS = [
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_LDAP_SERVER_URI = ""

# Specify if self-signed TLS should be used without importing CA, comment out if not
ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

AUTH_LDAP_BIND_DN = "cn=admin,dc=example,dc=com"
AUTH_LDAP_BIND_PASSWORD = "change_me"

AUTH_LDAP_USER_BASE = "ou=Users,dc=example,dc=com"
AUTH_LDAP_ADMIN_BASE = "ou=AdminUsers,dc=example,dc=com"
AUTH_LDAP_CLUB_ADMIN_BASE = ""
AUTH_LDAP_USER_SEARCH = LDAPSearchUnion(
    LDAPSearch(AUTH_LDAP_ADMIN_BASE, ldap.SCOPE_SUBTREE, "(cn=%(user)s)"),
    LDAPSearch(AUTH_LDAP_CLUB_ADMIN_BASE, ldap.SCOPE_SUBTREE, "(cn=%(user)s)"),
    LDAPSearch(AUTH_LDAP_USER_BASE, ldap.SCOPE_SUBTREE, "(cn=%(user)s)"),
)

AUTH_LDAP_CACHE_TIMEOUT = 3600
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    "ou=Groups,dc=example,dc=com", ldap.SCOPE_SUBTREE, "(objectClass=groupOfNames)"
)
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="cn")

# Set both to admin group, grants access to Django database administration
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_staff": "cn=superadmins,ou=Groups,dc=example,dc=com",
    "is_superuser": "cn=superadmins,ou=Groups,dc=example,dc=com",
}

AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

LDAP_USER_DN = ""
LDAP_USER_FILTER = "objectClass=inetOrgPerson"

# Internal needed LDAP options
LDAP_GROUP_DN = "ou=Groups,dc=example,dc=com"
LDAP_GLOBAL_SEARCH_BASE = ""
LDAP_GROUP_FILTER = "objectClass=groupOfNames"

# Mailcow Configuration
MAILCOW_API_URI = ""
MAILCOW_API_KEY = ""
